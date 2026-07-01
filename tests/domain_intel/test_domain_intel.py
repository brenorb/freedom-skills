from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def load_module():
    module_path = (
        Path(__file__).resolve().parents[2]
        / "skills"
        / "domain-intel"
        / "scripts"
        / "domain_intel.py"
    )
    spec = importlib.util.spec_from_file_location("domain_intel_skill", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


domain_intel = load_module()


class FakeResponse:
    def __init__(self, payload: dict):
        self.payload = payload

    def read(self):
        return json.dumps(self.payload).encode()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return None


def test_whois_lookup_errors_for_unknown_tld():
    result = domain_intel.whois_lookup("example.unknown")
    assert result == {"error": "No WHOIS server for .unknown"}


def test_dns_records_returns_empty_lists_when_lookups_fail(monkeypatch):
    def fake_getaddrinfo(*args, **kwargs):
        raise OSError("no record")

    def fake_urlopen(*args, **kwargs):
        raise OSError("doh unavailable")

    monkeypatch.setattr(domain_intel.socket, "getaddrinfo", fake_getaddrinfo)
    monkeypatch.setattr(domain_intel.urllib.request, "urlopen", fake_urlopen)

    result = domain_intel.dns_records("example.com")

    assert result["domain"] == "example.com"
    assert result["records"] == {
        "A": [],
        "AAAA": [],
        "MX": [],
        "NS": [],
        "TXT": [],
        "CNAME": [],
    }


def test_bulk_check_limits_domains_to_first_twenty(monkeypatch):
    seen = []

    def fake_ssl(domain):
        seen.append(domain)
        return {"host": domain}

    monkeypatch.setitem(domain_intel.COMMAND_MAP, "ssl", fake_ssl)

    domains = [f"example{i}.com" for i in range(25)]
    result = domain_intel.bulk_check(domains, checks=["ssl"], max_workers=2)

    assert result["total"] == 20
    assert sorted(seen) == sorted(domains[:20])


def test_dns_records_trims_trailing_dots_from_doh_answers(monkeypatch):
    def fake_getaddrinfo(*args, **kwargs):
        if args[2] == domain_intel.socket.AF_INET:
            return [(None, None, None, None, ("93.184.216.34", 0))]
        raise OSError("no ipv6")

    def fake_urlopen(*args, **kwargs):
        return FakeResponse({"Answer": [{"data": "ns1.example.com."}]})

    monkeypatch.setattr(domain_intel.socket, "getaddrinfo", fake_getaddrinfo)
    monkeypatch.setattr(domain_intel.urllib.request, "urlopen", fake_urlopen)

    result = domain_intel.dns_records("example.com", types=["A", "NS"])

    assert result["records"]["A"] == ["93.184.216.34"]
    assert result["records"]["NS"] == ["ns1.example.com"]
