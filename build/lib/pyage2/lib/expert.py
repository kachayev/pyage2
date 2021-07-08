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
    return unpacked_result

ri_loom = 0
house = 1
lumber_camp = 2
mill = 3
farm = 4
mining_camp = 5
blacksmith = 6
barracks = 7
archery_range = 8

villager = 0
archer_line = 1

dark_age, feudal_age, castle_age, imperial_age, post_imperial_age = 0, 1, 2, 3, 4

food, wood, gold, stone = 0, 1, 2, 3

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
            raw_result = _unpack(response.results[i], result_type).result
            # check if it's array or not
            if "." in result_key:
                result_key, = result_key.split(".", 1)
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