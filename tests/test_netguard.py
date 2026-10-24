"""Resolve-then-check outbound URL guard (SSRF), 2026-09-03 fleet review K-006."""
from __future__ import annotations

import socket

import pytest

from huginn_muninn import netguard
from huginn_muninn.netguard import host_is_public


@pytest.fixture
def resolver(monkeypatch):
    """Install a fake resolver; returns a dict the test fills with name -> addresses."""
    table: dict[str, list[str]] = {}

    def fake(hostname: str) -> list[str]:
        if hostname not in table:
            raise socket.gaierror(8, "nodename nor servname provided")
        return table[hostname]

    monkeypatch.setattr(netguard, "resolve_addresses", fake)
    return table


class TestLiterals:
    def test_public_literal_passes(self):
        assert host_is_public("93.184.216.34")[0] is True

    @pytest.mark.parametrize("ip", ["127.0.0.1", "10.0.0.5", "192.168.1.1", "172.16.0.1",
                                    "169.254.169.254", "0.0.0.0", "::1", "fe80::1"])
    def test_private_literals_blocked(self, ip):
        assert host_is_public(ip)[0] is False

    def test_missing_hostname_blocked(self):
        assert host_is_public(None)[0] is False
        assert host_is_public("")[0] is False


class TestNames:
    def test_local_names_blocked_without_resolving(self, resolver):
        for name in ("localhost", "printer.local", "db.internal", "LOCALHOST", "svc.localhost"):
            assert host_is_public(name)[0] is False, name

    def test_name_resolving_public_passes(self, resolver):
        resolver["hooks.example.com"] = ["93.184.216.34"]
        ok, reason = host_is_public("hooks.example.com")
        assert ok is True
        assert "public" in reason

    def test_name_resolving_private_blocked(self, resolver):
        resolver["evil.example.com"] = ["127.0.0.1"]
        assert host_is_public("evil.example.com")[0] is False

    def test_mixed_answers_blocked(self, resolver):
        resolver["mixed.example.com"] = ["93.184.216.34", "10.0.0.9"]
        assert host_is_public("mixed.example.com")[0] is False

    def test_unresolvable_fails_closed(self, resolver):
        ok, reason = host_is_public("does-not-exist.invalid")
        assert ok is False
        assert "did not resolve" in reason

    def test_non_dotted_decimal_literal_goes_through_resolver(self, resolver):
        """ipaddress rejects 2130706433; Linux resolvers map it to 127.0.0.1."""
        resolver["2130706433"] = ["127.0.0.1"]
        assert host_is_public("2130706433")[0] is False

    def test_ipv6_zone_suffix_is_parsed(self, resolver):
        resolver["z.example.com"] = ["fe80::1%eth0"]
        assert host_is_public("z.example.com")[0] is False
