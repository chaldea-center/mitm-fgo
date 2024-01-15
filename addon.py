"""
python 3.11
Usage: mitmweb -p 8888 -s addon.py
"""
from src.battle import BattleSetupAddOn
from src.dump_all import DumpAllAddOn
from src.masterdata import MasterDataAddOn
from src.toplogin import TopLoginAddOn

addons = [
    TopLoginAddOn(),
    BattleSetupAddOn(),
    MasterDataAddOn("gamedata"),
    DumpAllAddOn(),
]
