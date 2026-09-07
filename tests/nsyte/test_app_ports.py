import importlib.util
from pathlib import Path

script = Path(__file__).resolve().parents[2] / "skills/nsyte-static-sites/scripts/validate_app_ports.py"
spec = importlib.util.spec_from_file_location("app_ports", script)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_build_endpoint_checks(tmp_path):
    (tmp_path / "index.html").write_text('<script src="app.js"></script>')
    app = tmp_path / "app.js"
    app.write_text('new WebSocket("ws://localhost:4870");')
    assert module.validate(tmp_path)["ok"]
    assert not module.validate(tmp_path, blossom=True)["ok"]
    app.write_text('new WebSocket("wss://relay.example:4870"); fetch("https://blob.example:24243/x");')
    assert module.validate(tmp_path, blossom=True)["ok"]
    app.write_text(app.read_text() + 'new WebSocket("wss://other.example:443");')
    assert not module.validate(tmp_path)["ok"]
    app.write_text('const port = 4870; new WebSocket(host + port);')
    assert not module.validate(tmp_path)["ok"]
    app.write_text(r'const url = "ws:\/\/localhost:4870";')
    assert module.validate(tmp_path)["ok"]
    app.write_text('new WebSocket("ws://localhost:99999");')
    assert not module.validate(tmp_path)["ok"]
