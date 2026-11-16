from __future__ import annotations

import json
import os
import re
import stat
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "skills" / "nostr-vpn"
PAGES = ["SKILL.md", "references/commands.md", "references/onboarding.md"]


def bash_blocks(text):
    return re.findall(r"```bash\n(.*?)\n```", text, re.S)


def command_recipes():
    # Discovery/install instructions are not identity/runtime command recipes.
    # Every remaining Bash block in these pages that invokes $NVPN is executed
    # against an argv-only fixture, including its real shell quoting/control flow.
    for page in PAGES:
        for index, block in enumerate(bash_blocks((SKILL / page).read_text())):
            if '\"$NVPN\"' in block and "cargo install" not in block:
                yield pytest.param(page, block, id=f"{page}:{index}")


@pytest.fixture
def fixture_cli(tmp_path):
    bindir = tmp_path / "fixture bin"
    bindir.mkdir()
    config = tmp_path / "identity with spaces" / "network.toml"
    config.parent.mkdir(mode=0o700)
    config.write_text(json.dumps({"identity_id": "fixture-intended-identity"}))
    config.chmod(0o600)
    trace = tmp_path / "argv.jsonl"
    client = bindir / "nvpn"
    client.write_text(f"#!{sys.executable}\n" + r'''
import json, os, pathlib, sys
args = sys.argv[1:]
headless = os.environ.get("NVPN_TEST_HEADLESS", "new") == "new"
if "--help" in args:
    if args[0] == "join-requests" and not headless:
        print("unsupported fixture command", file=sys.stderr)
        sys.exit(2)
    print("usage: " + args[0] + (" [--json]" if headless else ""))
    sys.exit(0)
if args and args[0] == "version":
    print(json.dumps({"version": "fixture-only"}))
    sys.exit(0)
if args and args[0] == "--config":
    print("--config belongs to the subcommand", file=sys.stderr)
    sys.exit(23)
context_commands = {"init", "join-request", "join-manual", "join-requests", "start", "stop", "pause", "resume", "status", "doctor", "ip", "whois", "ping", "set", "add-device", "remove-device", "add-admin", "remove-admin", "connect", "reload", "repair-network", "service"}
contextual = bool(args and args[0] in context_commands)
config = None
identity = None
if contextual:
    if "--config" not in args:
        print("fixture requires an explicit config", file=sys.stderr)
        sys.exit(23)
    if args[0] == "service" and args.index("--config") < 2:
        print("service --config belongs after its action", file=sys.stderr)
        sys.exit(23)
    config = args[args.index("--config") + 1]
    if not pathlib.Path(config).is_absolute():
        print("fixture requires an absolute config", file=sys.stderr)
        sys.exit(23)
    identity = json.loads(pathlib.Path(config).read_text())["identity_id"]
if args and args[0] == "join-request" and "--json" in args and not headless:
    print("unsupported fixture flag", file=sys.stderr)
    sys.exit(2)
row = {"argv": args, "role": os.environ.get("NVPN_TEST_ROLE", "user"), "config": config, "identity_id": identity}
with open(os.environ["NVPN_TEST_TRACE"], "a") as output:
    output.write(json.dumps(row) + "\n")
if args and args[0] == "status":
    print(os.environ.get("NVPN_TEST_STATUS", '{"status_source":"daemon","mesh_ready":true}'))
else:
    print(json.dumps({"fixture_only": True, "identity_id": identity}))
''')
    client.chmod(0o755)
    elevation = bindir / "sudo"
    elevation.write_text(f"#!{sys.executable}\n" + '''
import os, sys
assert sys.argv[1] == os.environ["NVPN"], "Only the fixture executable may be elevated"
os.environ["NVPN_TEST_ROLE"] = "elevated-fixture"
os.execv(sys.argv[1], sys.argv[1:])
''')
    elevation.chmod(0o755)
    env = dict(os.environ)
    env.update(NVPN=str(client), NVPN_CONFIG=str(config), NVPN_TEST_TRACE=str(trace), PATH=str(bindir) + os.pathsep + os.environ["PATH"])
    return config, trace, env


def execute(block, env):
    return subprocess.run(["bash", "-eu", "-o", "pipefail", "-c", block], env=env, text=True, capture_output=True, timeout=10)


def read_trace(path):
    return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []


@pytest.mark.parametrize("page,block", list(command_recipes()))
def test_every_documented_identity_recipe_keeps_the_same_absolute_config(page, block, fixture_cli):
    config, trace, env = fixture_cli
    original = config.read_bytes()
    result = execute(block, env)
    assert result.returncode == 0, f"{page}: {result.stderr}\n{result.stdout}"
    rows = read_trace(trace)
    for row in rows:
        if row["config"] is not None:
            assert row["config"] == str(config)
            assert row["identity_id"] == "fixture-intended-identity"
    assert config.read_bytes() == original
    assert stat.S_IMODE(config.stat().st_mode) == 0o600


def section_block(title):
    text = (SKILL / "references/commands.md").read_text().split(f"## {title}", 1)[1].split("\n## ", 1)[0]
    return bash_blocks(text)


def test_service_elevation_keeps_the_user_selected_identity(fixture_cli):
    config, trace, env = fixture_cli
    result = execute(section_block("Persistent service")[0], env)
    assert result.returncode == 0, result.stderr
    rows = read_trace(trace)
    assert {row["role"] for row in rows} == {"user", "elevated-fixture"}
    assert all(row["config"] == str(config) for row in rows)
    assert all(row["identity_id"] == "fixture-intended-identity" for row in rows)


def test_missing_service_config_stops_before_any_install_or_key_creation(fixture_cli):
    config, trace, env = fixture_cli
    config.unlink()
    result = execute(section_block("Persistent service")[0], env)
    assert result.returncode == 1
    assert read_trace(trace) == []
    assert not config.exists()


@pytest.mark.parametrize("selection", ["", "relative/config.toml"])
def test_config_selection_guard_rejects_unknown_or_relative_paths(fixture_cli, selection):
    _, trace, env = fixture_cli
    env["NVPN_CONFIG"] = selection
    blocks = bash_blocks((SKILL / "references/onboarding.md").read_text())
    guard = next(block for block in blocks if 'case "${NVPN_CONFIG:-}"' in block)
    result = execute(guard, env)
    assert result.returncode == 2
    assert read_trace(trace) == []


@pytest.mark.parametrize("payload,code,message", [
    ({"status_source": "daemon", "mesh_ready": True}, 0, "ready"),
    ({"status_source": "daemon", "mesh_ready": False}, 1, "not ready"),
    ({"status_source": "config", "mesh_ready": None}, 2, "unknown"),
    ({"status_source": "config", "mesh_ready": True}, 2, "unknown"),
    ({"mesh_ready": True}, 2, "unknown"),
    ({"status_source": "daemon"}, 2, "unknown"),
    ({"status_source": "daemon", "mesh_ready": "true"}, 2, "unknown"),
])
def test_documented_readiness_check_uses_live_daemon_boolean_only(fixture_cli, payload, code, message):
    _, _, env = fixture_cli
    env["NVPN_TEST_STATUS"] = json.dumps(payload)
    result = execute(section_block("Interpret runtime readiness")[0], env)
    assert result.returncode == code, result.stderr
    assert result.stdout.strip().startswith(message)


@pytest.mark.parametrize("capability", ["old", "new"])
def test_headless_request_is_gated_and_uses_interactive_link_fallback(fixture_cli, capability):
    _, trace, env = fixture_cli
    env["NVPN_TEST_HEADLESS"] = capability
    result = execute(section_block("Headless join capabilities")[0], env)
    assert result.returncode == 0, result.stderr
    args = read_trace(trace)[0]["argv"]
    assert ("--json" in args) is (capability == "new")
    assert ("--no-wait" in args) is (capability == "old")


@pytest.mark.parametrize("capability", ["old", "new"])
def test_admin_headless_inspection_never_approves_a_request(fixture_cli, capability):
    _, trace, env = fixture_cli
    env["NVPN_TEST_HEADLESS"] = capability
    result = execute(section_block("Headless join capabilities")[1], env)
    assert result.returncode == 0, result.stderr
    rows = read_trace(trace)
    assert not any("approve" in row["argv"] for row in rows)
    if capability == "old":
        assert rows == []
        assert "admin app" in result.stdout
    else:
        assert rows[0]["argv"][:2] == ["join-requests", "list"]


@pytest.mark.parametrize("payload", ["not-json", "[]", "null"])
def test_invalid_status_payload_is_unknown_not_not_ready(fixture_cli, payload):
    _, _, env = fixture_cli
    env["NVPN_TEST_STATUS"] = payload
    result = execute(section_block("Interpret runtime readiness")[0], env)
    assert result.returncode == 2
    assert result.stdout.strip() == "unknown: invalid status JSON"
