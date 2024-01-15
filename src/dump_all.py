import re
from pathlib import Path
from urllib.parse import urlparse

import orjson
from mitmproxy import http

from .common import fmt_date


class DumpAllAddOn:
    def response(self, flow: http.HTTPFlow):
        if not flow.response:
            return
        uri = urlparse(flow.request.url)
        if "game.fate-go.jp" != uri.hostname:
            return
        print("dump_all", uri.geturl())
        if uri.path.startswith("/gamedata/"):
            return
        user_id = re.search(r"_userId=(\d+)", uri.query)
        if not user_id:
            return
        user_id = int(user_id.group(1))
        nid = uri.path.strip("/").replace("/", "_")
        prefix = f"dump/{user_id}/{nid}/{nid}_{fmt_date(flow.response.timestamp_start)}"

        _req_body = dict(flow.request.urlencoded_form)
        _req_body = _req_body or flow.request.get_text(strict=False)

        request_data = {
            "url": flow.request.url,
            "method": flow.request.method,
            "headers": dict(flow.request.headers),
            "data": _req_body,
        }

        try:
            _resp_body = flow.response.json()
        except:
            _resp_body = flow.response.get_text(strict=False)
        response_data = {
            "url": flow.request.url,
            "headers": dict(flow.response.headers),
            "data": _resp_body,
        }
        req_fp = Path(prefix + "_request.json")
        resp_fp = Path(prefix + "_response.json")
        req_fp.parent.mkdir(parents=True, exist_ok=True)
        req_fp.write_bytes(
            orjson.dumps(
                request_data, option=orjson.OPT_INDENT_2 | orjson.OPT_APPEND_NEWLINE
            )
        )
        resp_fp.write_bytes(orjson.dumps(response_data))
        print(f"Saved: {prefix}")
