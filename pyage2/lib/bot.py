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
"""Implements tools for working with scripted AI bots."""

from pathlib import Path

# xxx(okachaiev): not sure if there's a need to rename/reconfigure this
DEFAULT_NOOP_BOT_NAME = "PyAge2_NOOP"

EMPTY_RULE = """
(defrule
    (true)
=>
    (disable-self)
)
"""

def ensure_noop_bot(exec_path: str, bot_name: str = DEFAULT_NOOP_BOT_NAME):
    """Generates effectively 'empty' AI Bot, so the game process doesn't
    reports error when working with programmable agents.
    """
    ai_folder = Path(exec_path).parent.parent.joinpath("Ai\\")
    ai_folder.joinpath(f"{bot_name}.ai").touch()
    with ai_folder.joinpath(f"{bot_name}.per").open("w") as f:
        f.write(EMPTY_RULE)
    return bot_name