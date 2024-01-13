import base64

from mitmproxy import http

from .common import CN_TW_REGIONS, get_region, save_response


class TopLoginAddOn:
    def response(self, flow: http.HTTPFlow) -> None:
        if get_region(flow):
            print(flow.request.url)
        region = get_region(flow, "/login/top", "_key=toplogin")
        if not region:
            return
        print(f"Saving {region}: ", flow.request.url)
        assert flow.response
        content = flow.response.content
        assert content
        if region in CN_TW_REGIONS and content.startswith(b"ey"):
            content = base64.urlsafe_b64decode(content)
        save_response(content, region, "toplogin")
