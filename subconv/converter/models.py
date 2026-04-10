"""Shared Pydantic models for transport layers, TLS, and Reality options.

Field names use aliases to match mihomo's proxy struct tags exactly.
Each model provides ``to_dict()`` that strips ``None`` values and
outputs hyphenated keys compatible with mihomo YAML.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class MihomoBaseModel(BaseModel):
    """Shared Pydantic config for mihomo-aligned models."""

    model_config = ConfigDict(populate_by_name=True)


class _StripNoneMixin(MihomoBaseModel):
    """Base mixin that strips ``None`` values from ``to_dict()`` output."""

    def to_dict(self) -> dict[str, object]:
        return self.model_dump(by_alias=True, exclude_none=True)


class HttpOpts(_StripNoneMixin):
    method: str | None = Field(None, alias="method")
    path: list[str] | None = Field(None, alias="path")
    headers: dict[str, list[str]] | None = Field(None, alias="headers")


class H2Opts(_StripNoneMixin):
    host: list[str] | None = Field(None, alias="host")
    path: str | list[str] | None = Field(None, alias="path")
    headers: dict[str, list[str]] | None = Field(None, alias="headers")


class GrpcOpts(_StripNoneMixin):
    grpc_service_name: str | None = Field(None, alias="grpc-service-name")
    grpc_user_agent: str | None = Field(None, alias="grpc-user-agent")


class WsOpts(_StripNoneMixin):
    path: str | None = Field(None, alias="path")
    headers: dict[str, str] | None = Field(None, alias="headers")
    max_early_data: int | None = Field(None, alias="max-early-data")
    early_data_header_name: str | None = Field(None, alias="early-data-header-name")
    v2ray_http_upgrade: bool | None = Field(None, alias="v2ray-http-upgrade")
    v2ray_http_upgrade_fast_open: bool | None = Field(
        None, alias="v2ray-http-upgrade-fast-open"
    )


class XhttpReuseSettings(_StripNoneMixin):
    max_connections: str | None = Field(None, alias="max-connections")
    max_concurrency: str | None = Field(None, alias="max-concurrency")
    c_max_reuse_times: str | None = Field(None, alias="c-max-reuse-times")
    h_max_request_times: str | None = Field(None, alias="h-max-request-times")
    h_max_reusable_secs: str | None = Field(None, alias="h-max-reusable-secs")


class XhttpDownloadSettings(_StripNoneMixin):
    path: str | None = Field(None, alias="path")
    host: str | None = Field(None, alias="host")
    no_grpc_header: bool | None = Field(None, alias="no-grpc-header")
    x_padding_bytes: str | None = Field(None, alias="x-padding-bytes")
    reuse_settings: XhttpReuseSettings | None = Field(None, alias="reuse-settings")
    server: str | None = Field(None, alias="server")
    port: int | None = Field(None, alias="port")
    tls: bool | None = Field(None, alias="tls")
    servername: str | None = Field(None, alias="servername")
    client_fingerprint: str | None = Field(None, alias="client-fingerprint")
    alpn: list[str] | None = Field(None, alias="alpn")


class XhttpOpts(_StripNoneMixin):
    path: str | None = Field(None, alias="path")
    host: str | None = Field(None, alias="host")
    mode: str | None = Field(None, alias="mode")
    headers: dict[str, str] | None = Field(None, alias="headers")
    no_grpc_header: bool | None = Field(None, alias="no-grpc-header")
    x_padding_bytes: str | None = Field(None, alias="x-padding-bytes")
    sc_max_each_post_bytes: int | None = Field(None, alias="sc-max-each-post-bytes")
    reuse_settings: XhttpReuseSettings | None = Field(None, alias="reuse-settings")
    download_settings: XhttpDownloadSettings | None = Field(
        None, alias="download-settings"
    )


class RealityOpts(_StripNoneMixin):
    public_key: str = Field(alias="public-key")
    short_id: str | None = Field(None, alias="short-id")


class ECHOpts(_StripNoneMixin):
    enable: bool | None = Field(None, alias="enable")
    config: str | None = Field(None, alias="config")
    query_server_name: str | None = Field(None, alias="query-server-name")
