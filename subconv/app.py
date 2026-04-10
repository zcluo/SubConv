import os
import re

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.requests import Request
from fastapi.responses import FileResponse, Response, StreamingResponse
from fastapi.staticfiles import StaticFiles
from urllib.parse import urlencode

from . import config
from . import packer
from . import subscription
from .converter import ConvertsV2Ray

DISALLOW_ROBOTS = bool(eval(os.environ.get("DISALLOW_ROBOTS", "False")))

app = FastAPI()

STATIC_DIR = "mainpage/dist"
if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def mainpage():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.isfile(index_path):
        return FileResponse(index_path)
    return Response(status_code=404)


@app.get("/robots.txt")
async def robots():
    if DISALLOW_ROBOTS:
        return Response(content="User-agent: *\nDisallow: /", media_type="text/plain")
    return Response(status_code=404)


@app.get("/provider")
async def provider(request: Request):
    headers = {"Content-Type": "text/yaml;charset=utf-8"}
    url = request.query_params.get("url")
    if url is None:
        raise HTTPException(
            status_code=400, detail="Missing required query parameter: url"
        )

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers={"User-Agent": "v2rayn"})
        if resp.status_code < 200 or resp.status_code >= 400:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        result = await subscription.parseSubs(resp.text)
    return Response(content=result, headers=headers)


@app.get("/sub")
async def sub(request: Request):
    args = request.query_params
    interval = args.get("interval", "1800")
    short = args.get("short")
    notproxyrule = args.get("npr")

    url_param = args.get("url")
    if url_param is None:
        raise HTTPException(
            status_code=400, detail="Missing required query parameter: url"
        )

    url, urlstandalone_raw = _split_sources(url_param)

    urlstandby_param = args.get("urlstandby")
    urlstandby: list[str] | None = None
    urlstandbystandalone_raw: str | None = None
    if urlstandby_param:
        urlstandby, urlstandbystandalone_raw = _split_sources(urlstandby_param)

    urlstandalone = (
        await ConvertsV2Ray(urlstandalone_raw) if urlstandalone_raw else None
    )
    urlstandbystandalone = (
        await ConvertsV2Ray(urlstandbystandalone_raw)
        if urlstandbystandalone_raw
        else None
    )

    user_agent = request.headers.get("User-Agent", "v2rayn")

    async with httpx.AsyncClient() as client:
        headers = {"Content-Type": "text/yaml;charset=utf-8"}
        if url is not None and len(url) == 1:
            resp = await client.head(url[0], headers={"User-Agent": user_agent})
            if resp.status_code < 200 or resp.status_code >= 400:
                raise HTTPException(status_code=resp.status_code, detail=resp.text)
            elif resp.status_code >= 300 and resp.status_code < 400:
                while resp.status_code >= 300 and resp.status_code < 400:
                    url[0] = resp.headers["Location"]
                    resp = await client.head(url[0], headers={"User-Agent": user_agent})
                    if resp.status_code < 200 or resp.status_code >= 400:
                        raise HTTPException(
                            status_code=resp.status_code, detail=resp.text
                        )
            originalHeaders = resp.headers
            if "subscription-userinfo" in originalHeaders:
                headers["subscription-userinfo"] = originalHeaders[
                    "subscription-userinfo"
                ]
            if "Content-Disposition" in originalHeaders:
                headers["Content-Disposition"] = originalHeaders[
                    "Content-Disposition"
                ].replace("attachment", "inline")

        content: list[str] | None = []
        if url is not None:
            for i in range(len(url)):
                respText = (
                    await client.get(url[i], headers={"User-Agent": "v2rayn"})
                ).text
                content.append(await subscription.parseSubs(respText))
                url[i] = "{}provider?{}".format(
                    str(request.base_url), urlencode({"url": url[i]})
                )
    if content is not None and len(content) == 0:
        content = None
    if urlstandby:
        for i in range(len(urlstandby)):
            urlstandby[i] = "{}provider?{}".format(
                str(request.base_url), urlencode({"url": urlstandby[i]})
            )

    hostname = request.url.hostname
    if hostname is None:
        raise HTTPException(status_code=400, detail="Unable to determine request host")

    match = re.search(r"([^:]+)(:\d{1,5})?", hostname)
    if match is None:
        raise HTTPException(status_code=400, detail="Unable to parse request host")

    domain = match.group(1)
    result = await packer.pack(
        url=url,
        urlstandalone=urlstandalone,
        urlstandby=urlstandby,
        urlstandbystandalone=urlstandbystandalone,
        content=content,
        interval=interval,
        domain=domain,
        short=short,
        notproxyrule=notproxyrule,
        base_url=str(request.base_url),
    )
    return Response(content=result, headers=headers)


@app.get("/proxy")
async def proxy(request: Request, url: str):
    is_whitelisted = False
    for rule in config.configInstance.RULESET:
        if rule[1] == url:
            is_whitelisted = True
            break
    if not is_whitelisted:
        raise HTTPException(status_code=403, detail="Forbidden: URL not in whitelist")

    user_agent = request.headers.get("User-Agent", "v2rayn")
    client = httpx.AsyncClient()
    response = await client.send(
        client.build_request("GET", url, headers={"User-Agent": user_agent}),
        stream=True,
    )

    if response.status_code < 200 or response.status_code >= 400:
        body = await response.aread()
        await response.aclose()
        await client.aclose()
        raise HTTPException(
            status_code=response.status_code,
            detail=body.decode("utf-8", errors="ignore"),
        )

    async def stream_body():
        try:
            async for chunk in response.aiter_bytes():
                yield chunk
        finally:
            await response.aclose()
            await client.aclose()

    content_type = response.headers.get("Content-Type")
    return StreamingResponse(stream_body(), media_type=content_type)


@app.get("/{path:path}")
async def index(path: str):
    static_path = os.path.join(STATIC_DIR, path)
    if os.path.isfile(static_path):
        return FileResponse(static_path)
    raise HTTPException(status_code=404, detail="Not Found")


def _split_sources(source: str) -> tuple[list[str] | None, str | None]:
    remote_urls: list[str] = []
    standalone_urls: list[str] = []

    for item in filter(None, re.split(r"[|\n]", source)):
        if (
            item.startswith("http://") or item.startswith("https://")
        ) and not item.startswith("https://t.me/"):
            remote_urls.append(item)
        else:
            standalone_urls.append(item)

    standalone = "\n".join(standalone_urls) or None
    return (remote_urls or None, standalone)
