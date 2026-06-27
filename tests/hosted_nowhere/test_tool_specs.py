import json
import pathlib
import subprocess
import sys


SCRIPT_PATH = (
    pathlib.Path(__file__).resolve().parents[2]
    / "skills"
    / "hosted-nowhere"
    / "scripts"
    / "tool_specs.py"
)


def load_specs_module():
    namespace = {}
    exec(SCRIPT_PATH.read_text(), namespace)
    return namespace


def test_expected_builder_slugs():
    module = load_specs_module()
    specs = module["load_specs"]()
    assert [spec.slug for spec in specs] == [
        "store",
        "message",
        "fundraiser",
        "petition",
        "event",
        "forum",
        "drop",
        "art",
    ]


def test_specs_have_valid_routes_and_references():
    module = load_specs_module()
    specs = module["load_specs"]()
    skill_dir = SCRIPT_PATH.parents[1]

    for spec in specs:
        assert spec.create_url == f"https://hostednowhere.com/create/{spec.slug}"
        assert (skill_dir / spec.reference).exists()
        assert spec.share_step > 0
        assert spec.minimum_requirements


def test_high_stakes_key_sensitive_builders_are_correct():
    module = load_specs_module()
    specs = {spec.slug: spec for spec in module["load_specs"]()}

    assert specs["store"].key_ownership_sensitive is True
    assert specs["petition"].key_ownership_sensitive is True
    assert specs["forum"].key_ownership_sensitive is True
    assert specs["event"].key_ownership_sensitive is False
    assert specs["message"].requires_description_or_title is True
    assert specs["drop"].requires_description is True
    assert specs["art"].requires_svg is True


def test_json_cli_emits_all_specs():
    result = subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--json"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert len(payload) == 8
    assert payload[0]["slug"] == "store"
    assert payload[-1]["slug"] == "art"
