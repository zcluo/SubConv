# Deploy with Docker

First make sure you have installed Docker and Docker Compose.

## Steps

1. Clone this repository on your server:

    ```bash
    git clone --depth=1 https://github.com/SubConv/SubConv.git
    cd SubConv
    ```

2. Run `cp config.yaml.example config.yaml` to create the runtime config file (required by `docker-compose.yml`).

3. Put your runtime changes in `config.yaml`, then adjust `template/zju.yaml` or `template/general.yaml` as needed. The container uses the template named by `DEFAULT_TEMPLATE`, which is `zju` by default.

4. Review the bundled `docker-compose.yml` if you want to change the published port or the mounted config/template paths. By default it mounts `./config.yaml:/app/config.yaml` and `./template:/app/template`, so `config.yaml` must exist before you run `docker compose up`.

5. Run `docker compose up -d` to start the service.
6. Enjoy
