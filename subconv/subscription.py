import re

import yaml

from .converter import ConvertsV2Ray


async def parseSubs(content: str) -> str:
    try:
        loaded = yaml.load(content, Loader=yaml.FullLoader)
        if not isinstance(loaded, dict):
            raise ValueError("subscription content is not a mapping")

        proxies_value = loaded.get("proxies")
        if not isinstance(proxies_value, list):
            raise ValueError("subscription content missing proxies list")

        proxies = yaml.safe_dump(
            {"proxies": proxies_value}, allow_unicode=True, sort_keys=False
        )
    except Exception:
        proxies = yaml.safe_dump(
            {"proxies": await ConvertsV2Ray(content)},
            allow_unicode=True,
            sort_keys=False,
        )
    return proxies


async def mkListProxyNames(content: list[str] | None) -> list[str]:
    providerProxyNames: list[str] = []
    if content:
        for u in content:
            contentTmp = re.findall(r"- name: (.+)", u)
            providerProxyNames.extend(contentTmp)
    return providerProxyNames
