from __future__ import annotations

import base64
import urllib.parse as urlparse
from typing import Callable, Protocol

from .hysteria import parse_hysteria
from .hysteria2 import parse_hysteria2
from .http_socks import parse_http_socks
from .registry import NameRegistry
from .shadowsocks import parse_ss
from .shadowsocksr import parse_ssr
from .telegram import parse_tg, parse_tg_https
from .trojan import parse_trojan
from .tuic import parse_tuic
from .util import ParseError
from .vless import parse_vless
from .vmess import parse_vmess


class ProxyModel(Protocol):
    def to_dict(self) -> dict[str, object]: ...


ParserFn = Callable[[str, NameRegistry], ProxyModel | None]


async def ConvertsV2Ray(buf: bytes | str) -> list[dict[str, object]]:
    try:
        data = base64.b64decode(
            buf + b"=" * (-len(buf) % 4)
            if isinstance(buf, bytes)
            else buf + "=" * (-len(buf) % 4)
        ).decode("utf-8")
    except Exception:
        try:
            data = buf.decode("utf-8") if isinstance(buf, bytes) else buf
        except Exception:
            data = buf if isinstance(buf, str) else ""

    lines = data.splitlines()
    proxies: list[dict[str, object]] = []
    registry = NameRegistry()

    for line in lines:
        line = line.rstrip(" \r")
        if not line:
            continue

        if "://" not in line:
            continue

        scheme, _ = line.split("://", 1)
        scheme = scheme.lower()
        parser = _select_parser(line, scheme)

        try:
            proxy = parser(line, registry)
            if proxy is not None:
                proxies.append(proxy.to_dict())
        except ParseError:
            continue

    if not proxies:
        raise Exception("No valid proxies found")

    return proxies


def _unsupported(line: str, registry: NameRegistry) -> None:
    del line, registry
    return None


def _select_parser(line: str, scheme: str) -> ParserFn:
    if scheme == "https":
        hostname = urlparse.urlparse(line).hostname
        if hostname == "t.me":
            return parse_tg_https
        return parse_http_socks
    return _DISPATCH.get(scheme, _unsupported)


_DISPATCH: dict[str, ParserFn] = {
    "hysteria": parse_hysteria,
    "hysteria2": parse_hysteria2,
    "hy2": parse_hysteria2,
    "tuic": parse_tuic,
    "trojan": parse_trojan,
    "vless": parse_vless,
    "vmess": parse_vmess,
    "ss": parse_ss,
    "ssr": parse_ssr,
    "socks": parse_http_socks,
    "socks5": parse_http_socks,
    "socks5h": parse_http_socks,
    "http": parse_http_socks,
    "tg": parse_tg,
}
