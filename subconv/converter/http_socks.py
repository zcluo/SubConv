from __future__ import annotations

import urllib.parse as urlparse

from pydantic import Field

from .models import MihomoBaseModel
from .registry import NameRegistry
from .util import ParseError, base64_raw_std_decode, base64_raw_url_decode


class HttpSocksProxy(MihomoBaseModel):
    name: str = Field(alias="name")
    type: str = Field(alias="type")
    server: str = Field(alias="server")
    port: int = Field(alias="port")
    username: str | None = Field(None, alias="username")
    password: str | None = Field(None, alias="password")
    tls: bool | None = Field(None, alias="tls")
    skip_cert_verify: bool | None = Field(None, alias="skip-cert-verify")

    def to_dict(self) -> dict[str, object]:
        return self.model_dump(by_alias=True, exclude_none=True)


def parse_http_socks(line: str, registry: NameRegistry) -> HttpSocksProxy:
    url = urlparse.urlparse(line)
    server = url.hostname
    if not server:
        raise ParseError("http/socks: missing host")

    try:
        port = url.port
    except ValueError as exc:
        raise ParseError("http/socks: invalid port") from exc

    if port is None:
        raise ParseError("http/socks: missing port")

    proxy_type = _proxy_type(url.scheme.lower())
    username, password = _parse_credentials(url)
    name = registry.register(urlparse.unquote_plus(url.fragment) or f"{server}:{port}")

    payload: dict[str, object] = {
        "name": name,
        "type": proxy_type,
        "server": server,
        "port": port,
        "skip_cert_verify": True,
    }

    if username is not None:
        payload["username"] = username
    if password is not None:
        payload["password"] = password
    if url.scheme.lower() == "https":
        payload["tls"] = True

    return HttpSocksProxy.model_validate(payload)


def _proxy_type(scheme: str) -> str:
    if scheme in {"socks", "socks5", "socks5h"}:
        return "socks5"
    if scheme in {"http", "https"}:
        return "http"
    raise ParseError("http/socks: unsupported scheme")


def _parse_credentials(url: urlparse.ParseResult) -> tuple[str | None, str | None]:
    raw_userinfo, _, _ = url.netloc.rpartition("@")
    if raw_userinfo:
        decoded = _decode_credentials(urlparse.unquote(raw_userinfo))
        if decoded is not None:
            return decoded

    return (None, None)


def _decode_credentials(raw_userinfo: str) -> tuple[str | None, str | None] | None:
    for decoder in (base64_raw_std_decode, base64_raw_url_decode):
        try:
            decoded = decoder(raw_userinfo)
        except Exception:
            continue

        username, separator, password = decoded.partition(":")
        if not username:
            return None
        if separator:
            return username, password or None
        return username, None

    return None
