# 使用 Docker 部署

首先请确保你已经安装了 Docker 和 Docker Compose。

## 步骤

1. 在服务器上克隆本仓库：

    ```bash
    git clone --depth=1 https://github.com/SubConv/SubConv.git
    cd SubConv
    ```

2. 运行 `cp config.yaml.example config.yaml` 创建运行时配置文件（`docker-compose.yml` 需要此文件）。

3. 将运行时改动写入 `config.yaml`，再按需修改 `template/zju.yaml` 或 `template/general.yaml`。容器会使用 `DEFAULT_TEMPLATE` 指定的模板，默认值是 `zju`。

4. 如果你想修改对外端口或配置/模板挂载路径，可以查看仓库自带的 `docker-compose.yml`。默认会挂载 `./config.yaml:/app/config.yaml` 和 `./template:/app/template`，所以在运行 `docker compose up` 之前必须先准备好 `config.yaml`。

5. 运行 `docker compose up -d` 来启动服务。
6. 尽情享受吧
