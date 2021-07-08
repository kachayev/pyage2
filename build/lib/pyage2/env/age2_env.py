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
"""Age of Empire II environment."""

from enum import Enum
import logging
import msgpackrpc
import subprocess
import time
from typing import List

from pyage2.env.core import BaseEnv
from pyage2.lib import LibraryInjector
from pyage2.lib.bot import DEFAULT_NOOP_BOT_NAME
from pyage2.lib.configs import GameConfig, PlayerType, RunConfig
from pyage2.lib.expert import ExpertClient

import pyage2.expert.fact.fact_pb2 as fact
import pyage2.expert.action.action_pb2 as action

# this is a hack to avoid problems with Game struct
# initialization in the game process
AIMODULE_LOAD_DELAY_SECONDS = 2

class Age2LaunchError(Exception):
    pass

class Age2EnvState(Enum):
    START = 0
    RUNNING = 1
    DONE = 2

class Age2Env(BaseEnv):
    """Age of Empire II environment."""

    def __init__(self, run_config: RunConfig, game_config: GameConfig):
        """Creates Age of Empire II environment."""
        self._run_config = run_config
        self._game_config = game_config.validate()

        # xxx(okachaiev): this is somewhat problematic...
        # we want to track general observations for non-agent players as well
        # e.g. score/alive?/etc :thinking:
        # self._num_agents = sum(1 for p in game_config.players if p.player_type == PlayerType.AGENT)
        self._num_agents = len(game_config.players)

        self._proc = None
        self._autogame_client = None
        self._expert_client = None

        # launch game process
        self._launch_process(self._run_config)

        # inject DLL for running game programmatically
        self._init_autogame(self._proc.pid, self._run_config)

        # inject DLL to interact with expert facts and actions
        time.sleep(AIMODULE_LOAD_DELAY_SECONDS)
        self._init_expert_api(self._proc.pid, self._run_config)

        # create game based on the configuration given
        self._run_game(self._game_config)

        # prepare environment
        self._prepare()

        logging.info("Environment is ready.")

    # xxx(okachaiev): move this functionality to a separate module
    # xxx(okachaiev): what if I want to run game on one machine and
    # connect to it from a different one? should be possible if
    # there's a flag to skip "run process & inject DLLs" step
    def _launch_process(self, run_config: RunConfig):
        try:
            logging.debug(f"Launching game process %s", run_config.exec_path)
            # xxx(okachaiev): assume i also need to run a background thread
            # to poll from it periodically to make sure we can close env
            # properly if the process was killed externally
            # curious if there's an API to just provide on_close callback or something
            self._proc = subprocess.Popen(run_config.exec_path)
            logging.debug(f"Game process PID: %s", self._proc.pid)
        except OSError:
            logging.exception("Failed to launch game process.")
            raise Age2LaunchError(f"Failed to launch {run_config.exec_path}")

    def _inject_dlls(self, pid: int, libraries: List[str]):
        # xxx(okachaiev): i should just have a "remote process" abstraction
        # with Popen, on_close callback, and DLL injector (all together)
        # in this case it should be much easier to reimplement for other platforms
        with LibraryInjector(pid) as injector:
            for dll_path in libraries:
                injector.load_library(dll_path)

    def _init_autogame(self, pid: int, run_config: RunConfig):
        self._inject_dlls(pid, [run_config.autogame_dll])
        logging.debug("Connecting to autogame Msgpack RPC on %s:%s", run_config.host, run_config.autogame_port)
        self._autogame_client = msgpackrpc.Client(msgpackrpc.Address(run_config.host, run_config.autogame_port), timeout=30, reconnect_limit=30)

    def _init_expert_api(self, pid: int, run_config: RunConfig):
        self._inject_dlls(pid, [run_config.aimodule_dll])
        logging.debug("Connecting to aimodule gRPC on %s:%s", run_config.host, run_config.aimodule_port)
        self._expert_client = ExpertClient(run_config.host, run_config.aimodule_port)

    def _run_game(self, game_config: GameConfig):
        assert self._autogame_client, "Autogame client is not initialized."
        assert not self.running, "Game is already in progress."

        # for the sake of safety...
        self._autogame_client.call('ResetGameSettings')

        # general game configuration
        self._autogame_client.call('SetGameMapType', game_config.map_type.value)
        self._autogame_client.call('SetGameMapSize', game_config.map_size.value)
        self._autogame_client.call('SetGameDifficulty', game_config.game_difficulty.value)
        self._autogame_client.call('SetGameStartingAge', game_config.starting_age.value)
        self._autogame_client.call('SetGameStartingResources', game_config.starting_resources.value)
        self._autogame_client.call('SetGameType', game_config.game_type.value)
        self._autogame_client.call('SetGameRevealMap', game_config.reveal_map.value)
        # xxx(okachaiev): additional configuration should be handled properly
        self._autogame_client.call('SetGameVictoryType', game_config.victory_type.value, 0)
        if game_config.scenario_name:
            self._autogame_client.call('SetScenarioName', game_config.scenario_name)

        # running configuration
        self._autogame_client.call('SetRunFullSpeed', game_config.full_speed)
        self._autogame_client.call('SetRunUnfocused', game_config.run_unfocused)
        self._autogame_client.call('SetWindowMinimized', game_config.minimized_window)
        self._autogame_client.call('SetGameRecorded', game_config.save_replay)

        # configure players
        self._autogame_client.call('SetGameTeamsLocked', True)
        for i, player in enumerate(game_config.players):
            player_id = i+1
            if player.is_human:
                self._autogame_client.call('SetPlayerHuman', player_id)
            elif player.is_agent:
                self._autogame_client.call('SetPlayerComputer', player_id, DEFAULT_NOOP_BOT_NAME)
            else:
                self._autogame_client.call('SetPlayerComputer', player_id, player.agent)
            civilization = player.civilization or PlayerCivilization.RANDOM
            self._autogame_client.call('SetPlayerCivilization', player_id, civilization.value)
            self._autogame_client.call('SetPlayerTeam', player_id, player.team.value)
            if player.color is not None:
                self._autogame_client.call('SetPlayerColor', player_id, player.color)

        return self._autogame_client.call('StartGame')

    def _prepare(self):
        self._last_score = [0] * self._num_agents
        self._total_steps = 0
        self._episode_steps = 0
        self._episode_count = 0
        self._episode_start_time = None
        self._state = Age2EnvState.START # force to reset

    def reset(self):
        """Starts a new episode."""
        self._episode_steps = 0
        if self._episode_count > 0:
            # do not need to restart for the first episode
            self._restart()

        self._state = Age2EnvState.RUNNING
        self._episode_start_time = time.time()
        self._episode_count += 1
        logging.info("Starting episode %s.", self._episode_count)

        self._last_score = [0] * self._num_agents
        self._winning = [0] * self._num_agents
        self._info = None

        self._observe_game()

        return self._observe(), self._info

    def step(self, actions):
        """Apply actions, step the world forward, and return observations."""
        assert self._autogame_client

        if self._state == Age2EnvState.START:
            self.reset()

        # xxx(okachaiev): this is not exactly true when dealing with real-time game :thinking:
        self._total_steps += 1
        self._episode_steps += 1

        # issue actions into the game
        self._expert_client.actions(actions)

        # get observations from the game
        self._observe_game()

        # observation, reward, done, info
        # xxx(okachaiev): i'm curious what's the best approach to let agent to
        # determine it's own reward and do we even need it here? :thinking:
        return self._observe_agents(), 0, not self.running, self._info

    @property
    def game_time(self):
        if self._autogame_client is None: return 0
        return float(self._autogame_client.call('GetGameTime'))

    @property
    def running(self):
        # xxx(okachaiev): in some cases (not sure how to reproduce),
        # this call returns True for the game that already finished
        return self._autogame_client and self._autogame_client.call('GetGameInProgress')

    @property
    def game_config(self):
        return self._game_config

    def _observe_agents(self):
        """Returns an array of observations for each agent."""
        # xxx(okachaiev): ideally, we need to do this in parallel
        return [self._observe_agent(index+1) for index in range(self._num_agents)]

    def _observe_agent(self, player_id: int):
        """Collects observartions for a specific agent (or bot)."""
        # xxx(okachaiev): need to think about how the agent can get
        # access to the information about enemies (where allowed)
        expert_obs = self._expert_client.player_facts(player_id, [
            ('current_age', fact.CurrentAge(), fact.CurrentAgeResult),
            ('current_age_time', fact.CurrentAgeTime(), fact.CurrentAgeTimeResult),
            ('score', fact.CurrentScore(), fact.CurrentScoreResult),
            ('population', fact.Population(), fact.PopulationResult),
            ('population_cap', fact.PopulationCap(), fact.PopulationCapResult),
            ('population_headroom', fact.PopulationHeadroom(), fact.PopulationHeadroomResult),
            ('civilian_population', fact.CivilianPopulation(), fact.CivilianPopulationResult),
            ('military_population', fact.MilitaryPopulation(), fact.MilitaryPopulationResult),
            ('housing_headroom', fact.HousingHeadroom(), fact.HousingHeadroomResult),

            ('idle_farm_count', fact.IdleFarmCount(), fact.IdleFarmCountResult),
            # ('SoldierCount ')
            # ('AttackSoldierCount ')
            # ('DefendSoldierCount ')
            # ('WarboatCount  ')
            # ('AttackWarboatCount ')
            # ('DefendWarboatCount ')
            # ('BuildingCount ')
            # ('UnitCount ')

            # resources
            # xxx(okachaiev): this should be something like 'resources[food]'
            ('resources.0', fact.FoodAmount(), fact.FoodAmountResult),
            ('resources.1', fact.WoodAmount(), fact.WoodAmountResult),
            ('resources.2', fact.GoldAmount(), fact.GoldAmountResult),
            ('resources.3', fact.StoneAmount(), fact.StoneAmountResult),
            # ('EscrowAmount ') # for each resource

        ])

        # xxx(okachaiev): fill those in
        expert_obs.update({
            'can_build': [0]*24,
            'can_research': [0]*24,
            'can_train': [0]*24,
            'resource_found': [0]*4,
            'dropsite_min_distance': [0]*4,
        })

        expert_obs.update({
            "alive": self._autogame_client.call('GetPlayerAlive', player_id),
            "winning": self._winning[player_id-1],
        })

        return expert_obs

    def _observe_game(self):
        """Collects general informatio about the state of the game."""
        # update information on winning players
        self._winning = [0] * self._num_agents
        # xxx(okachaiev): as of now, this call returns all players
        # even when game is finished
        for player_id in self._autogame_client.call('GetWinningPlayers'):
            self._winning[player_id-1] = 1

        # better be a dataclass though in this case it wouldn't
        # be possible to merge different observations
        self._info = {
            "game_time": self.game_time,
            "wall_time": time.time() - self._episode_start_time,
            "episode": self._episode_count,
            "episode_steps": self._episode_steps,
            "total_steps": self._total_steps,
        }

    def _restart(self):
        """Restarts the game, keeps game process running."""
        assert self._autogame_client
        self._autogame_client.call('RestartGame')

    def observation_spec(self):
        """Defines the observations provided by the environment."""
        pass

    def action_spec(self):
        """Defines the actions that could be provided to `step` method."""
        pass

    def close(self):
        """Frees up any resources associated with the environment (e.g. external
        processes). The method could be used directly or via a context manager.
        """
        if self._autogame_client is not None:
            self._autogame_client.close()
            self._autogame_client = None

        if self._expert_client is not None:
            self._expert_client.close()
            self._expert_client = None

        if self._proc and self._proc.poll() is None:
            self._proc.terminate()
            self._proc = None
