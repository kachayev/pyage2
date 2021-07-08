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

import pyage2.protos.expert.action.action_pb2 as action

def no_op():
    return None

def build(building_type: int):
    return action.Build(inConstBuildingId=building_type)

def train(unit_type: int):
    return action.Train(inConstUnitId=unit_type)

def research(tech_type: int):
    return action.Research(inConstTechId=tech_type)

def attack_now():
    return action.AttackNow()