# 什么是 SubConv

欢迎来到 SubConv 的知识库。

[SubConv](https://github.com/SubConv/SubConv) 是一个面向 mihomo 的配置生成器，同时也是一个订阅转换器。它可以将多种格式的订阅和分享链接转换为兼容 mihomo 的配置。

它易于使用。  

它易于部署，可以部署在 [Vercel](https://vercel.com)、Docker 或您自己的 VPS 上。

我们提供了一般用户的配置文件和ZJU配置文件

## 截图

![screenshot](/assets/screenshot.png)

## 特性

- 支持 Clash YAML 订阅和 V2Ray 风格的 base64 链接（即原始订阅不一定是 Clash YAML）
- 自带 Web-UI (感谢 [@Musanico](https://github.com/musanico))
- 大体基于 ACL 的规则
- 基于 proxy-provider 的节点自动更新
- 基于 rule-provider 的规则自动更新
- 支持代理 rule-provider 防止无法从 GitHub 获取规则集
- 多机场用户提供了支持
- 剩余流量和总流量的显示（单机场的时候才有用，需要你的机场和你用的Clash同时支持，已知Clash for Windows, Clash Verge, Stash, Clash Meta for Android等已支持）
- 提供了将订阅转换为 proxy-provider 输出的 API
- 支持配置文件
