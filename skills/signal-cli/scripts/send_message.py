#!/usr/bin/env python3

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


FIELDS = [
    "name",
    "givenName",
    "familyName",
    "nickName",
    "nickGivenName",
    "nickFamilyName",
    "username",
    "number",
    "uuid",
]

UUID_RE = re.compile(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")


def run(cmd: list[str]) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"command failed ({result.returncode}): {' '.join(cmd)}\n{result.stderr.strip()}"
        )
    return result.stdout


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip().lower())


def is_e164(value: str) -> bool:
    return isinstance(value, str) and bool(re.fullmatch(r"\+[1-9]\d{6,14}", value.strip()))


def is_aci_uuid(value: str) -> bool:
    return (
        isinstance(value, str)
        and bool(UUID_RE.fullmatch(value.strip()))
        and value.strip() != "00000000-0000-0000-0000-000000000000"
    )


def contact_identifier(contact: dict) -> str | None:
    if is_e164(contact.get("number")):
        return contact["number"].strip()
    if is_aci_uuid(contact.get("uuid")):
        return contact["uuid"].strip()
    return None


def score_contact(contact: dict, query: str) -> int:
    best = 0
    for field in FIELDS:
        raw_value = contact.get(field)
        if not raw_value:
            continue
        if field == "uuid" and not is_aci_uuid(raw_value):
            continue
        candidate = normalize(str(raw_value))
        if candidate == query:
            best = max(best, 100)
        elif field == "uuid":
            # An identifier fragment must never guess a recipient.
            continue
        elif query and candidate.startswith(query):
            best = max(best, 60)
        elif query and query in candidate:
            best = max(best, 40)
    return best


def resolve_number(account: str, recipient: str) -> tuple[str | None, list[dict]]:
    recipient = recipient.strip()
    if not recipient:
        raise RuntimeError("Recipient must not be empty")
    if is_e164(recipient) or is_aci_uuid(recipient):
        return recipient, []

    output = run(["signal-cli", "-o", "json", "--account", account, "listContacts"])
    contacts = json.loads(output)
    query = normalize(recipient)

    matches = []
    for contact in contacts:
        score = score_contact(contact, query)
        if score > 0:
            matches.append((score, contact))

    matches.sort(
        key=lambda item: (
            -item[0],
            normalize(item[1].get("name") or ""),
            item[1].get("number") or item[1].get("uuid") or "",
        )
    )

    if not matches:
        raise RuntimeError(
            f"No Signal contact match for '{recipient}'. Use an explicit E.164 number or ACI UUID, or check the contact in the selected Signal account."
        )

    best_score = matches[0][0]
    top_matches = [contact for score, contact in matches if score == best_score]
    if len(top_matches) != 1:
        candidates = []
        for contact in top_matches[:10]:
            candidates.append(
                {
                    "score": best_score,
                    "number": contact.get("number"),
                    "uuid": contact.get("uuid"),
                    "name": contact.get("name"),
                    "nickName": contact.get("nickName"),
                    "givenName": contact.get("givenName"),
                    "familyName": contact.get("familyName"),
                }
            )
        return None, candidates

    identifier = contact_identifier(top_matches[0])
    if identifier is None:
        raise RuntimeError(
            f"Signal contact '{recipient}' has no usable E.164 number or ACI UUID. "
            "Check this contact in the selected account before sending."
        )
    return identifier, []


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--account", required=True, help="Sender E.164 number or ACI from listAccounts (numberless accounts require signal-cli 0.14.9+)")
    parser.add_argument(
        "--to",
        required=True,
        help="Recipient E.164 number, full ACI UUID, or contact name to resolve through listContacts",
    )
    parser.add_argument("--text", required=True, help="Message text")
    parser.add_argument(
        "--attachment",
        action="append",
        default=[],
        help="Attachment path; may be passed multiple times",
    )
    args = parser.parse_args()

    identifier, candidates = resolve_number(args.account, args.to)
    if identifier is None:
        print(
            json.dumps(
                {"error": "ambiguous_recipient", "candidates": candidates},
                ensure_ascii=False,
                indent=2,
            )
        )
        return 3

    command = ["signal-cli", "--account", args.account, "send", identifier, "-m", args.text]
    for attachment in args.attachment:
        command.extend(["-a", str(Path(attachment).expanduser())])

    run(command)
    print(json.dumps({"ok": True, "account": args.account, "to": identifier}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2)
