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

from typing import Union

import pyage2.expert.action.action_pb2 as action
from  pyage2.lib import expert

def no_op():
    return None

def build(building_type: Union[str, int]):
    if isinstance(building_type, str):
        building_type = expert.building(building_type)
    return action.Build(inConstBuildingId=building_type)

def train(unit_type: Union[str, int]):
    if isinstance(unit_type, str):
        unit_type = expert.unit(unit_type)
    return action.Train(inConstUnitId=unit_type)

def research(tech_type: Union[str, int]):
    if isinstance(tech_type, str):
        tech_type = expert.tech(tech_type)
    return action.Research(inConstTechId=tech_type)

def attack_now():
    return action.AttackNow()

def set_strategic_number(sn_id: Union[str, int], sn_value: int):
    if isinstance(sn_id, str):
        sn_id = expert.sn(sn_id)
    return action.SetStrategicNumber(inConstSnId=sn_id, inConstValue=sn_value)