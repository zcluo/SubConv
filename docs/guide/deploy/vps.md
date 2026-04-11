# Deploy on VPS or PC (Binary)
Here I suppose you're using Linux server (Windows is similar).  

## Steps
1. Download the latest version from the [Releases](https://github.com/SubConv/SubConv/releases) page and extract it to your machine, for example `/opt/subconv`. Keep the extracted `api` executable, `mainpage/dist`, `config.yaml.example`, and `template/` directory together so the Web UI and runtime templates are available.
2. `cd /opt/subconv` to enter the directory
3. `chmod +x api` to give it execution permission
4. Put machine-specific runtime changes in `config.yaml`, then adjust `template/zju.yaml` or `template/general.yaml` as needed. The service uses `DEFAULT_TEMPLATE`, which is `zju` by default. `HOST` and `PORT` also come from `config.yaml`. For detailed template items, please refer to [Configuration](../configuration/overview)
5. Run the program.
   > ***Note***: If you're not using a privileged user, you usually can't bind to a port below 1024. It's recommended to use a high port in `config.yaml`, or you can use `setcap` to give the `api` binary the permission to bind to a low port.
6. Use reverse proxy (optional)

## Enjoy
