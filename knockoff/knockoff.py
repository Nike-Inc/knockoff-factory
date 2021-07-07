# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


from faker import Faker
from numpy import random

import yaml

from . import orm
from .factory.assembly import Blueprint, Assembler
from .factory.node import Table, FactoryPart
from .factory.node import FactoryComponent, FactoryPrototype


class Knockoff(object):

    def __init__(self, path_or_config, seed=None):

        if isinstance(path_or_config, dict):
            self.config = path_or_config
        else:
            with open(path_or_config, "rb") as f:
                self.config = yaml.safe_load(f)

        self.seed = seed

        self.__register_database_engines()

        blueprint = Blueprint.from_config(self.config["knockoff"])
        assembler = Assembler(blueprint)
        assembler.start()

        self.__register_nodes(blueprint)

    def __register_database_engines(self):
        for config in self.config["knockoff"].get("databases", []):
            orm.register_engine(config["name"], config["config"])

    def __register_nodes(self, blueprint):
        data = {}
        for node in blueprint.nodes:
            if node.node_type in {Table.node_type,
                                  FactoryPart.node_type,
                                  FactoryPrototype.node_type}:
                data.setdefault(node.node_type, {})[node.name] = node.data
            elif node.node_type == FactoryComponent.node_type:
                data.setdefault(node.node_type, {})[node.name] = node.generator
        self.tables = data.get(Table.node_type, {})
        self.parts = data.get(FactoryPart.node_type, {})
        self.prototypes = data.get(FactoryPrototype.node_type, {})
        self.components = data.get(FactoryComponent.node_type, {})

    @property
    def seed(self):
        return self._seed

    @seed.setter
    def seed(self, seed):
        if seed:
            Faker.seed(seed)
            random.seed(seed)
        self._seed = seed
