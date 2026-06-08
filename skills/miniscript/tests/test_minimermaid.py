from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from minimermaid import PolicyError, mermaid_to_html, miniscript_to_mermaid, parse_policy, simplify_policy


def test_parse_rejects_extra_closing_parenthesis() -> None:
    with pytest.raises(PolicyError, match="Unexpected trailing characters"):
        parse_policy("or(pk(A),pk(B)))")


def test_parse_rejects_invalid_or_arity() -> None:
    with pytest.raises(PolicyError, match="expects exactly two subpolicies"):
        parse_policy("or(pk(A),pk(B),pk(C))")


def test_simplify_preserves_case_and_valid_policy_syntax() -> None:
    simplified = simplify_policy("or(and(pk(A),pk(B)),or(and(pk(A),pk(C)),and(pk(B),pk(C))))")

    assert "pk(A)" in simplified
    assert "pk(B)" in simplified
    assert "pk(C)" in simplified
    assert simplified.startswith("thresh(1,")
    parse_policy(simplified)


def test_simplified_mermaid_keeps_original_key_names() -> None:
    mermaid = miniscript_to_mermaid("or(and(pk(A),pk(B)),and(pk(A),pk(C)))", simp=True)

    assert 'A -->|pk|' in mermaid
    assert 'B -->|pk|' in mermaid
    assert 'C -->|pk|' in mermaid
    assert "a -->|pk|" not in mermaid
    assert "spend((spend))" in mermaid


def test_mermaid_html_wraps_graph() -> None:
    html_page = mermaid_to_html("graph TD\nA --> B", title="Demo")

    assert "<!doctype html>" in html_page
    assert "class=\"mermaid\"" in html_page
    assert "Demo" in html_page


def test_cli_writes_preview_html(tmp_path: Path) -> None:
    html_path = tmp_path / "preview.html"

    completed = subprocess.run(
        [
            sys.executable,
            "scripts/minimermaid.py",
            "and(pk(A),or(pk(B),older(144)))",
            "--html",
            str(html_path),
        ],
        check=False,
        capture_output=True,
        text=True,
        cwd=Path(__file__).resolve().parent.parent,
    )

    assert completed.returncode == 0
    assert "graph TD" in completed.stdout
    assert html_path.exists()
    assert "class=\"mermaid\"" in html_path.read_text(encoding="utf-8")
