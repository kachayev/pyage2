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
"""Set of tools to work with CLI scripts."""

import click
from collections import OrderedDict

class EnumChoice(click.Choice):
    def __init__(self, enum, case_sensitive=False):
        self._enum = enum
        self._enum_choices = OrderedDict((elem.name.lower(), elem) for elem in enum)
        super().__init__(self._enum_choices.keys(), case_sensitive)

    def convert(self, value, param, ctx):
        if isinstance(value, self._enum): return value
        result = super().convert(value, param, ctx)
        return self._enum_choices[result]