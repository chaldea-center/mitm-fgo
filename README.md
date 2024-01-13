# MITM-FGO

## Emulator setup

Install `Drony.apk` for global proxy and setup mitmproxy cert

For details, check [English Docs](https://docs.chaldea.center/guide/import_https/mitmproxy) | [中文文档](https://docs.chaldea.center/zh/guide/import_https/mitmproxy)

## Dump login data only

1. Use bundled mitmdump.exe or download from [mitmproxy.org](https://mitmproxy.org/) or install via pip
2. on Windows, double click to open `start.cmd`
   > or running `mitmdump -p 8888 -s fgoaddon.py`

## Fully Support

0. Delete mitm\*.exe under root folder, install it via pip
1. Install Python 3.11 or create a virtual env
2. `pip install -r requirements`
   > set proxy if github is blocked
3. Copy `.env.example` and rename to `.env`, change your secret_key if needed
4. `mitmweb -p 8888 -s addon.py`
