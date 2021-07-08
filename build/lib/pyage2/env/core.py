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

from dataclasses import dataclass
from typing import Any

@dataclass
class Step:
    observation: Any
    reward: int
    discount: float

class BaseEnv:
    """Abstract environment compatible with OpenGym API."""

    def reset(self):
        pass

    def step(self, action):
        pass

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
        pass

    def __enter__(self):
        """Allows the environment to be used as a context manager (with-statement)."""
        return self

    def __exit__(self, _exception_type, _exception_value, _exception_traceback):
        self.close()
    
    def __del__(self):
        self.close()
