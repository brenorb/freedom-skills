from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).with_name("fixtures")
ACCOUNTS = json.loads((FIXTURES / "accounts.json").read_text())
CONTACTS = json.loads((FIXTURES / "contacts.json").read_text())


def load_helper(name):
    path = ROOT / "skills" / "signal-cli" / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SEND = load_helper("send_message")
FIND = load_helper("find_contact")


@pytest.fixture
def cli(monkeypatch):
    """Every command is intercepted; no installed Signal CLI is ever executed."""
    calls = []
    state = {"contacts": CONTACTS, "error": None}

    def run(command):
        calls.append(command)
        if state["error"]:
            raise RuntimeError(state["error"])
        if command[-1] == "listContacts":
            return json.dumps(state["contacts"])
        assert "send" in command, command
        return ""

    monkeypatch.setattr(SEND, "run", run)
    monkeypatch.setattr(FIND, "run", run)
    return calls, state


def invoke_send(monkeypatch, account, recipient, extra=()):
    monkeypatch.setattr(sys, "argv", ["send_message.py", "--account", account, "--to", recipient, "--text", "fixture text", *extra])
    return SEND.main()


def test_named_numberless_contact_uses_saved_uuid(cli):
    calls, _ = cli
    identifier, candidates = SEND.resolve_number(ACCOUNTS[1]["aci"], "Fixture Bob")
    assert identifier == CONTACTS[1]["uuid"]
    assert candidates == []
    assert calls == [["signal-cli", "-o", "json", "--account", ACCOUNTS[1]["aci"], "listContacts"]]


@pytest.mark.parametrize("account", [ACCOUNTS[0]["number"], ACCOUNTS[0]["aci"], ACCOUNTS[1]["aci"], ACCOUNTS[1]["aci"].replace("-", "")])
def test_selected_phone_or_aci_account_is_preserved_in_lookup_and_send(cli, monkeypatch, capsys, account):
    calls, _ = cli
    assert invoke_send(monkeypatch, account, "Fixture Bob") == 0
    result = json.loads(capsys.readouterr().out)
    assert result == {"ok": True, "account": account, "to": CONTACTS[1]["uuid"]}
    assert len(calls) == 2
    assert all(command[command.index("--account") + 1] == account for command in calls)
    assert calls[-1] == ["signal-cli", "--account", account, "send", CONTACTS[1]["uuid"], "-m", "fixture text"]


@pytest.mark.parametrize("identifier", [CONTACTS[0]["number"], CONTACTS[1]["uuid"], CONTACTS[1]["uuid"].upper()])
def test_explicit_identifier_is_passed_exactly_without_contact_guessing(cli, monkeypatch, capsys, identifier):
    calls, _ = cli
    assert invoke_send(monkeypatch, ACCOUNTS[1]["aci"], identifier) == 0
    assert len(calls) == 1
    assert calls[0][3:5] == ["send", identifier]
    assert json.loads(capsys.readouterr().out)["to"] == identifier


def test_existing_phone_contact_and_attachments_keep_their_command_contract(cli, monkeypatch, tmp_path, capsys):
    calls, _ = cli
    attachment = tmp_path / "fixture attachment.txt"
    attachment.write_text("fixture")
    assert invoke_send(monkeypatch, ACCOUNTS[0]["number"], "Fixture Alice", ["--attachment", str(attachment)]) == 0
    capsys.readouterr()
    assert calls[-1] == ["signal-cli", "--account", ACCOUNTS[0]["number"], "send", CONTACTS[0]["number"], "-m", "fixture text", "-a", str(attachment)]


def test_phone_and_numberless_contacts_both_participate_in_ambiguity(cli, monkeypatch, capsys):
    calls, state = cli
    state["contacts"] = [{**CONTACTS[0], "name": "Fixture Alex"}, {**CONTACTS[1], "name": "Fixture Alex"}]
    assert invoke_send(monkeypatch, ACCOUNTS[1]["aci"], "Fixture Alex") == 3
    result = json.loads(capsys.readouterr().out)
    assert result["error"] == "ambiguous_recipient"
    assert {row["uuid"] for row in result["candidates"]} == {CONTACTS[0]["uuid"], CONTACTS[1]["uuid"]}
    assert not any("send" in command for command in calls)


def test_unroutable_exact_match_does_not_fall_through_to_weaker_contact(cli, monkeypatch):
    calls, state = cli
    state["contacts"] = [{"name": "Fixture Charlie", "number": None, "uuid": None}, {**CONTACTS[0], "name": "Fixture Charlie Other"}]
    with pytest.raises(RuntimeError, match="no usable E.164 number or ACI UUID"):
        invoke_send(monkeypatch, ACCOUNTS[0]["number"], "Fixture Charlie")
    assert not any("send" in command for command in calls)


@pytest.mark.parametrize("identifier", ["2222aaaa", "2222aaaa-3333", "3333-4bbb-8ccc", "PNI:" + CONTACTS[1]["uuid"], "ACI:" + CONTACTS[1]["uuid"]])
def test_uuid_fragments_and_other_identifier_forms_never_guess_a_recipient(cli, monkeypatch, identifier):
    calls, _ = cli
    with pytest.raises(RuntimeError, match="No Signal contact match"):
        invoke_send(monkeypatch, ACCOUNTS[1]["aci"], identifier)
    assert not any("send" in command for command in calls)


@pytest.mark.parametrize("identifier", [None, "not-a-uuid", "00000000-0000-0000-0000-000000000000", 123])
def test_numberless_contact_with_invalid_uuid_stops_before_send(cli, monkeypatch, identifier):
    calls, state = cli
    state["contacts"] = [{**CONTACTS[1], "uuid": identifier}]
    with pytest.raises(RuntimeError, match="no usable E.164 number or ACI UUID"):
        invoke_send(monkeypatch, ACCOUNTS[1]["aci"], "Fixture Bob")
    assert not any("send" in command for command in calls)


def test_malformed_uuid_field_is_not_used_for_identifier_search(cli):
    _, state = cli
    state["contacts"] = [{**CONTACTS[0], "uuid": "not-a-uuid"}]
    with pytest.raises(RuntimeError, match="No Signal contact match"):
        SEND.resolve_number(ACCOUNTS[0]["number"], "not-a-uuid")


def test_missing_account_is_rejected_before_any_cli_call(cli, monkeypatch):
    calls, _ = cli
    monkeypatch.setattr(sys, "argv", ["send_message.py", "--to", "Fixture Bob", "--text", "fixture"])
    with pytest.raises(SystemExit) as exc:
        SEND.main()
    assert exc.value.code == 2
    assert calls == []


def test_empty_recipient_is_rejected_before_any_cli_call(cli, monkeypatch):
    calls, _ = cli
    with pytest.raises(RuntimeError, match="must not be empty"):
        invoke_send(monkeypatch, ACCOUNTS[1]["aci"], " ")
    assert calls == []


def test_client_lookup_error_does_not_trigger_a_send_or_account_fallback(cli, monkeypatch):
    calls, state = cli
    state["error"] = "fixture account unavailable"
    with pytest.raises(RuntimeError, match="fixture account unavailable"):
        invoke_send(monkeypatch, ACCOUNTS[1]["aci"], "Fixture Bob")
    assert len(calls) == 1
    assert ACCOUNTS[1]["aci"] in calls[0]
    assert not any("send" in command for command in calls)


@pytest.mark.parametrize("query", ["Fixture Bob", CONTACTS[1]["uuid"], CONTACTS[1]["uuid"].upper()])
def test_find_contact_keeps_null_phone_and_uuid(cli, monkeypatch, capsys, query):
    calls, _ = cli
    monkeypatch.setattr(sys, "argv", ["find_contact.py", "--account", ACCOUNTS[1]["aci"], "--query", query])
    assert FIND.main() == 0
    result = json.loads(capsys.readouterr().out)
    assert len(result) == 1
    assert result[0]["number"] is None
    assert result[0]["uuid"] == CONTACTS[1]["uuid"]
    assert calls[0] == ["signal-cli", "-o", "json", "--account", ACCOUNTS[1]["aci"], "listContacts"]


def test_find_contact_does_not_match_a_uuid_fragment(cli, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["find_contact.py", "--account", ACCOUNTS[1]["aci"], "--query", "2222aaaa"])
    assert FIND.main() == 0
    assert json.loads(capsys.readouterr().out) == []


def test_find_contact_retains_phone_fragment_search(cli, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["find_contact.py", "--account", ACCOUNTS[0]["number"], "--query", "0101002"])
    assert FIND.main() == 0
    result = json.loads(capsys.readouterr().out)
    assert [row["number"] for row in result] == [CONTACTS[0]["number"]]
