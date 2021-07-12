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

from dataclasses import dataclass, field
from enum import Enum
import logging
import os
import os.path
from pathlib import Path
from typing import List, Optional, Tuple, Union

PYAGE2_PATH_ENV = 'PYAGE2PATH'
APPDATA_ENV = 'AppData'

DEFAULT_EXEC_PATH = 'Microsoft Games\\Age of Empires ii\\Age2_x1\\age2_x1.5.exe'
DEFAULT_AUTOGAME = 'hooks\\aoc-auto-game.dll'
DEFAULT_AIMODULE = 'hooks\\aimodule-aoc.dll'
DEFAULT_AUTOGAME_PORT = 64720
DEFAULT_AIMODULE_PORT = 37412
# this is a hack to avoid problems with Game struct
# initialization in the game process
DEFAULT_AIMODULE_LOAD_DELAY_SECONDS = 2
DEFAULT_AUTOGAME_CONNECT_DELAY_SECONDS = 3
DEFAULT_AUTOGAME_TIMEOUT_SECONDS = 2
DEFAULT_AUTOGAME_RECONNECT_LIMIT = 30

MAX_SLOTS = 8

PACKAGE_FOLDER = Path(__file__).parent.parent

@dataclass
class RunConfig:
    """All configuration options necessary to run Age of Empires II process."""

    exec_path: str
    autogame_dll: str
    aimodule_dll: str
    autogame_port: int
    aimodule_port: int
    autogame_connect_delay: int = DEFAULT_AUTOGAME_CONNECT_DELAY_SECONDS
    autogame_timeout: int = DEFAULT_AUTOGAME_TIMEOUT_SECONDS
    autogame_reconnect_limit: int = DEFAULT_AUTOGAME_RECONNECT_LIMIT
    aimodule_load_delay: int = DEFAULT_AIMODULE_LOAD_DELAY_SECONDS
    host: str = "127.0.0.1"

    @classmethod
    def create(cls,
               *,
               exec_path: Optional[str] = None,
               autogame_dll: Optional[str] = None,
               aimodule_dll: Optional[str] = None,
               autogame_connect_delay: int = DEFAULT_AUTOGAME_CONNECT_DELAY_SECONDS,
               autogame_timeout: int = DEFAULT_AUTOGAME_TIMEOUT_SECONDS,
               autogame_reconnect_limit: int = DEFAULT_AUTOGAME_RECONNECT_LIMIT,
               aimodule_load_delay: int = DEFAULT_AIMODULE_LOAD_DELAY_SECONDS) -> 'RunConfig':
        # exec path resolution order:
        # * explicit param from the launcher script
        # * PYAGE2PATH env variable
        # * default EXE files from AppData folder
        if exec_path is None:
            exec_path = os.getenv(PYAGE2_PATH_ENV)
            if exec_path is not None:
                logging.debug('Using exec path from %s environment variable.', PYAGE2_PATH_ENV)
            else:
                exec_path = os.path.join(os.getenv(APPDATA_ENV), DEFAULT_EXEC_PATH)
                logging.debug('Using default exec path.')
        exec_path = os.path.expanduser(exec_path)
        if not os.path.isfile(exec_path):
            raise RuntimeError(f"{exec_path} does not exist.")
        if not os.access(exec_path, os.X_OK):
            raise RuntimeError(f"{exec_path} is not executable.")

        # find DLLs
        if autogame_dll is None:
            autogame_dll = PACKAGE_FOLDER.joinpath(DEFAULT_AUTOGAME)
        if not os.path.isfile(autogame_dll):
            raise RuntimeError(f"{autogame_dll} does not exist.")

        if aimodule_dll is None:
            aimodule_dll = PACKAGE_FOLDER.joinpath(DEFAULT_AIMODULE)
        if not os.path.isfile(aimodule_dll):
            raise RuntimeError(f"{aimodule_dll} does not exist.")

        return cls(
            exec_path=exec_path,
            autogame_dll=os.path.expanduser(autogame_dll),
            autogame_port=DEFAULT_AUTOGAME_PORT, # xxx(okachaiev): is it possible to use a free one?
            aimodule_dll=os.path.expanduser(aimodule_dll),
            aimodule_port=DEFAULT_AIMODULE_PORT, # xxx(okachaiev): find free port if necessary
            aimodule_load_delay=aimodule_load_delay,
            autogame_connect_delay=autogame_connect_delay,
            autogame_timeout=autogame_timeout,
            autogame_reconnect_limit=autogame_reconnect_limit,
        )

class PlayerType(Enum):
    HUMAN = 0
    BOT = 1 # AI bot
    AGENT = 2 # gym compatible agent

class PlayerCivilization(Enum):
    # 19 and 30 stands for Random, not sure what's the difference
    # we also use `None` to represent random civilization
    BRITONS = 1
    FRANKS = 2
    GOTHS = 3
    TEUTONS = 4
    JAPANESE = 5
    CHINESE = 6
    BYZANTINE = 7
    PERSIANS = 8
    SARACENS = 9
    TURKS = 10
    VIKINGS = 11
    MONGOLS = 12
    CELTS = 13
    SPANISH = 14
    AZTEC = 15
    MAYAN = 16
    HUNS = 17
    KOREANS = 18
    RANDOM = 19

class PlayerTeam(Enum):
    NO_TEAM = 0
    TEAM_1 = 1
    TEAM_2 = 2
    TEAM_3 = 3
    TEAM_4 = 4
    RANDOM = 5

class MapType(Enum):
    ARABIA = 9
    ARCHIPELAGO = 10
    BALTIC = 11
    BLACK_FOREST = 12
    COASTAL = 13
    CONTINENTAL = 14
    CRATER_LAKE = 15
    FORTRESS = 16
    GOLD_RUSH = 17
    HIGHLAND = 18
    ISLANDS = 19
    MEDITERRANEAN = 20
    MIGRATION = 21
    RIVERS = 22
    TEAM_ISLANDS = 23
    SCANDINAVIA = 25
    MONGOLIA = 26
    YUCATAN = 27
    SALT_MARSH = 28
    ARENA = 29
    OASIS = 31
    GHOST_LAKE = 32
    NOMAD = 33
    IBERIA = 34
    BRITAIN = 25
    MIDEAST = 36
    TEXAS = 37
    ITALY = 38
    CENTRAL_AMERICA = 39
    FRANCE = 40
    NORSE_LANDS = 41
    SEA_OF_JAPAN = 42
    BYZENTIUM = 43
    # all possible randoms below:
    RANDOM = 24
    RANDOM_LAND = 45
    RANDOM_REAL_WORLD = 47
    RANDOM_BLIND = 48
    RANDOM_CONVENTIONAL = 49

class MapSize(Enum):
    TINY = 0
    SMALL = 1
    MEDIUM = 2
    NORMAL = 3
    LARGE = 4
    GIANT = 5

class GameDifficulty(Enum):
    HARDEST = 0
    HARD = 1
    MODERATE = 2
    STANDARD = 3
    EASIEST = 4

class StartingAge(Enum):
    STANDARD = 0
    DARK_AGE = 2
    FEUDAL_AGE = 3
    CASTLE_AGE = 4
    IMPERIAL_AGE = 5

class StartingResources(Enum):
    STANDARD = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3

class GameType(Enum):
    RANDOM_MAP = 0
    REGICIDE = 1
    DEATH_MATCH = 2
    SCENARIO = 3
    KING_OF_THE_HILL = 5
    WONDER_RACE = 6
    TURBO_RANDOM = 8

class RevealMap(Enum):
    NORMAL = 0
    EXPLORED = 1
    ALL_VISIBLE = 2

class VictoryType(Enum):
    STANDARD = 0
    CONQUEST = 1
    RELICS = 4
    TIME_LIMIT = 7
    SCORE = 8

@dataclass
class PlayerConfig:
    player_type: PlayerType
    # based on player_type, either Bot filename or Agent module
    # `None` here means "random bot"
    agent: Optional[str]
    civilization: Optional[PlayerCivilization] # None = random civilization
    team: PlayerTeam = PlayerTeam.NO_TEAM
    color: Optional[int] = None

    @classmethod
    def create(cls,
               *,
               agent: Optional[str] = None,
               civilization: Optional[PlayerCivilization] = None,
               team: PlayerTeam = PlayerTeam.NO_TEAM,
               color: Optional[int] = None):
        if agent is None:
            player_type = PlayerType.HUMAN
        elif "." in agent:
            # xxx(okachaiev): check import
            player_type = PlayerType.AGENT
        else:
            # xxx(okachaiev): check file exists
            player_type = PlayerType.BOT
        if color is not None:
            assert 1 <= color <= 8, "Color should be an integer between 1 to 8"
        
        return cls(
            player_type=player_type,
            agent=agent,
            civilization=civilization,
            team=team,
            color=color,
        )
    
    @property
    def is_human(self):
        return self.player_type == PlayerType.HUMAN

    @property
    def is_agent(self):
        return self.player_type == PlayerType.AGENT

@dataclass
class GameConfig:
    map_type: MapType = MapType.RANDOM
    map_size: Union[MapSize, Tuple[int, int]] = MapSize.MEDIUM
    game_difficulty: GameDifficulty = GameDifficulty.MODERATE
    starting_age: StartingAge = StartingAge.STANDARD
    starting_resources: StartingResources = StartingResources.STANDARD
    game_type: GameType = GameType.DEATH_MATCH
    reveal_map: RevealMap = RevealMap.NORMAL
    victory_type: VictoryType = VictoryType.STANDARD
    scenario_name: Optional[str] = None # works only for GameType.SCENARIO
    population_limit: int = 250
    full_speed: bool = False
    run_unfocused: bool = True
    minimized_window: bool = False
    save_replay: bool = False
    players: List[PlayerConfig] = field(default_factory=list)

    def add_player(self, player_config: PlayerConfig):
        if len(self.players) == MAX_SLOTS:
            raise ValueError("All player slots are already taken.")
        if player_config.is_human and any(p.is_human for p in self.players):
            raise ValueError("Only single HUMAN player allowed.")
        self.players.append(player_config)
    
    def validate(self):
        if len(self.players) < 2:
            raise ValueError("At least 2 players required for a game.")
        assert 50 <= self.population_limit <= 300, "population_limit should be in [50, 300] range"
        assert self.population_limit % 25 == 0, "population_limit should be devided by 25"
        if self.scenario_name is not None:
            assert self.game_type == GameType.SCENARIO, "scenario_name could be set only for GameType.SCENARION"
        return self