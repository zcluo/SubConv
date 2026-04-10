"""VLESS share link parser aligned with mihomo common/convert/v.go."""

from __future__ import annotations

import binascii
import json
import urllib.parse as urlparse
from typing import TypeVar

from pydantic import Field

from .models import (
    ECHOpts,
    GrpcOpts,
    H2Opts,
    HttpOpts,
    MihomoBaseModel,
    RealityOpts,
    WsOpts,
    XhttpDownloadSettings,
    XhttpOpts,
    XhttpReuseSettings,
)
from .registry import NameRegistry
from .util import (
    ParseError,
    base64_raw_std_decode,
    base64_raw_url_decode,
    rand_user_agent,
)


T = TypeVar("T")


class VlessProxy(MihomoBaseModel):
    name: str = Field(alias="name")
    type: str = Field(alias="type")
    server: str = Field(alias="server")
    port: int = Field(alias="port")
    uuid: str = Field(alias="uuid")
    flow: str | None = Field(None, alias="flow")
    tls: bool | None = Field(None, alias="tls")
    alpn: list[str] | None = Field(None, alias="alpn")
    udp: bool = Field(True, alias="udp")
    packet_addr: bool | None = Field(None, alias="packet-addr")
    xudp: bool | None = Field(None, alias="xudp")
    packet_encoding: str | None = Field(None, alias="packet-encoding")
    encryption: str | None = Field(None, alias="encryption")
    network: str | None = Field(None, alias="network")
    ech_opts: ECHOpts | None = Field(None, alias="ech-opts")
    reality_opts: RealityOpts | None = Field(None, alias="reality-opts")
    http_opts: HttpOpts | None = Field(None, alias="http-opts")
    h2_opts: H2Opts | None = Field(None, alias="h2-opts")
    grpc_opts: GrpcOpts | None = Field(None, alias="grpc-opts")
    ws_opts: WsOpts | None = Field(None, alias="ws-opts")
    xhttp_opts: XhttpOpts | None = Field(None, alias="xhttp-opts")
    ws_headers: dict[str, str] | None = Field(None, alias="ws-headers")
    skip_cert_verify: bool | None = Field(None, alias="skip-cert-verify")
    fingerprint: str | None = Field(None, alias="fingerprint")
    certificate: str | None = Field(None, alias="certificate")
    private_key: str | None = Field(None, alias="private-key")
    servername: str | None = Field(None, alias="servername")
    client_fingerprint: str | None = Field(None, alias="client-fingerprint")

    def to_dict(self) -> dict[str, object]:
        return self.model_dump(by_alias=True, exclude_none=True)


def parse_vless(line: str, registry: NameRegistry) -> VlessProxy:
    url = urlparse.urlparse(line)
    url = _decode_vless_host(url)

    proxy = handle_v_share_link(url, registry, "vless")
    query = urlparse.parse_qs(url.query, keep_blank_values=True)

    flow = _query_first(query, "flow")
    if flow:
        proxy["flow"] = flow.lower()

    encryption = _query_first(query, "encryption")
    if encryption:
        proxy["encryption"] = encryption

    return VlessProxy.model_validate(proxy)


def handle_v_share_link(
    url: urlparse.ParseResult, registry: NameRegistry, scheme: str
) -> dict[str, object]:
    query = urlparse.parse_qs(url.query, keep_blank_values=True)

    port = _port_from_url(url)
    hostname = url.hostname
    if not hostname:
        raise ParseError("v share link: missing host")
    if port is None:
        raise ParseError("v share link: missing port")

    proxy: dict[str, object] = {
        "name": registry.register(urlparse.unquote_plus(url.fragment)),
        "type": scheme,
        "server": hostname,
        "port": port,
        "uuid": url.username or "",
        "udp": True,
    }

    security = _query_first(query, "security").lower()
    if security.endswith("tls") or security == "reality":
        proxy["tls"] = True
        fingerprint = _query_first(query, "fp")
        proxy["client_fingerprint"] = fingerprint if fingerprint else "chrome"

        alpn = _query_first(query, "alpn")
        if alpn:
            proxy["alpn"] = alpn.split(",")

        pcs = _query_first(query, "pcs")
        if pcs:
            proxy["fingerprint"] = pcs

    sni = _query_first(query, "sni")
    if sni:
        proxy["servername"] = sni

    pbk = _query_first(query, "pbk")
    if pbk:
        proxy["reality_opts"] = RealityOpts.model_construct(
            public_key=pbk,
            short_id=_query_first(query, "sid") or None,
        )

    packet_encoding = _query_first(query, "packetEncoding")
    if packet_encoding == "packet":
        proxy["packet_addr"] = True
    elif packet_encoding != "none":
        proxy["xudp"] = True

    network = _query_first(query, "type").lower()
    if not network:
        network = "tcp"
    fake_type = _query_first(query, "headerType").lower()
    if fake_type == "http":
        network = "http"
    elif network == "http":
        network = "h2"
    proxy["network"] = network

    if network == "tcp":
        if fake_type != "none":
            headers: dict[str, list[str]] = {}
            host = _query_first(query, "host")
            if host:
                headers["Host"] = [host]

            method = _query_first(query, "method")
            proxy["http_opts"] = HttpOpts.model_construct(
                method=method or None,
                path=[_query_first(query, "path") or "/"],
                headers=headers,
            )

    elif network == "http":
        # headerType=="http" forces network="http" → outputs h2-opts
        # (when type=="http" without headerType, network becomes "h2" with no opts)
        h2_path = _query_first(query, "path") or "/"
        h2_host = _query_first(query, "host")
        proxy["h2_opts"] = H2Opts.model_construct(
            path=[h2_path],
            host=[h2_host] if h2_host else None,
            headers={},
        )

    elif network in {"ws", "httpupgrade"}:
        ws_path = _query_first(query, "path")
        ws_headers = {
            "User-Agent": rand_user_agent(),
            "Host": _query_first(query, "host"),
        }
        max_early_data: int | None = None
        early_data_header_name: str | None = None
        v2ray_http_upgrade_fast_open: bool | None = None

        early_data = _query_first(query, "ed")
        if early_data:
            try:
                max_early_data = int(early_data)
            except ValueError as exc:
                raise ParseError(f"bad WebSocket max early data size: {exc}") from exc
            if network == "ws":
                early_data_header_name = "Sec-WebSocket-Protocol"
            else:
                max_early_data = None
                v2ray_http_upgrade_fast_open = True

        early_data_header = _query_first(query, "eh")
        if early_data_header:
            early_data_header_name = early_data_header

        proxy["ws_opts"] = WsOpts.model_construct(
            path=ws_path,
            headers=ws_headers,
            max_early_data=max_early_data,
            early_data_header_name=early_data_header_name,
            v2ray_http_upgrade_fast_open=v2ray_http_upgrade_fast_open,
        )

    elif network == "grpc":
        proxy["grpc_opts"] = GrpcOpts.model_construct(
            grpc_service_name=_query_first(query, "serviceName")
        )

    elif network == "xhttp":
        proxy["network"] = "xhttp"
        path = _query_first(query, "path")
        host = _query_first(query, "host")
        mode = _query_first(query, "mode")
        extra_opts: dict[str, object] = {}

        extra = _query_first(query, "extra")
        if extra:
            try:
                extra_map = json.loads(extra)
            except json.JSONDecodeError:
                extra_map = None
            if isinstance(extra_map, dict):
                extra_opts = _parse_xhttp_extra(extra_map)

        proxy["xhttp_opts"] = XhttpOpts.model_construct(
            path=path or None,
            host=host or None,
            mode=mode or None,
            headers=None,
            no_grpc_header=_get_typed(extra_opts, "no_grpc_header", bool),
            x_padding_bytes=_get_typed(extra_opts, "x_padding_bytes", str),
            sc_max_each_post_bytes=_get_typed(
                extra_opts, "sc_max_each_post_bytes", int
            ),
            reuse_settings=_get_typed(extra_opts, "reuse_settings", XhttpReuseSettings),
            download_settings=_get_typed(
                extra_opts, "download_settings", XhttpDownloadSettings
            ),
        )

    return proxy


def _decode_vless_host(url: urlparse.ParseResult) -> urlparse.ParseResult:
    userinfo = ""
    hostpart = url.netloc
    if "@" in hostpart:
        userinfo, hostpart = hostpart.rsplit("@", 1)

    decoded_host = _try_decode_base64(hostpart)
    if decoded_host is None:
        return url

    netloc = f"{userinfo}@{decoded_host}" if userinfo else decoded_host
    return url._replace(netloc=netloc)


def _try_decode_base64(value: str) -> str | None:
    for decoder in (base64_raw_std_decode, base64_raw_url_decode):
        try:
            return decoder(value)
        except (binascii.Error, UnicodeDecodeError, ValueError):
            continue
    return None


def _query_first(query: dict[str, list[str]], key: str) -> str:
    values = query.get(key)
    if not values:
        return ""
    return values[0]


def _port_from_url(url: urlparse.ParseResult) -> int | None:
    try:
        return url.port
    except ValueError as exc:
        raise ParseError(f"v share link: invalid port: {exc}") from exc


def _get_typed(source: dict[str, object], key: str, typ: type[T]) -> T | None:
    value = source.get(key)
    if isinstance(value, typ):
        return value
    return None


def _parse_xhttp_extra(extra: dict[str, object]) -> dict[str, object]:
    opts: dict[str, object] = {}

    no_grpc_header = extra.get("noGRPCHeader")
    if isinstance(no_grpc_header, bool) and no_grpc_header:
        opts["no_grpc_header"] = True

    x_padding_bytes = extra.get("xPaddingBytes")
    if isinstance(x_padding_bytes, str) and x_padding_bytes:
        opts["x_padding_bytes"] = x_padding_bytes

    xmux = extra.get("xmux")
    if isinstance(xmux, dict):
        reuse_settings = _xmux_to_reuse_settings(xmux)
        if reuse_settings is not None:
            opts["reuse_settings"] = reuse_settings

    download_settings = extra.get("downloadSettings")
    if isinstance(download_settings, dict):
        parsed_download_settings = _parse_xhttp_download_settings(download_settings)
        if parsed_download_settings is not None:
            opts["download_settings"] = parsed_download_settings

    return opts


def _xmux_to_reuse_settings(xmux: dict[str, object]) -> XhttpReuseSettings | None:
    kwargs: dict[str, object] = {}
    mapping = {
        "maxConnections": "max_connections",
        "maxConcurrency": "max_concurrency",
        "cMaxReuseTimes": "c_max_reuse_times",
        "hMaxRequestTimes": "h_max_request_times",
        "hMaxReusableSecs": "h_max_reusable_secs",
    }

    for source, target in mapping.items():
        value = xmux.get(source)
        if isinstance(value, str) and value:
            kwargs[target] = value
        elif isinstance(value, (int, float)):
            kwargs[target] = str(int(value))

    if not kwargs:
        return None
    return XhttpReuseSettings.model_validate(kwargs)


def _parse_xhttp_download_settings(
    download_settings: dict[str, object],
) -> XhttpDownloadSettings | None:
    kwargs: dict[str, object] = {}

    address = download_settings.get("address")
    if isinstance(address, str) and address:
        kwargs["server"] = address

    port = download_settings.get("port")
    if isinstance(port, (int, float)):
        kwargs["port"] = int(port)

    security = download_settings.get("security")
    if isinstance(security, str) and security.lower() == "tls":
        kwargs["tls"] = True

    tls_settings = download_settings.get("tlsSettings")
    if isinstance(tls_settings, dict):
        server_name = tls_settings.get("serverName")
        if isinstance(server_name, str) and server_name:
            kwargs["servername"] = server_name

        fingerprint = tls_settings.get("fingerprint")
        if isinstance(fingerprint, str) and fingerprint:
            kwargs["client_fingerprint"] = fingerprint

        alpn = tls_settings.get("alpn")
        if isinstance(alpn, list):
            alpn_list = [item for item in alpn if isinstance(item, str)]
            if alpn_list:
                kwargs["alpn"] = alpn_list

    xhttp_settings = download_settings.get("xhttpSettings")
    if isinstance(xhttp_settings, dict):
        path = xhttp_settings.get("path")
        if isinstance(path, str) and path:
            kwargs["path"] = path

        host = xhttp_settings.get("host")
        if isinstance(host, str) and host:
            kwargs["host"] = host

        no_grpc_header = xhttp_settings.get("noGRPCHeader")
        if isinstance(no_grpc_header, bool) and no_grpc_header:
            kwargs["no_grpc_header"] = True

        x_padding_bytes = xhttp_settings.get("xPaddingBytes")
        if isinstance(x_padding_bytes, str) and x_padding_bytes:
            kwargs["x_padding_bytes"] = x_padding_bytes

        extra = xhttp_settings.get("extra")
        if isinstance(extra, dict):
            xmux = extra.get("xmux")
            if isinstance(xmux, dict):
                reuse_settings = _xmux_to_reuse_settings(xmux)
                if reuse_settings is not None:
                    kwargs["reuse_settings"] = reuse_settings

    if not kwargs:
        return None
    return XhttpDownloadSettings.model_validate(kwargs)
