from __future__ import annotations

import argparse
import html
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

from sympy import And, Or, Symbol, simplify_logic

VALID_FUNCTIONS = {
    "pk",
    "after",
    "older",
    "sha256",
    "hash256",
    "ripemd160",
    "hash160",
    "and",
    "or",
    "thresh",
}
HASH_LENGTHS = {"sha256": 64, "hash256": 64, "ripemd160": 40, "hash160": 40}


class PolicyError(ValueError):
    """Raised when a policy cannot be parsed or validated."""


@dataclass(frozen=True)
class LeafNode:
    kind: str
    value: str | int


@dataclass(frozen=True)
class ThresholdNode:
    threshold: int
    children: tuple["PolicyNode", ...]
    source: str = "thresh"


PolicyNode = LeafNode | ThresholdNode


def parse_policy(policy: str) -> PolicyNode:
    return _parse_expr(policy.strip())


def _parse_expr(expr: str) -> PolicyNode:
    expr = expr.strip()
    if not expr:
        raise PolicyError("Policy expression is empty")
    open_index = expr.find("(")
    if open_index == -1 or not expr.endswith(")"):
        raise PolicyError(f"Invalid expression: {expr}")
    function_name = expr[:open_index].strip().lower()
    if function_name not in VALID_FUNCTIONS:
        raise PolicyError(f"Invalid function: {function_name}")
    inner = _strip_outer_call(expr)
    args = _split_args(inner)
    return _build_node(function_name, args)


def _strip_outer_call(expr: str) -> str:
    depth = 0
    open_index = expr.find("(")
    for index, char in enumerate(expr[open_index:], start=open_index):
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth < 0:
                raise PolicyError("Unexpected closing parenthesis")
            if depth == 0:
                if index != len(expr) - 1:
                    raise PolicyError(f"Unexpected trailing characters: {expr[index + 1:]}")
                return expr[open_index + 1:index]
    raise PolicyError("Missing closing parenthesis")


def _split_args(args: str) -> list[str]:
    if not args.strip():
        return []
    parts: list[str] = []
    current: list[str] = []
    depth = 0
    for char in args:
        if char == "," and depth == 0:
            part = "".join(current).strip()
            if not part:
                raise PolicyError("Empty argument")
            parts.append(part)
            current = []
            continue
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth < 0:
                raise PolicyError("Unexpected closing parenthesis")
        current.append(char)
    if depth != 0:
        raise PolicyError("Missing closing parenthesis")
    part = "".join(current).strip()
    if not part:
        raise PolicyError("Empty argument")
    parts.append(part)
    return parts


def _build_node(function_name: str, args: list[str]) -> PolicyNode:
    if function_name == "pk":
        if len(args) != 1 or not args[0]:
            raise PolicyError("pk() expects exactly one key name")
        return LeafNode(function_name, args[0])

    if function_name in HASH_LENGTHS:
        if len(args) != 1:
            raise PolicyError(f"{function_name}() expects exactly one hash")
        value = args[0]
        if value != "H" and len(value) != HASH_LENGTHS[function_name]:
            raise PolicyError(f"Invalid argument for {function_name}: {value}")
        return LeafNode(function_name, value)

    if function_name in {"after", "older"}:
        if len(args) != 1:
            raise PolicyError(f"{function_name}() expects exactly one timelock value")
        try:
            value = int(args[0])
        except ValueError as exc:
            raise PolicyError(f"Invalid argument for {function_name}: {args[0]}") from exc
        if value <= 0:
            raise PolicyError(f"Invalid argument for {function_name}: {args[0]}")
        return LeafNode(function_name, value)

    if function_name in {"and", "or"}:
        if len(args) != 2:
            raise PolicyError(f"{function_name}() expects exactly two subpolicies")
        children = tuple(_parse_expr(arg) for arg in args)
        threshold = 2 if function_name == "and" else 1
        return ThresholdNode(threshold, children, source=function_name)

    if function_name == "thresh":
        if len(args) < 2:
            raise PolicyError("thresh() expects a threshold and at least one subpolicy")
        try:
            threshold = int(args[0])
        except ValueError as exc:
            raise PolicyError(f"Invalid threshold value: {args[0]}") from exc
        children = tuple(_parse_expr(arg) for arg in args[1:])
        if threshold < 1 or threshold > len(children):
            raise PolicyError(f"Invalid threshold value: {threshold}")
        return ThresholdNode(threshold, children)

    raise PolicyError(f"Unsupported function: {function_name}")


def policy_to_string(node: PolicyNode, preserve_source: bool = False) -> str:
    if isinstance(node, LeafNode):
        return f"{node.kind}({node.value})"

    if preserve_source and node.source in {"and", "or"} and len(node.children) == 2:
        joined = ", ".join(policy_to_string(child, preserve_source=True) for child in node.children)
        return f"{node.source}({joined})"

    if node.threshold == 1 and len(node.children) == 2:
        joined = ", ".join(policy_to_string(child) for child in node.children)
        return f"or({joined})"

    if node.threshold == len(node.children) and len(node.children) == 2:
        joined = ", ".join(policy_to_string(child) for child in node.children)
        return f"and({joined})"

    joined = ", ".join(policy_to_string(child) for child in node.children)
    return f"thresh({node.threshold}, {joined})"


def simplify_policy(policy: str) -> str:
    simplified = simplify_node(parse_policy(policy))
    return policy_to_string(simplified)


def simplify_node(node: PolicyNode) -> PolicyNode:
    symbol_map: Dict[str, PolicyNode] = {}
    expr = _node_to_sympy(node, symbol_map)
    simplified_expr = simplify_logic(expr, force=True)
    simplified = _sympy_to_node(simplified_expr, symbol_map)
    return _flatten_thresholds(simplified)


def _node_to_sympy(node: PolicyNode, symbol_map: Dict[str, PolicyNode]) -> Symbol | And | Or:
    if isinstance(node, LeafNode):
        symbol_name = f"leaf_{len(symbol_map)}"
        symbol_map[symbol_name] = node
        return Symbol(symbol_name)

    if node.threshold == 1:
        return Or(*(_node_to_sympy(child, symbol_map) for child in node.children))
    if node.threshold == len(node.children):
        return And(*(_node_to_sympy(child, symbol_map) for child in node.children))

    symbol_name = f"threshold_{len(symbol_map)}"
    symbol_map[symbol_name] = node
    return Symbol(symbol_name)


def _sympy_to_node(expr, symbol_map: Dict[str, PolicyNode]) -> PolicyNode:
    if isinstance(expr, Symbol):
        return symbol_map[str(expr)]
    if expr.func is And:
        children = tuple(_sympy_to_node(arg, symbol_map) for arg in expr.args)
        return ThresholdNode(len(children), children)
    if expr.func is Or:
        children = tuple(_sympy_to_node(arg, symbol_map) for arg in expr.args)
        return ThresholdNode(1, children)
    raise PolicyError(f"Unsupported simplified expression: {expr}")


def _flatten_thresholds(node: PolicyNode) -> PolicyNode:
    if isinstance(node, LeafNode):
        return node

    flattened_children = tuple(_flatten_thresholds(child) for child in node.children)
    merged_children: list[PolicyNode] = []
    for child in flattened_children:
        if (
            isinstance(child, ThresholdNode)
            and child.threshold == node.threshold
            and (
                child.threshold == 1
                or child.threshold == len(child.children)
            )
        ):
            merged_children.extend(child.children)
        else:
            merged_children.append(child)
    return ThresholdNode(node.threshold, tuple(merged_children), source=node.source)


def miniscript_to_mermaid(miniscript: str, simp: bool = True) -> str:
    node = parse_policy(miniscript)
    if simp:
        node = simplify_node(node)
    builder = MermaidBuilder()
    builder.render(node)
    return builder.to_string()


def mermaid_to_html(mermaid_code: str, title: str = "Miniscript Flowchart") -> str:
    escaped_title = html.escape(title)
    escaped_mermaid = html.escape(mermaid_code)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escaped_title}</title>
  <style>
    :root {{
      color-scheme: dark;
      font-family: "Iowan Old Style", "Palatino Linotype", serif;
      background:
        radial-gradient(circle at top, rgba(182, 148, 63, 0.2), transparent 35%),
        linear-gradient(180deg, #17130d 0%, #0e0b08 100%);
      color: #f3ead7;
    }}
    body {{
      margin: 0;
      min-height: 100vh;
      display: grid;
      place-items: center;
      padding: 2rem;
    }}
    main {{
      width: min(1100px, 100%);
      border: 1px solid rgba(243, 234, 215, 0.18);
      background: rgba(17, 13, 10, 0.88);
      box-shadow: 0 32px 80px rgba(0, 0, 0, 0.35);
      border-radius: 24px;
      padding: 2rem;
      backdrop-filter: blur(18px);
    }}
    h1 {{
      margin-top: 0;
      font-size: clamp(1.8rem, 4vw, 2.8rem);
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }}
    pre {{
      overflow-x: auto;
      padding: 1rem;
      border-radius: 16px;
      background: rgba(255, 255, 255, 0.04);
    }}
  </style>
  <script type="module">
    import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
    mermaid.initialize({{ startOnLoad: true, theme: "dark" }});
  </script>
</head>
<body>
  <main>
    <h1>{escaped_title}</h1>
    <pre class="mermaid">{escaped_mermaid}</pre>
  </main>
</body>
</html>
"""


class MermaidBuilder:
    def __init__(self) -> None:
        self.lines = ["graph TD"]
        self.counter = 0

    def render(self, node: PolicyNode) -> None:
        root_id = self._render_node(node, None)
        self.lines.append(f"{root_id} -->|yes| spend((spend))")
        self.lines.append(f"{root_id} -->|no| reject((nothing))")

    def _render_node(self, node: PolicyNode, parent_id: str | None) -> str:
        if isinstance(node, LeafNode):
            if parent_id is None:
                node_id = self._next_id("thresh")
                self.lines.append(f'{node_id}{{"Check 1/1"}}')
                self.lines.append(f'{self._label(node.value)} -->|{node.kind}| {node_id}')
                return node_id
            self.lines.append(f'{self._label(node.value)} -->|{node.kind}| {parent_id}')
            return parent_id

        prefix = node.source if node.source in {"and", "or"} else "thresh"
        node_id = self._next_id(prefix)
        for child in node.children:
            self._render_node(child, node_id)
        self.lines.append(f'{node_id}{{"Check {node.threshold}/{len(node.children)}"}}')
        if parent_id is not None:
            self.lines.append(f"{node_id} --> {parent_id}")
        return node_id

    def _next_id(self, prefix: str) -> str:
        node_id = f"{prefix}_{self.counter}"
        self.counter += 1
        return node_id

    @staticmethod
    def _label(value: str | int) -> str:
        return str(value).replace('"', '\\"')

    def to_string(self) -> str:
        return "\n".join(self.lines)


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Render Miniscript policies as Mermaid flowcharts.")
    parser.add_argument("policy", help="Miniscript policy expression to render.")
    parser.add_argument(
        "--audit",
        action="store_true",
        help="Keep the original structure instead of simplifying equivalent boolean expressions.",
    )
    parser.add_argument(
        "--html",
        type=Path,
        help="Write a self-contained Mermaid preview HTML file to this path.",
    )
    return parser


def main() -> int:
    args = _build_arg_parser().parse_args()
    mermaid_code = miniscript_to_mermaid(args.policy, simp=not args.audit)
    print(mermaid_code)
    if args.html:
        args.html.write_text(mermaid_to_html(mermaid_code, args.policy), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
