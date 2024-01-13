import base64
import zlib
from pathlib import Path

import msgpack
import orjson

# from py3rijndael import Pkcs7Padding, RijndaelCbc
from cppdael import MODE_CBC, Pkcs7Padding, decrypt_unpad, pad_encrypt
from mitmproxy import http

from .common import Region, calc_auth_code, dump_json, makedir, read_text, save_text


class MasterDataAddOn:
    def __init__(self, gamedata_folder: str | Path) -> None:
        self.gamedata_folder = Path(gamedata_folder)

    def get_bin_and_folder(self, region: Region) -> tuple[Path, Path]:
        folder = self.gamedata_folder / region
        return folder / "master.bin", folder / "master"

    def request(self, flow: http.HTTPFlow):
        url = flow.request.url

        if "game.fate-go.jp/gamedata/top" in url:
            from .config import settings

            your_secretKey = settings.jp_secretKey
            if not your_secretKey:
                print("secretKey not provided, skip masterdata modification")
                return
            region = Region.JP
            master_bin, master_folder = self.get_bin_and_folder(region)
            if master_bin.exists() and master_folder.exists():
                print("local master data exists")
                return

            form_data = flow.request.urlencoded_form
            form_data_dict = {k: form_data.get(k) for k in form_data.keys()}
            dataVer = form_data_dict.get("dataVer")
            authCode = form_data_dict.pop("authCode", None)
            if not dataVer:
                print("dataVer not in params, skip")
                return
            new_dataVer = str(int(dataVer) - 1)
            new_authCode = calc_auth_code(form_data_dict, your_secretKey)
            print(f"changing: dataVer {dataVer}->{new_dataVer}")
            print(f"changing: authCode {authCode}->{new_authCode}")
            flow.request.urlencoded_form["dataVer"] = new_dataVer
            flow.request.urlencoded_form["authCode"] = new_authCode
        else:
            return

    def response(self, flow: http.HTTPFlow):
        url = flow.request.url
        response = flow.response
        if "fate-go.jp" in url:
            print(url)
        if not response:
            return

        # gamedata/top
        if "masterdata-update.fate-go.jp/AWS.release/" in url:
            region = Region.JP
            master_bin, master_folder = self.get_bin_and_folder(region)
            makedir(master_folder)

            key = b"pX6q6xK2UymhFKcaGHHUlfXqfTsWF0uH"
            # na_key = b"6OScqiI59EU3WM8U1TDYCHyKnKbQvoyE"
            resp_data = response.json()
            if master_bin.exists() and master_folder.exists():
                local_data: dict = {}
                for fp in master_folder.glob("*.json"):
                    name = fp.name[:-5]
                    mst_items = orjson.loads(fp.read_bytes())
                    local_data[name] = mst_items
                if local_data:
                    local_master = read_text(master_bin)
                    iv = get_master_iv(local_master)
                    final_master = encrypt_masterdata(key, iv, local_data)
                    resp_data["response"][0]["success"]["master"] = final_master
                    response.set_content(dump_json(resp_data))
                    print("loaded local masterdata")
            else:
                master: str = resp_data["response"][0]["success"]["master"]
                save_text(master, master_bin)
                iv, masterdata = decrypt_masterdata(key, master)
                for k, v in masterdata.items():
                    dump_json(v, master_folder / f"{k}.json", indent=True)
                print(f"saved masterdata to {master_folder}")
        else:
            return
        assert flow.response


def get_master_iv(master: str) -> bytes:
    return base64.b64decode(master)[:32]


# jp/na: base64 -> decrypt -> unzip -> msgpack
def decrypt_masterdata(key: bytes, master: str) -> tuple[bytes, dict]:
    masterbundle = base64.b64decode(master)

    iv = masterbundle[:32]
    data = masterbundle[32:]
    decrypted = decrypt_unpad(MODE_CBC, 32, key, iv, data, Pkcs7Padding(32))
    # rijndael_cbc = RijndaelCbc(key=key, iv=iv, padding=Pkcs7Padding(32), block_size=32)
    # decrypted = rijndael_cbc.decrypt(data)
    unzip = zlib.decompress(decrypted, wbits=zlib.MAX_WBITS | 16)
    master_dict: dict = msgpack.unpackb(unzip)
    return iv, master_dict


def encrypt_masterdata(key: bytes, iv: bytes, master_dict: dict) -> str:
    packed = msgpack.packb(master_dict)
    assert isinstance(packed, bytes)
    compressed = zlib.compress(packed, wbits=zlib.MAX_WBITS | 16)
    encrypted = pad_encrypt(MODE_CBC, 32, key, iv, compressed, Pkcs7Padding(32))
    # rijndael_cbc = RijndaelCbc(key=key, iv=iv, padding=Pkcs7Padding(32), block_size=32)
    # encrypted = rijndael_cbc.encrypt(compressed)
    return base64.b64encode(iv + encrypted).decode()
