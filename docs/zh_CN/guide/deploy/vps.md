# 在 VPS 或 PC 上部署（二进制文件）
这里我假设你使用的是 Linux 服务器（Windows类似）。  

## 步骤
1. 从 [Releases](https://github.com/SubConv/SubConv/releases) 页面下载对应系统的最新版本，然后解压到机器上，假设解压到了 `/opt/subconv`。请保持解压后的 `api` 可执行文件、`mainpage/dist`、`config.yaml.example` 和 `template/` 目录在一起，这样 Web UI 和运行时模板都能正常工作。
2. `cd /opt/subconv` 进入目录
3. `chmod +x api` 来给予执行权限
4. 如果需要机器专用运行时配置，请把改动写进 `config.yaml`，然后按需修改 `template/zju.yaml` 或 `template/general.yaml`。服务使用 `DEFAULT_TEMPLATE` 指定的模板，默认值为 `zju`。`HOST` 和 `PORT` 也来自 `config.yaml`。详细模板项可参考 [配置](../configuration/overview)
5. 运行程序。
    > ***注意***：如果你不是使用特权用户，通常你是不能绑定 1024 以下的端口的。推荐直接在 `config.yaml` 中使用高端口，或者你也可以使用 `setcap` 来给 `api` 可执行文件绑定低端口的权限。
6. 使用反向代理（可选）

## 尽情享受吧
