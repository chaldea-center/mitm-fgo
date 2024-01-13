import base64
import datetime
import hashlib
import re
from enum import StrEnum
from pathlib import Path
from urllib.parse import urlparse

import orjson
from mitmproxy import http


class Region(StrEnum):
    JP = "JP"
    CN_Android = "CN_Android"
    CN_iOS = "CN_iOS"
    CN_qudao = "CN_qudao"
    TW = "TW"
    NA = "NA"
    KR = "KR"


CN_REGIONS = [Region.CN_Android, Region.CN_iOS, Region.CN_qudao]
CN_TW_REGIONS = CN_REGIONS + [Region.TW]


def fmt_date(timestamp=None):
    dt = (
        datetime.datetime.fromtimestamp(timestamp)
        if timestamp
        else datetime.datetime.now()
    )
    return dt.strftime(f"%Y%m%d_%H%M%S")


def save_response(content: bytes, region: Region, key: str):
    project_root = Path(__file__).resolve().parents[1]
    folder = project_root / "dump" / key
    filename = f"{key}_{region.value}_{fmt_date()}.json"
    fp = folder / filename
    folder.mkdir(parents=True, exist_ok=True)
    fp.write_bytes(content)
    print(f"Saved: {fp}")


def get_region(
    flow: http.HTTPFlow, path1: str | None = None, path2: str | None = None
) -> Region | None:
    uri = urlparse(flow.request.url)
    hostname, path = uri.hostname, uri.path
    if not hostname:
        return
    if "game.fate-go.jp" in hostname:
        if not path1 or path1 in path:
            return Region.JP
    elif "game.fate-go.us" in hostname:
        if not path1 or path1 in path:
            return Region.NA
    elif re.search(r"line\d-s\d-all\.fate-go\.com\.tw", hostname):
        if not path2 or path2 in path:
            return Region.TW
    elif not path2 or path2 in path:
        if re.search(r".*-ios-fate\.bilibiligame\.net", hostname):
            return Region.CN_iOS
        elif re.search(r".*-bili-fate\.bilibiligame\.net", hostname):
            return Region.CN_Android
        elif re.search(r".*-uo-fate\.bilibiligame\.net", hostname):
            return Region.CN_Android


def calc_auth_code(params: dict, secretKey: str) -> str:
    params = dict(params)
    params.pop("authCode", None)
    keys = sorted(params.keys())
    text = "&".join(f"{k}={params[k]}" for k in keys)
    text += ":" + secretKey
    sha1_value = hashlib.sha1(text.encode()).digest()
    return base64.b64encode(sha1_value).decode()


def dump_json(obj, fp: str | Path | None = None, indent: bool = False) -> bytes:
    opt = orjson.OPT_NON_STR_KEYS
    if indent:
        opt |= orjson.OPT_INDENT_2 | orjson.OPT_APPEND_NEWLINE
    data = orjson.dumps(obj, option=opt)
    if fp:
        Path(fp).write_bytes(data)
    return data


def save_text(text: str, fp: str | Path):
    Path(fp).write_text(text, encoding="utf-8")


def read_text(fp: str | Path):
    return Path(fp).read_text("utf-8")


def makedir(p: str | Path):
    Path(p).mkdir(parents=True, exist_ok=True)
