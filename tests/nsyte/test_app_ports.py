import importlib.util
import json
from pathlib import Path
import subprocess
import sys

script = Path(__file__).resolve().parents[2] / "skills/nsyte-static-sites/scripts/validate_app_ports.py"
spec = importlib.util.spec_from_file_location("app_ports", script)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_build_endpoint_checks(tmp_path):
    (tmp_path / "index.html").write_text('<script src="app.js"></script>')
    app = tmp_path / "app.js"
    assert module.validate(tmp_path, no_relay=True)["ok"]
    assert not module.validate(tmp_path)["ok"]
    app.write_text('new WebSocket("ws://localhost:4870");')
    assert module.validate(tmp_path)["ok"]
    assert not module.validate(tmp_path, blossom=True)["ok"]
    app.write_text('new WebSocket("wss://relay.example:4870"); fetch("https://blob.example:24243/x");')
    assert module.validate(tmp_path, blossom=True)["ok"]
    app.write_text(app.read_text() + 'new WebSocket("wss://other.example:443");')
    assert not module.validate(tmp_path)["ok"]
    assert not module.validate(tmp_path, no_relay=True)["ok"]
    app.write_text('const port = 4870; new WebSocket(host + port);')
    assert not module.validate(tmp_path)["ok"]
    app.write_text(r'const url = "ws:\/\/localhost:4870";')
    assert module.validate(tmp_path)["ok"]
    app.write_text('new WebSocket("ws://localhost:99999");')
    assert not module.validate(tmp_path)["ok"]


def test_cli_explains_blossom_port_failure_without_leaking_url(tmp_path):
    (tmp_path / "index.html").write_text('<script src="app.js"></script>')
    (tmp_path / "app.js").write_text('fetch("https://user:secret@blob.example/private?token=hidden");')
    run = subprocess.run([sys.executable, str(script), str(tmp_path), "--no-relay", "--blossom"],
                         capture_output=True, text=True)
    assert run.returncode == 1
    result = json.loads(run.stdout)
    assert not result["ok"]
    assert "app.js:1 (port 443)" in result["errors"][0]
    assert "24243" in result["errors"][0] and "Keep --blossom" in result["errors"][0]
    assert result["next_action"].startswith("STOP: do not deploy.")
    assert all(secret not in run.stdout for secret in ("user", "secret", "blob.example", "private", "hidden"))
