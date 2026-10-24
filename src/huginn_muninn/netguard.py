"""Outbound-URL guard: resolve, then check every address (SSRF).

`_validate_url` in api.py used to inspect only the literal form of a
hostname: an IP literal was checked, a DNS name was checked against three
suffixes. Two holes followed. A name resolving to a private address passed,
and a non-dotted literal such as ``2130706433`` failed the IP parse, fell into
the DNS branch, and on Linux resolves to 127.0.0.1. The rule here is the one
the 2026-09-03 fleet review asked for: resolve the name, check every address,
fail closed on anything unresolvable, and check again at delivery time because
DNS can change between registration and the POST.
"""
from __future__ import annotations

import ipaddress
import logging
import socket

log = logging.getLogger(__name__)

_LOCAL_NAME_SUFFIXES = (".local", ".internal", ".localhost")


def _is_blocked(addr: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    return (
        addr.is_private
        or addr.is_loopback
        or addr.is_link_local
        or addr.is_reserved
        or addr.is_multicast
        or addr.is_unspecified
    )


def resolve_addresses(hostname: str) -> list[str]:
    """Every address the resolver returns for the name. Tests replace this."""
    infos = socket.getaddrinfo(hostname, None, proto=socket.IPPROTO_TCP)
    return sorted({info[4][0] for info in infos})


def host_is_public(hostname: str | None) -> tuple[bool, str]:
    """Return (ok, reason). ok is False for anything not provably public."""
    if not hostname:
        return False, "missing hostname"
    lower = hostname.strip().lower().rstrip(".")
    if lower == "localhost" or lower.endswith(_LOCAL_NAME_SUFFIXES):
        return False, f"{hostname} is a local name"
    try:
        literal = ipaddress.ip_address(lower)
    except ValueError:
        literal = None
    if literal is not None:
        if _is_blocked(literal):
            return False, f"{hostname} is a private or internal address"
        return True, "public address literal"
    try:
        addresses = resolve_addresses(lower)
    except (socket.gaierror, UnicodeError, OSError) as e:
        return False, f"{hostname} did not resolve ({e.__class__.__name__})"
    if not addresses:
        return False, f"{hostname} resolved to no addresses"
    for raw in addresses:
        try:
            addr = ipaddress.ip_address(raw.split("%")[0])
        except ValueError:
            return False, f"{hostname} resolved to unparseable address {raw!r}"
        if _is_blocked(addr):
            return False, f"{hostname} resolves to private or internal address {raw}"
    return True, f"{hostname} resolves to {len(addresses)} public address(es)"
