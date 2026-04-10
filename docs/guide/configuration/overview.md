# Configuration

The configuration of this program uses the YAML file format. The configuration file is `config.yaml`, located in the root directory of the program. An example can be found at [config.yaml](https://github.com/SubConv/SubConv/blob/main/config.yaml).

If you are running from a source checkout, you can generate the default configuration file with `uv run python api.py -G default > config.yaml`. If you need the ZJU configuration file, use `uv run python api.py -G zju > config.yaml`.

If you are running a released binary, you can use `./api -G default > config.yaml` or `./api -G zju > config.yaml` instead.

## Configuration Items

- `HEAD`: Configuration before the node information, such as
    ```yaml
    HEAD:
      mixed-port: 7890
      allow-lan: true
      mode: rule
      log-level: info
      external-controller: :9090
      dns:
        enable: true
        listen: 0.0.0.0:1053
        default-nameserver:
        - 223.5.5.5
        - 8.8.8.8
        - 1.1.1.1
        nameserver-policy:
          geosite:gfw,geolocation-!cn:
          - https://1.1.1.1/dns-query
          - https://1.0.0.1/dns-query
          - https://8.8.8.8/dns-query
        nameserver:
        - https://223.5.5.5/dns-query
        - https://1.12.12.12/dns-query
        - https://8.8.8.8/dns-query
        fallback:
        - https://1.1.1.1/dns-query
        - https://8.8.8.8/dns-query
        fallback-filter:
          geoip: false
          geoip-code: CN
          ipcidr:
          - 240.0.0.0/4
        fake-ip-filter:
        - +.lan
        - +.microsoft*.com
        - localhost.ptlogin2.qq.com
    ```
- `TEST_URL`: The URL of the test node, such as
    ```yaml
    TEST_URL: https://www.gstatic.com/generate_204
    ```
- `RULESET`: Rule set, refer to [Rule Set](./rule-set)
- `CUSTOM_PROXY_GROUP` Custom proxy group, refer to [Proxy Groups](./proxy-groups)
