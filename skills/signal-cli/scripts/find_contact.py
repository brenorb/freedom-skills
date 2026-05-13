#!/usr/bin/env python3

import argparse
import json
import re
import subprocess
import sys


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
    return bool(re.fullmatch(r"\+[1-9]\d{6,14}", (value or "").strip()))


def score_contact(contact: dict, query: str) -> int:
    best = 0
    for field in FIELDS:
        raw_value = contact.get(field)
        if not raw_value:
            continue
        candidate = normalize(str(raw_value))
        if candidate == query:
            best = max(best, 100)
        elif query and candidate.startswith(query):
            best = max(best, 60)
        elif query and query in candidate:
            best = max(best, 40)
    return best


def load_contacts(account: str) -> list[dict]:
    output = run(["signal-cli", "-o", "json", "-u", account, "listContacts"])
    return json.loads(output)


def simplify(contact: dict, score: int) -> dict:
    return {
        "score": score,
        "number": contact.get("number"),
        "name": contact.get("name"),
        "nickName": contact.get("nickName"),
        "givenName": contact.get("givenName"),
        "familyName": contact.get("familyName"),
        "username": contact.get("username"),
        "uuid": contact.get("uuid"),
        "isBlocked": contact.get("isBlocked"),
        "unregistered": contact.get("unregistered"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--account", required=True, help="Sender account in E.164 format")
    parser.add_argument("--query", required=True, help="Name, nickname, or number fragment")
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()

    contacts = load_contacts(args.account)
    query = args.query.strip()
    normalized_query = normalize(query)

    matches = []
    if is_e164(query):
        for contact in contacts:
            if contact.get("number") == query:
                matches.append(simplify(contact, 100))
    else:
        for contact in contacts:
            score = score_contact(contact, normalized_query)
            if score > 0:
                matches.append(simplify(contact, score))

    matches.sort(
        key=lambda item: (
            -item["score"],
            normalize(item.get("name") or ""),
            item.get("number") or "",
        )
    )
    print(json.dumps(matches[: args.limit], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2)
