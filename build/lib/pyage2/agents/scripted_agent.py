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

class ScriptedAgent(BaseAgent):

    # xxx(okachaiev): need to deal with strategic numbers as well
    def _actions(self, obs):
        if obs.observation['military_population'] >= 10:
            yield actions.attack_now()
        
        if obs.observation['can_research'][expert.ri_loom]:
            yield actions.research(const.ri_loom)
        
        if obs.observation['civilian_population'] >= 21 \
                and obs.observation['can_research'][expert.feudal_age]:
            yield actions.research(const.feadal_age)
        
        if obs.observation['civilian_population'] < 130 \
                and obs.observation['can_train'][expert.villager]:
            yield actions.train(const.villager)
        
        if obs.observation['can_train'][expert.archer_line]:
            yield actions.train(const.archer_line)

        if obs.observation['housing_headroom'] < 5 \
                and obs.observation['population_headroom'] != 0 \
                and obs.observation['can_build'][expert.house]:
            yield actions.build(const.house)

        if obs.observation['resource_found'][expert.wood] \
                and obs.observation['dropsite_min_distance'][expert.wood] > 3 \
                and obs.observation['can_build'][expert.lumber_camp]:
            yield actions.build(expert.lumber_camp)

        if obs.observation['resource_found'][expert.food] \
                and obs.observation['dropsite_min_distance'][expert.food] > 3 \
                and obs.observation['can_build'][expert.mill]:
            yield actions.build(expert.mill)

        if obs.observation['buildings'][expert.farm] < 6 \
                and obs.observation['can_build'][expert.farm]:
            yield actions.build(expert.farm)

        if obs.observation['current_age'] >= expert.feudal_age \
                and obs.observation['resource_found'][expert.gold] \
                and obs.observation['dropsite_min_distance'][expert.gold] > 3 \
                and obs.observation['can_build'][expert.mining_camp]:
            yield actions.build(expert.mining_camp)
        
        if obs.observation['buildings'][expert.blacksmith] == 0 \
                and obs.observation['can_build'][expert.blacksmith]:
            yield actions.build(expert.blacksmith)

        if obs.observation['current_age'] >= expert.feudal_age \
                and obs.observation['buildings'][expert.barracks] == 0 \
                and obs.observation['can_build'][expert.barracks]:
            yield actions.build(expert.barracks)

        if obs.observation['current_age'] >= expert.feudal_age \
                and obs.observation['buildings'][expert.archery_range] < 2 \
                and obs.observation['can_build'][expert.archery_range]:
            yield actions.build(expert.archery_range)

    def step(self, obs):
        super(ScriptedAgent, self).step(obs)
        # xxx(okachaiev): still not sure if array is the best
        # container for actions but so far I don't have use cases
        return list(self._actions(obs))
