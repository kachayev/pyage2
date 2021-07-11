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
"""Scripted agent inspired by AI Scripting tutorial on Steam:

https://steamcommunity.com/sharedfiles/filedetails/?id=1238296169
"""

from pyage2.agents import BaseAgent
from pyage2.lib import actions
from pyage2.lib import expert
from pyage2.lib.expert import StrategicNumber

class ScriptedAgent(BaseAgent):
    """Simplest agent capable of building, training, and research."""

    def reset(self):
        super(ScriptedAgent, self).reset()
        self.sn = False
        self.sn_dark_age = False
        self.sn_feudal_age = False

    def step(self, obs):
        super(ScriptedAgent, self).step(obs)
        # xxx(okachaiev): still not sure if array is the best
        # container for actions but so far I don't have use cases
        return list(self._actions(obs))

    def _set_strategic_numbers(self, obs):
        if not self.sn:
            self.sn = True
            yield actions.set_strategic_number(StrategicNumber.PERCENT_CIVILIAN_EXPLORERS, 0)
            yield actions.set_strategic_number(StrategicNumber.TOTAL_NUMBER_EXPLORERS, 1)
            yield actions.set_strategic_number(StrategicNumber.NUMBER_EXPLORE_GROUPS, 1)
            yield actions.set_strategic_number(StrategicNumber.ENABLE_BOAR_HUNTING, 1)

        if not self.sn_dark_age and obs.observation['current_age'] == expert.AGE.DARK:
            self.sn_dark_age = True
            yield actions.set_strategic_number(StrategicNumber.FOOD_GATHERER_PERCENTAGE, 80)
            yield actions.set_strategic_number(StrategicNumber.WOOD_GATHERER_PERCENTAGE, 20)
            yield actions.set_strategic_number(StrategicNumber.GOLD_GATHERER_PERCENTAGE, 0)
            yield actions.set_strategic_number(StrategicNumber.STONE_GATHERER_PERCENTAGE, 0)

        if not self.sn_feudal_age and obs.observation['current_age'] == expert.AGE.FEUDAL:
            self.sn_feudal_age = True
            yield actions.set_strategic_number(StrategicNumber.FOOD_GATHERER_PERCENTAGE, 50)
            yield actions.set_strategic_number(StrategicNumber.WOOD_GATHERER_PERCENTAGE, 30)
            yield actions.set_strategic_number(StrategicNumber.GOLD_GATHERER_PERCENTAGE, 15)
            yield actions.set_strategic_number(StrategicNumber.STONE_GATHERER_PERCENTAGE, 5)

    # xxx(okachaiev): need to deal with strategic numbers as well
    def _actions(self, obs):

        yield from self._set_strategic_numbers(obs)

        if obs.observation['military_population'] >= 10:
            yield actions.attack_now()
        
        # xxx(okachaiev): should this be base agent API
        # like, self.can_research and self.tech?
        if expert.can_research(obs.observation, 'Loom'):
            yield actions.research('Loom')

        if expert.can_research(obs.observation, 'Fletching'):
            yield actions.research('Fletching')

        if obs.observation['civilian_population'] >= 19 \
                and expert.can_research(obs.observation, 'Feudal Age'):
            # xxx(okachaiev): if we don't have access to the result of previous
            # actions... how do we know that this action should not be issued again?
            # even if we have "research status", "building queue", and "training queue"...
            # actions are still issued in parallel to the game process, so race condition
            # could still happen even if we are extremly precise with our rules
            yield actions.research('Feudal Age')

        if obs.observation['civilian_population'] < 130 \
                and expert.can_train(obs.observation, 'Villager'):
            yield actions.train('Villager')

        if expert.can_train(obs.observation, 'Man-at-Arms'):
            yield actions.train('Man-at-Arms')
        elif expert.can_train(obs.observation, 'Militia'):
            yield actions.train('Militia')
        elif expert.can_train(obs.observation, 'Archer'):
            yield actions.train('Archer')

        if obs.observation['housing_headroom'] < 5 \
                and obs.observation['population_headroom'] != 0 \
                and expert.can_build(obs.observation, 'House'):
            yield actions.build('House')

        if expert.resource_found(obs.observation, 'Wood') \
                and expert.dropsite_min_distance(obs.observation, 'Wood') > 3 \
                and expert.can_build(obs.observation, 'Lumber Camp'):
            yield actions.build('Lumber Camp')

        if expert.resource_found(obs.observation, 'Food') \
                and expert.dropsite_min_distance(obs.observation, 'Food') > 3 \
                and expert.can_build(obs.observation, 'Mill'):
            yield actions.build('Mill')

        if expert.count_buildings(obs.observation, 'Farm') < 6 \
                and expert.can_build(obs.observation, 'Farm'):
            yield actions.build('Farm')

        if obs.observation['current_age'] >= expert.AGE.FEUDAL \
                and expert.resource_found(obs.observation, 'Gold') \
                and expert.dropsite_min_distance(obs.observation, 'Gold') > 3 \
                and expert.can_build(obs.observation, 'Mining Camp'):
            yield actions.build('Mining Camp')

        if expert.count_buildings(obs.observation, 'Blacksmith') == 0 \
                and expert.can_build(obs.observation, 'Blacksmith'):
            yield actions.build('Blacksmith')

        if expert.count_buildings(obs.observation, 'Barracks') == 0 \
                and expert.can_build(obs.observation, 'Barracks'):
            yield actions.build('Barracks')

        if obs.observation['current_age'] >= expert.AGE.FEUDAL \
                and expert.count_buildings(obs.observation, 'Archery Range') == 0 \
                and expert.can_build(obs.observation, 'Archery Range'):
            yield actions.build('Archery Range')