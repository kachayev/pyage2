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
"""Run Age of Empires II game based on a given configuration."""

import click
import logging

from pyage2.env import Age2Env, Age2ProcessError, Step, Agent
from pyage2.lib import actions, bot
from pyage2.lib.configs import *
from pyage2.lib.cli import EnumChoice


# xxx(okachaiev): need to adjust this config (change time format, highlight module)
logging.basicConfig(format='%(asctime)-15s %(message)s', level=logging.DEBUG)	


@click.command()
@click.option("--agent1") # xxx(okachaiev): i'm curious what is the best way to express "--agent{1-8}"
@click.option("--civilization1", default=PlayerCivilization.RANDOM, type=EnumChoice(PlayerCivilization))
@click.option("--team1", default=PlayerTeam.NO_TEAM, type=PlayerTeam)
@click.option("--color1", default=None, type=int)
@click.option("--agent2")
@click.option("--civilization2", default=PlayerCivilization.RANDOM, type=EnumChoice(PlayerCivilization))
@click.option("--team2", default=PlayerTeam.NO_TEAM, type=PlayerTeam)
@click.option("--color2", default=None, type=int)
@click.option("--map-type", default=MapType.BLACK_FOREST, type=EnumChoice(MapType))
@click.option("--map-size", default=MapSize.TINY, type=EnumChoice(MapSize))
@click.option("--game-difficulty", default=GameDifficulty.HARD, type=EnumChoice(GameDifficulty))
@click.option("--starting-age", default=StartingAge.STANDARD, type=EnumChoice(StartingAge))
@click.option("--starting-resources", default=StartingResources.STANDARD, type=EnumChoice(StartingResources))
@click.option("--game-type", default=GameType.RANDOM_MAP, type=EnumChoice(GameType))
@click.option("--reveal-map", default=RevealMap.ALL_VISIBLE, type=EnumChoice(RevealMap))
@click.option("--victory-type", default=VictoryType.STANDARD, type=EnumChoice(VictoryType))
@click.option("--scenario-name", default=None, type=str)
@click.option("--population-limit", default=250, type=int)
@click.option("--save-replay/--no-replay", default=False)
@click.option("--run-full-speed/--run-normal-speed", default=False)
@click.option("--run-focused-only/--run-unfocused", default=False) # xxx(okachaiev): fix this option
@click.option("--minimized-window/--no-minimized-window", default=False)
@click.option("--exec-path", default=None)
@click.option("--autogame-dll-path", default=None)
@click.option("--aimodule-dll-path", default=None)
def entry_point(**kwargs):
	run_config = RunConfig.create(
		exec_path=kwargs.get('exec_path'),
		autogame_dll=kwargs.get('autogame_dll_path'),
		aimodule_dll=kwargs.get('aimodule_dll_path'),
	)

	game_config = GameConfig(
		map_type=kwargs.get("map_type"),
		map_size=kwargs.get("map_size"), # xxx(okachaiev): what about exact coordinates?
		game_difficulty=kwargs.get("game_difficulty"),
		starting_age=kwargs.get("starting_age"),
		starting_resources=kwargs.get("starting_resources"),
		game_type=kwargs.get("game_type"),
		reveal_map=kwargs.get("reveal_map"),
		victory_type=kwargs.get("victory_type"),
		scenario_name=kwargs.get("scenario_name"),
		population_limit=kwargs.get("population_limit"),
		full_speed=bool(kwargs.get("run_full_speed")),
		run_unfocused=bool(kwargs.get("run_unfocused")),
		minimized_window=bool(kwargs.get("minimized_window")),
		save_replay=bool(kwargs.get("save_replay")),
	)

	# add players based on given "--agent{1-8}" configurations
	# xxx(okachaiev): right now it defines only {1,2} rather than 8 slots
	for i in range(1, MAX_SLOTS+1):
		# xxx(okachaiev): we should probably raise an exception if agents
		# configuration given has empty slot. e.g. agent1, agent2, agent5
		if kwargs.get(f"agent{i}") is None: break
		game_config.add_player(PlayerConfig.create(
			agent=kwargs.get(f"agent{i}"),
			civilization=kwargs.get(f"civilization{i}"),
			team=kwargs.get(f"team{i}"),
			color=kwargs.get(f"color{i}"),
		))

	logging.info("Game configuration: %s", game_config)

	agents = [Agent.for_player(i+1, p) for i,p in enumerate(game_config.players) if p.is_agent]
	if agents:
		# xxx(okachaiev): this should be probably called from the env
		# itself rather than from a script (to make sure it always happens)
		bot.ensure_noop_bot(run_config.exec_path)

	logging.info("Agents setup: %s", agents)

	with Age2Env(run_config, game_config) as env:
		for agent in agents:
			agent.instance.setup(env.observation_spec(), env.action_spec())
			agent.instance.reset()
		reward, done = 0, False
		obs, info = env.reset()
		while not done:
			# xxx(okachaiev): should totally run this in separate threads
			actions = []
			for agent in agents:
				agent_obs = obs[agent.player_id-1]
				agent_obs.update(info)
				agent_actions = agent.instance.step(Step(
					observation=agent_obs,
					reward=reward,
					discount=0.,
				))
				actions.append((agent.player_id, agent_actions))
			# xxx(okachaiev): what would be the most flexible way
			# to define reward? a callback? weights?
			try:
				obs, reward, done, info = env.step(actions)
			except Age2ProcessError as e:
				logging.error(str(e))
				done = True
			else:
				if info['episode_steps'] % 100 == 0:
					print(obs)
					print(info)
		logging.info("Game if finished.")
		print(obs)
		print(info)

if __name__ == "__main__":
	entry_point()