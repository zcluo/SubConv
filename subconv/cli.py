#!/usr/bin/env python3

import argparse
import sys

from . import config_template


def main():
    class GenerateConfigAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            import yaml

            yaml.SafeDumper.ignore_aliases = lambda self, data: True
            if values == "default":
                with open("config.yaml", "w", encoding="utf-8") as f:
                    f.write(
                        yaml.safe_dump(
                            config_template.template_default,
                            allow_unicode=True,
                            sort_keys=False,
                        )
                    )
            elif values == "zju":
                with open("config.yaml", "w", encoding="utf-8") as f:
                    f.write(
                        yaml.safe_dump(
                            config_template.template_zju,
                            allow_unicode=True,
                            sort_keys=False,
                        )
                    )
            parser.exit()

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--port", "-P", type=int, default=8080, help="port of the api, default: 8080"
    )
    parser.add_argument(
        "--host",
        "-H",
        type=str,
        default="0.0.0.0",
        help="host of the api, default: 0.0.0.0",
    )
    parser.add_argument("--version", "-V", action="version", version="version: v2.0.0")
    parser.add_argument(
        "--generate-config",
        "-G",
        type=str,
        choices=("default", "zju"),
        action=GenerateConfigAction,
        help="generate a default config file",
    )
    args = parser.parse_args()

    from . import config

    import uvicorn
    import os

    DISALLOW_ROBOTS = bool(eval(os.environ.get("DISALLOW_ROBOTS", "False")))

    print("host:", args.host)
    print("port:", args.port)
    if DISALLOW_ROBOTS:
        print("robots: Disallow")
    else:
        print("robots: Allow")
    uvicorn.run(
        "subconv.app:app",
        host=args.host,
        port=args.port,
        workers=4,
        proxy_headers=True,
        forwarded_allow_ips="*",
    )
