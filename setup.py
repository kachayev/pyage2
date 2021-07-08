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

from setuptools import setup

description = """PyAge2 - Age of Empires II Learning Environment

PyAge2 is set of tools to programmatically manage games of "Age of Empires II: The Conquerors" with a
custom AI bots (agents). The environment runs the game process, injects DLL that exposes gRPC server
allowing external tools to interact with the game. Thanks to some internal hacks, the system is capable
of simulating games at incradibly high speed (20-30 minutes game could be simualted in seconds).

Disclaimer: the API used to manage the game process **is not officially supported** by game developers.

Read the README at https://github.com/kachayev/pyage2 for more information.
"""

setup(
    name = 'PyAge2',
    version = '1.0.0',
    description = 'Age of Empires II learning environment and toolkit for training AI agents.',
    long_description = description,
    author = 'Oleksii Kachaiev',
    author_email = 'kachayev@gmail.com',
    license = 'Apache License, Version 2.0',
    keywords = 'Age of Empires, AI, Reinforcement Learning',
    url = 'https://github.com/kachayev/pyage2',
    packages = [
        'pyage2',
        'pyage2.agents',
        'pyage2.protos',
        'pyage2.expert',
        'pyage2.bin',
        'pyage2.env',
        'pyage2.lib',
        'pyage2.tests',
    ],
    package_data = {'': ['*.dll']},
    install_requires = [
        'click>=8.0.0',
        'msgpack-rpc-python>=0.4.1',
        'protobuf>=3.17.3',
        'grpcio>=1.38.1',
    ],
    entry_points = {
        'console_scripts': [
            'pyage2_play = pyage2.bin.play:entry_point',
        ],
    },
    classifiers= [
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
)