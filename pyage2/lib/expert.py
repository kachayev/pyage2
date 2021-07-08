# Copyright 2021 PyAge2, Oleksii Kachaiev <kachayev@gmail.com>. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Client to communicate with AI Module gRPC server."""

from google.protobuf.any_pb2 import Any
import grpc
from typing import Any as AnyType, List, Tuple

import pyage2.protos.expert.expert_api_pb2_grpc as expert_grpc
import pyage2.protos.expert.expert_api_pb2 as expert

Actions = List[AnyType]

def _unpack(result, result_type):
    unpacked_result = result_type()
    result.Unpack(unpacked_result)
    # xxx(okachaiev): not sure if we have any use case where type != int
    return int(unpacked_result.result)

class ExpertClient:

    def __init__(self, host: str, port: int):
        self._host = host
        self._port = port
        self._channel = grpc.insecure_channel(f"{host}:{port}")
        self._api = expert_grpc.ExpertAPIStub(self._channel)

    def __call__(self, player_id, commands):
        request = expert.CommandList()
        request.playerNumber = player_id
        any_command = Any()
        for cmd in commands:
            any_command.Pack(cmd)
            request.commands.append(any_command)
        return self._api.ExecuteCommandList(request)

    def player_facts(self, player_id, commands):
        request = [cmd for _, cmd, _ in commands]
        response_types = [(result_key, result_type) for result_key, _, result_type in commands]
        response = self(player_id, request)
        response_keys = {}
        for i, (result_key, result_type) in enumerate(response_types):
            raw_result = _unpack(response.results[i], result_type)
            # check if it's array or not
            if "." in result_key:
                result_key, _ = result_key.split(".", 1)
                if result_key in response_keys:
                    response_keys[result_key].append(raw_result)
                else:
                    # xxx(okachaiev): allocations are pretty slow,
                    # better would be to use statically defined spec
                    # to allocate arrays with proper length hint
                    response_keys[result_key] = [raw_result]
            else:
                response_keys[result_key] = raw_result
        return response_keys

    def actions(self, actions: List[Tuple[int, Actions]]):
        for player_id, player_actions in actions:
            player_actions = list(filter(None, player_actions))
            if player_actions:
                self(player_id, player_actions)

    def close(self):
        if self._channel is not None:
            self._channel.close()
            self._channel = None

# xxx(okachaiev): I'm not sure we need all of them
_TECHNOLOGIES = {
    "2": "Elite Tarkan",
    "3": "Yeomen",
    "4": "El Dorado",
    "5": "Furor Celtica",
    "6": "Drill",
    "7": "Mahouts",
    "8": "Town Watch",
    "9": "Zealotry",
    "10": "Artillery",
    "11": "Crenellations",
    "12": "Crop Rotation",
    "13": "Heavy Plow",
    "14": "Horse Collar",
    "15": "Guilds",
    "16": "Anarchy",
    "17": "Banking",
    "19": "Cartography",
    "21": "Atheism",
    "22": "Loom",
    "23": "Coinage",
    "24": "Garland Wars",
    "27": "Plumed Archer",
    "34": "War Galley",
    "35": "Galleon",
    "37": "Cannon Galleon",
    "39": "Husbandry",
    "45": "Faith",
    "47": "Chemistry",
    "48": "Caravan",
    "49": "Berserkergang",
    "50": "Masonry",
    "51": "Architecture",
    "52": "Rocketry",
    "54": "Treadmill Crane",
    "55": "Gold Mining",
    "57": "Cannon Galleon",
    "59": "Kataparuto",
    "60": "Elite Conquistador",
    "61": "Logistica",
    "63": "Keep",
    "64": "Bombard Tower",
    "67": "Forging",
    "68": "Iron Casting",
    "74": "Scale Mail Armor",
    "75": "Blast Furnace",
    "76": "Chain Mail Armor",
    "77": "Plate Mail Armor",
    "80": "Plate Barding Armor",
    "81": "Scale Barding Armor",
    "82": "Chain Barding Armor",
    "83": "Bearded Axe",
    "85": "Hand Cannon",
    "90": "Tracking",
    "93": "Ballistics",
    "94": "Scorpion",
    "96": "Capped Ram",
    "98": "Elite Skirmisher",
    "100": "Crossbowman",
    "101": "Feudal Age",
    "102": "Castle Age",
    "103": "Imperial Age",
    "104": "Dark Age",
    "110": "Yes",
    "140": "Guard Tower",
    "172": "Roggan",
    "174": "Wololo",
    "175": "What Age Are You In?",
    "178": "Wait for My Signal to Attack",
    "182": "Gold Shaft Mining",
    "188": "Bombard Cannon",
    "192": "Roggan",
    "194": "Fortified Wall",
    "197": "Pikeman",
    "199": "Fletching",
    "200": "Bodkin Arrow",
    "201": "Bracer",
    "202": "Double-Bit Axe",
    "203": "Bow Saw",
    "207": "Long Swordsman",
    "209": "Cavalier",
    "211": "Padded Archer Armor",
    "212": "Leather Archer Armor",
    "213": "Wheelbarrow",
    "215": "Squires",
    "217": "Two-Handed Swordsman",
    "218": "Heavy Cav Archer",
    "219": "Ring Archer Armor",
    "221": "Two-Man Saw",
    "222": "Man-at-Arms",
    "230": "Block Printing",
    "231": "Sanctity",
    "233": "Illumination",
    "236": "Heavy Camel",
    "237": "Arbalest",
    "239": "Heavy Scorpion",
    "244": "Heavy Demolition Ship",
    "246": "Fast Fire Ship",
    "249": "Hand Cart",
    "252": "Fervor",
    "254": "Light Cavalry",
    "255": "Siege Ram",
    "257": "Onager",
    "264": "Champion",
    "265": "Paladin",
    "278": "Stone Mining",
    "279": "Stone Shaft Mining",
    "280": "Town Patrol",
    "315": "Conscription",
    "316": "Redemption",
    "317": "Logistica",
    "319": "Atonement",
    "320": "Siege Onager",
    "321": "Sappers",
    "322": "Murder Holes",
    "332": "Bearded Axe",
    "353": "Supremacy",
    "360": "Elite Longbowman",
    "361": "Elite Cataphract",
    "362": "Elite Chu Ko Nu",
    "363": "Elite Throwing Axeman",
    "364": "Elite Teutonic Knight",
    "365": "Elite Huskarl",
    "366": "Elite Samurai",
    "367": "Elite War Elephant",
    "368": "Elite Mameluke",
    "369": "Elite Janissary",
    "370": "Elite Woad Raider",
    "371": "Elite Mangudai",
    "372": "Elite Longboat",
    "373": "Shipwright",
    "374": "Careening",
    "375": "Dry Dock",
    "376": "Elite Cannon Galleon",
    "377": "Siege Engineers",
    "379": "Hoardings",
    "380": "Heated Shot",
    "398": "Elite Berserk",
    "408": "Spies/Treason",
    "428": "Hussar",
    "429": "Halberdier",
    "432": "Elite Jaguar Warrior",
    "434": "Elite Eagle Warrior",
    "435": "Bloodlines",
    "436": "Parthian Tactics",
    "437": "Thumb Ring",
    "438": "Theocracy",
    "439": "Heresy",
    "440": "Supremacy",
    "441": "Herbal Medicine",
    "445": "Shinkichon",
    "448": "Elite Turtle Ship",
    "450": "Elite War Wagon",
    "457": "Perfusion"
}

# xxx(okachaiev): not all of them
_UNITS = {
    "4": "Archer",
    "5": "Hand Cannoneer",
    "6": "Elite Skirmisher",
    "7": "Skirmisher",
    "8": "Longbowman",
    "11": "Mangudai",
    "24": "Crossbowman",
    "25": "Teutonic Knight",
    "37": "Light Cavalry",
    "38": "Knight",
    "39": "Cavalry Archer",
    "40": "Cataphract",
    "41": "Huskarl",
    "42": "Trebuchet",
    "46": "Janissary",
    "48": "Wild Boar",
    "56": "Fisherman",
    "74": "Militia", 
    "75": "Man-at-Arms",
    "76": "Heavy Swordsman",
    "77": "Long Swordsman",
    "83": "Villager",
    "93": "Spearman",
    "94": "Berserk",
    "118": "Builder",
    "120": "Forager",
    "122": "Hunter",
    "123": "Lumberjack",
    "124": "Stone Miner",
    "125": "Monk",
    "156": "Repairer",
}

# xxx(okachaiev): not all of them
_BUILDINGS = {
    "10": "Archery Range",
    "12": "Barracks",
    "15": "Junk",
    "17": "Trade Cog",
    "18": "Blacksmith",
    "20": "Barracks",
    "21": "War Galley",
    "30": "Monastery",
    "33": "Castle",
    "35": "Battering Ram",
    "45": "Dock",
    "46": "Janissary",
    "49": "Siege Workshop",
    "50": "Farm",
    "59": "Forage Bush",
    "63": "Gate",
    "66": "Gold Mine",
    "68": "Mill",
    "70": "House",
    "71": "Town Center",
    "72": "Palisade Wall",
    "79": "Watch Tower",
    "84": "Market",
    "102": "Stone Mine",
    "103": "Blacksmith",
    "110": "Trade Workshop",
    "112": "Flare",
    "116": "Market",
    "117": "Stone Wall",
    "562": "Lumber Camp",
    "584": "Mining Camp", 
}

_TECHNOLOGIES_NAME = {v:(index, int(k)) for index, (k, v) in enumerate(_TECHNOLOGIES.items())}
_TECHNOLOGIES_INDEX = [int(k) for k in _TECHNOLOGIES.keys()]

def tech(name: str):
    _, tech_id = _TECHNOLOGIES_NAME.get(name)
    return tech_id

def can_research(obs, name):
    index, _ = _TECHNOLOGIES_NAME.get(name)
    return obs['can_research'][index]

# xxx(okachaiev): code duplication, like a lot

_BUILDINGS_NAME = {v:(index, int(k)) for index, (k, v) in enumerate(_BUILDINGS.items())}
_BUILDINGS_INDEX = [int(k) for k in _BUILDINGS.keys()]

def building(name: str):
    _, building_id = _BUILDINGS_NAME.get(name)
    return building_id

def building_index(name: str):
    index, _ = _BUILDINGS_NAME.get(name)
    return index

def can_build(obs, name):
    return obs['can_build'][building_index(name)]

# xxx(okachaiev): maybe it makes sense to maintain same
# naming conventions as scripting languages provide?
def count_buildings(obs, name: str):
    return obs['buildings'][building_index(name)]

# xxx(okachaiev): code duplication, like a lot

_UNITS_NAME = {v:(index, int(k)) for index, (k, v) in enumerate(_UNITS.items())}
_UNITS_INDEX = [int(k) for k in _UNITS.keys()]

def unit(name: str):
    _, unit_id = _UNITS_NAME.get(name)
    return unit_id

def can_train(obs, name):
    index, _ = _UNITS_NAME.get(name)
    return obs['can_train'][index]

class _resource:
    Food = 0
    Wood = 1
    Gold = 2
    Stone = 3

def dropsite_min_distance(obs, resource_name: str):
    return obs['dropsite_min_distance'][getattr(_resource, resource_name)]

def resource_found(obs, resource_name: str):
    return obs['resource_found'][getattr(_resource, resource_name)]

class AGE:
    dark = 0
    feudal = 1
    castle = 2
    imperial = 3

# xxx(okachaiev): should get all of them
_SN = {
    'sn-percent-civilian-explorers': 0,
    'sn-total-number-explorers': 18,
    'sn-number-explore-groups': 42,
    'sn-enable-boar-hunting': 244,
    'sn-food-gatherer-percentage': 117,
    'sn-gold-gatherer-percentage': 118,
    'sn-stone-gatherer-percentage': 119,
    'sn-wood-gatherer-percentage': 120,
}

def sn(sn_name: str) -> int:
    return _SN[sn_name]