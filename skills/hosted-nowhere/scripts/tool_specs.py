#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class ToolSpec:
    slug: str
    label: str
    share_step: int
    requires_pubkey: bool
    requires_name: bool
    requires_description: bool
    requires_description_or_title: bool
    requires_items: bool
    requires_svg: bool
    key_ownership_sensitive: bool
    disposable_key_ok_for_tests: bool
    warning: str

    @property
    def create_url(self) -> str:
        return f"https://hostednowhere.com/create/{self.slug}"

    @property
    def reference(self) -> str:
        return f"references/{self.slug}.md"

    @property
    def minimum_requirements(self) -> list[str]:
        items: list[str] = []
        if self.requires_pubkey:
            items.append("public key")
        if self.requires_name:
            items.append("name")
        if self.requires_description:
            items.append("description/body")
        if self.requires_description_or_title:
            items.append("description/body or title")
        if self.requires_items:
            items.append("at least 1 item with name and numeric price")
        if self.requires_svg:
            items.append("SVG content")
        return items

    def as_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["create_url"] = self.create_url
        payload["reference"] = self.reference
        payload["minimum_requirements"] = self.minimum_requirements
        return payload


TOOL_SPECS = [
    ToolSpec(
        slug="store",
        label="Store",
        share_step=10,
        requires_pubkey=True,
        requires_name=True,
        requires_description=False,
        requires_description_or_title=False,
        requires_items=True,
        requires_svg=False,
        key_ownership_sensitive=True,
        disposable_key_ok_for_tests=True,
        warning="Encrypted orders are unreadable unless the builder key is one the user controls.",
    ),
    ToolSpec(
        slug="message",
        label="Message",
        share_step=6,
        requires_pubkey=False,
        requires_name=True,
        requires_description=False,
        requires_description_or_title=True,
        requires_items=False,
        requires_svg=False,
        key_ownership_sensitive=False,
        disposable_key_ok_for_tests=True,
        warning="A message with no body needs a title tag to become publishable.",
    ),
    ToolSpec(
        slug="fundraiser",
        label="Fundraiser",
        share_step=6,
        requires_pubkey=False,
        requires_name=True,
        requires_description=False,
        requires_description_or_title=False,
        requires_items=False,
        requires_svg=False,
        key_ownership_sensitive=False,
        disposable_key_ok_for_tests=True,
        warning="Fundraisers can publish with a simple name first, then optional payment and story details later.",
    ),
    ToolSpec(
        slug="petition",
        label="Petition",
        share_step=7,
        requires_pubkey=True,
        requires_name=True,
        requires_description=False,
        requires_description_or_title=False,
        requires_items=False,
        requires_svg=False,
        key_ownership_sensitive=True,
        disposable_key_ok_for_tests=True,
        warning="Encrypted signatures are unreadable unless the petition key is one the user controls.",
    ),
    ToolSpec(
        slug="event",
        label="Event",
        share_step=7,
        requires_pubkey=False,
        requires_name=True,
        requires_description=False,
        requires_description_or_title=False,
        requires_items=False,
        requires_svg=False,
        key_ownership_sensitive=False,
        disposable_key_ok_for_tests=True,
        warning="Event pages can publish from a name alone, but become more useful once date and venue are set.",
    ),
    ToolSpec(
        slug="forum",
        label="Forum",
        share_step=5,
        requires_pubkey=True,
        requires_name=True,
        requires_description=False,
        requires_description_or_title=False,
        requires_items=False,
        requires_svg=False,
        key_ownership_sensitive=True,
        disposable_key_ok_for_tests=True,
        warning="Forum management and verification depend on the private key for the chosen public key.",
    ),
    ToolSpec(
        slug="drop",
        label="Drop",
        share_step=4,
        requires_pubkey=False,
        requires_name=False,
        requires_description=True,
        requires_description_or_title=False,
        requires_items=False,
        requires_svg=False,
        key_ownership_sensitive=False,
        disposable_key_ok_for_tests=True,
        warning="A Drop does not need a title, but it does need body text before Share Link works.",
    ),
    ToolSpec(
        slug="art",
        label="Art",
        share_step=5,
        requires_pubkey=False,
        requires_name=False,
        requires_description=False,
        requires_description_or_title=False,
        requires_items=False,
        requires_svg=True,
        key_ownership_sensitive=False,
        disposable_key_ok_for_tests=True,
        warning="Art pages require valid SVG content before verification and sharing become useful.",
    ),
]


def load_specs() -> list[ToolSpec]:
    return list(TOOL_SPECS)


def references_exist(skill_dir: Path) -> dict[str, bool]:
    return {spec.slug: (skill_dir / spec.reference).exists() for spec in TOOL_SPECS}


def main() -> None:
    parser = argparse.ArgumentParser(description="Hosted Nowhere builder metadata")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args()

    if args.json:
        print(json.dumps([spec.as_dict() for spec in TOOL_SPECS], indent=2, sort_keys=True))
        return

    for spec in TOOL_SPECS:
        print(f"{spec.label}: {spec.create_url}")


if __name__ == "__main__":
    main()
