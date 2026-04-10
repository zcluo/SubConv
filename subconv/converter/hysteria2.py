"""Hysteria2 share link parser.

Formats: ``hysteria2://auth@host:port?sni=xxx#name`` or ``hy2://...``
Both normalize to ``type: "hysteria2"``.

Aligned with mihomo ``common/convert/converter.go`` case ``"hysteria2" | "hy2"``.
"""

from __future__ import annotations

import urllib.parse as urlparse

from pydantic import Field

from .models import MihomoBaseModel
from .registry import NameRegistry
from .util import ParseError


class Hysteria2Proxy(MihomoBaseModel):
    name: str = Field(alias="name")
    type: str = Field(alias="type")
    server: str = Field(alias="server")
    port: int = Field(alias="port")
    password: str | None = Field(None, alias="password")
    obfs: str | None = Field(None, alias="obfs")
    obfs_password: str | None = Field(None, alias="obfs-password")
    sni: str | None = Field(None, alias="sni")
    skip_cert_verify: bool | None = Field(None, alias="skip-cert-verify")
    alpn: list[str] | None = Field(None, alias="alpn")
    fingerprint: str | None = Field(None, alias="fingerprint")
    down: str | None = Field(None, alias="down")
    up: str | None = Field(None, alias="up")

    def to_dict(self) -> dict[str, object]:
        return self.model_dump(by_alias=True, exclude_none=True)


def parse_hysteria2(line: str, registry: NameRegistry) -> Hysteria2Proxy:
    url = urlparse.urlparse(line)
    if not url.hostname:
        raise ParseError("hysteria2: missing host")

    query = dict(urlparse.parse_qsl(url.query))
    port = url.port or 443

    kwargs: dict[str, object] = {
        "name": registry.register(urlparse.unquote_plus(url.fragment)),
        "type": "hysteria2",
        "server": url.hostname,
        "port": port,
        "obfs": query.get("obfs") or None,
        "obfs_password": query.get("obfs-password") or None,
        "sni": query.get("sni") or None,
    }

    if query.get("insecure"):
        kwargs["skip_cert_verify"] = _parse_bool(query.get("insecure"))

    if alpn := query.get("alpn"):
        kwargs["alpn"] = alpn.split(",")

    if auth := url.username:
        kwargs["password"] = auth

    if fp := query.get("pinSHA256"):
        kwargs["fingerprint"] = fp

    if down := query.get("down"):
        kwargs["down"] = down
    if up := query.get("up"):
        kwargs["up"] = up

    return Hysteria2Proxy.model_validate(kwargs)


def _parse_bool(val: str | None) -> bool:
    if val is None:
        return False
    return val.lower() in ("1", "true", "yes")
