# PyAge2 - "Age of Empires II" Learning Environment

**UNDER ACTIVE DEVELOPMENT**

`PyAge2` allows to interact with "Age of Empires II: The Conquerors" game from OpenAI Gym compatible Reinforcement Learning environment.

The environment runs the game process, injects DLLs that run a server within the game allowing external tools to interact with the it. Thanks to some internal hacks, the system is capable of simulating games at incredibly high speed (20-30 minutes game could be finished in seconds).

WIP. Additional goal of the project is to have a tool to deploy learned agent policies directly into the game process, bypassing the need to have a dedicated server & client to run the agent. With the help of this, the agent could be release as a publically available game Mod.

## Disclamer

**IMPORTANT**

The API used to manage the game process **is not officially supported** by game developers. As the system overwrites game process memory directly, it could lead to game crash. Usage of the environment on live games (against other human players) will lead to permanent ban both on Steam and Voobly. By running the environment, the user implicitly acknowledges the risk, and consents on using the system strickly for research purposes.

# Intro

"Age of Empires II" provides a way to script AI bots using built-in lisp-like scripting langauge. Each bot, effectively, is a set of rules (conditions and actions):

```lisp
(defrule
    (can-train villager)
=>
    (train villager)
)
```

Built-in AI agents contains 10k+ rules. To get a high level understanding of how typical bot looks inside and what capabilities are available, check out Steam guide on ["AI Scripting"](https://steamcommunity.com/sharedfiles/filedetails/?id=1238296169). In the game installation folder, you can find `Ai` directory with source code for bots available in the game.

`PyAge2` allows you to build AI bot in Python using OpenGym-like API with a `step` function takes observations from the environment and returns actions that needs to be performed. For example

```python
class VillagersOnlyAgent(BaseAgent):
    """I bet you not gonna win with this..."""
    def step(self, obs):
        if obs.observation['civilian_population'] < 130 \
                and expert.can_train(obs.observation, 'Villager'):
            return actions.train('Villager')
```

Check out `pyage2.agents.ScriptedAgent` as an example of a primitive but fully-functional agent.

The system allows you to match different AI bots/agents in a single game. 

# Motivation

Compared to other learning environment based on games (e.g. Atari, VizDoom, PySC2, MicroRTS), "Age of Empires II" presents interesting challenges for RL/ML research community.

## Long-horizon Macromanagement & Planning

RTS (Real Time Strategy) games are known for their complexity with respect to action planning. As it turned out, micromanagement (per-unit control) was easier to tackle, when macromanagement remains largely unsolved problem. "Age of Empires II" is a game where success is mainly determined by macromanagement (economy, build order, research, units production). Basic micromanagement tasks are scripted by the game engine, which means you don't need to worry about which villager should build a house and which unit should go first into the attack first.

Another challenge with macromanagement level control is delayed reward signal. For example, setting workers allocation for resources in the beginning on the game will have large impact only on the late stages of the game.

## Multiagent Coordination

The game allows up to 8 independent agents on a single map with flexible team formations (e.g. each agent on it's own team, or 4x4, or 2x2x2x2, etc). Agents do not have access to each other states. The coordination could be done only using in-game Chat. 

## Transfer Learning

"Age of Empires II" comes with loads of different civilizations, modes, maps, and custom scenarious. Default option would be to learn a new agent for each formation, which leads to combinatorical explosion. Ideally, a good agent should "understand" core game mechanics and strategies, while being flexible to utilize different tech trees, available units, flexible map conditions, etc.

## Explainability/Observability

An agent could be deployed into the environment using scripting language in a form of a decision tree (more formally, set of actions and corresponding activation conditions). This approach is not common in RL comminuty but it has tremendous practical advantage: explainability. This makes it possible for game designers and game engineers to understand and interact with internals, which might lead to much better story for game teams when incorporating learned AIs to improve game experience for players (e.g. by introducing "harder" levels of AI by incorporating RL-based improvements, or automatically adjusting agents to perform custom scenarious instead of scripting them each time manually).

# Citing

Please use this bibtex if you want to cite this repository in your publications:

```
@misc{pyage2,
    author = {Oleksii Kachaiev},
    title = {{PyAge2 - "Age of Empires II" Learning Environment}},
    year = {2021},
    publisher = {GitHub},
    journal = {GitHub repository},
    howpublished = {\url{https://github.com/kachayev/pyage2}},
}
```

# Quick Start

## Install

**Important.** Running `PyAge2` requires 32-bit Python3.7+, you can download 32-bit installer from [python.org](https://www.python.org/downloads/release/python-395/).

### PyPI

The faster and the easiest way to install PyAge2 with `pip`:

```shell
$ pip install pyage2
```

### From Source

Alternatively,

```shell
$ pip install --upgrade https://github.com/kachayev/pyage2/archive/main.zip
```

or from a local clone:

```shell
$ git clone https://github.com/kachayev/pyage2
$ pip install --upgrade pyage2/
```

## Install "Age of Empires II: The Conquerors"

`PyAge2` depends on the  "Age of Empires II: The Conquerors" game and (as of now) does not support DE versions. Which means, it won't work on Steam's versions of the game. Though, there's a tool that can help you to convert your AOE2HD to original AOC engine format: [AoE2Tool](https://github.com/gregstein/AoE2Tools) (please, follow the instructions from the repo on how to perform update). The environment was tested on most common game versions: `UserPatch 1.5`, `UserPatch 1.6`, and `WololoKingdoms` expansion.

### Windows

`PyAge2` expects default installation pass to be `C:\Users\<USER>\AppData\Roaming\Microsoft Games\Age of Empires ii\Age2_x1\age2_x1.5.exe`. In case you modified install path, please specify `PYAGE2PATH` environment variable.

### Linux/MacOS

`PyAge2` heavily relies on Win32 API, so far it's unclear if it's possible to run same hacks on Linux on MacOS. But both on my TODO list.

## Maps/AIs/Scenarios

The environment works with all built-in maps, scenarious, and AIs. And with pretty much all custom modes, e.g. [here](https://www.voobly.com/gamemods/mod/46/AoC-Custom-Scenarios) (follow the instruction for a specific mod).

To get the list of all available AI bots:

```shell
$ python -m pyage2.bin.bots_list
```

To get the list of all available maps:

```shell
$ python -m pyage2.bin.map_list
```

To get the list of all available civilizations:

```shell
$ python -m pyage2.bin.civilization_list
```

## Run an Agent

Let's run a simple game between AI bots:

```shell
$ python -m pyage2.bin.play --agent1 Barbarian --agent2 Illuminati --run-full-speed
```

or between AI bot and scripted agent:

```shell
$ python -m pyage2.bin.play --agent1 pyage2.agents.ScriptedAgent --agent2 Illuminati --run-full-speed
```

You can specify up to 8 agents on a map flexibily combining them into teams. The enviroment differenciate agents based on `.` in the agent name (names with dots recognized as a Python module and class name that will be used to instantiate an agent). Special name "HUMAN" is reserved to identify human player. There's only a single human player allowed in the game.

Additional game configuration options include map type, map size, starting age, starting resources, victory type, and more. Use `--help` to get information about all flags.

## Replay

A replay lets you review what happened during the game. To run specific replay with a game client, use

```shell
$ python -m pyage2.bin.replay <path-to-replay>
```

## In Addition

### OpenAge

[`openage`](https://openage.sft.mx/) is an open-source reimplementation of AOC engine that uses game assets but provides custom engine to run the game. It runs on all platforms, and exposes Python API for scripting. It should be possible to make the environment works on this engine, though I didn't have a chance to try to do so (as of now). Help wanted!

# Dependencies

The environments uses the following DLLs:

* [aoc-auto-game](https://github.com/FLWL/aoc-auto-game)

* [AoE2 AI Module](https://github.com/FLWL/aoe2-ai-module)

# How to Contribute

* Check for open issues or open a fresh issue to start a discussion around a feature idea or a bug.
* Fork the repository on Github & fork master to `feature-*` branch to start making your changes.
* Write a test which shows that the bug was fixed or that the feature works as expected.