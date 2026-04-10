# What is SubConv?

Welcome to the knowledge base of SubConv.

[SubConv](https://github.com/SubConv/SubConv) is a mihomo-oriented configuration generator and subscription converter. It can turn subscriptions and share links in multiple formats into a mihomo-compatible config.

It's user-friendly and easy to use.  

It is easy to deploy on [Vercel](https://vercel.com), with Docker, or on your own VPS.

We provide configuration files for general users and ZJU users.

## Screenshots

![screenshot](/assets/screenshot.png)

## Features

- Support Clash YAML subscriptions and V2Ray-style base64 links (the original subscription does not have to be Clash YAML)
- A Web-UI (thanks to [@Musanico](https://github.com/musanico))
- Rules based on ACL
- Nodes auto update based on proxy-provider
- Rules auto update based on rule-provider
- Support proxy rule-provider to prevent failure to get rules from GitHub
- Support multiple airpots
- Display remaining traffic and total traffic (only useful when you use a single airport, requires your airport and Clash to support it at the same time, Clash for Windows, Clash Verge, Stash, Clash Meta for Android, etc. are known to support it)
- Expose an API that converts subscriptions into proxy-provider output
- Support configuration file
