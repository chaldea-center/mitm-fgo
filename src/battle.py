import base64
import json
from typing import Literal

from mitmproxy import http

from .common import CN_TW_REGIONS, get_region, save_response

UserSvtType = Literal[
    "userSvt", "myUserSvt", "myUserSvtEquip", "enemyUserSvt", "transformUserSvt"
]


class BattleSetupAddOn:
    def response(self, flow: http.HTTPFlow) -> None:
        region = get_region(flow, "/battle/setup", "_key=battlesetup")
        if not region:
            return
        assert flow.response
        content = flow.response.content
        assert content
        use_b64 = region in CN_TW_REGIONS and content.startswith(b"ey")
        if use_b64:
            content = base64.urlsafe_b64decode(content)
        save_response(content, region, "toplogin")
        data = json.loads(content)
        # start
        # edit_svt(get_svt(data, "userSvt", 100100, 1), "skillId1", 11111)
        # add_add_passive(get_svt(data, "userSvt", 100100, 1), 1001212, 10)
        # add_class_passive(get_svt(data, "userSvt", 100100, 1), 1001212)
        # end
        response_data = json.dumps(data, ensure_ascii=False).encode()
        if use_b64:
            response_data = base64.urlsafe_b64encode(response_data)
        flow.response.data.content = response_data


def get_svt(data: dict, usr_svt_type: UserSvtType, svt_id: int, svt_idx: int):
    """
    svt_idx: start from 1
    """
    battle_info = data["cache"]["replaced"]["battle"][0]["battleInfo"]
    svt_list: list[dict] = battle_info[usr_svt_type]
    svts = [svt for svt in svt_list if int(svt["svtId"]) == svt_id]
    if len(svts) < svt_idx:
        print(f"Total {len(svts)} No.{svt_id} {usr_svt_type}, {svt_idx} out of range")
        return
    svt = svts[svt_idx - 1]
    print(f"Get svt {usr_svt_type}-{svt_id}-{svt_idx}")
    return svt


def edit_svt(svt, key: str, value):
    if not svt:
        return
    if key not in svt:
        print(f'Key "{key}" not in data')
        return
    src_value = svt[key]
    if isinstance(src_value, int):
        svt[key] = int(value)
    elif isinstance(src_value, str):
        svt[key] = str(value)
    else:
        svt[key] = value
    print(f"Change {key} from {src_value} to {value}")


def add_add_passive(svt, skill_id: int, lv: int = 1):
    if not svt:
        return
    svt["addPassive"].append(skill_id)
    if "addPassiveLvs" in svt:
        svt["addPassiveLvs"].append(lv)


def add_class_passive(svt, skill_id: int):
    if not svt:
        return
    svt["classPassive"].append(skill_id)
