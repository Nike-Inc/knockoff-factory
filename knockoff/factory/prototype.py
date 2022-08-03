# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.

import os
import logging
import itertools
from operator import itemgetter

import pandas as pd

from knockoff.factory.component import ComponentFunctionFactory
from knockoff.factory.counterfeit import KNOCKOFF_ATTEMPT_LIMIT_ENV
from knockoff.utilities.functools import call_with_args_kwargs


logger = logging.getLogger(__name__)


def load_prototype_from_components(source, assembler, node_name):
    limit = int(os.environ.get(KNOCKOFF_ATTEMPT_LIMIT_ENV, 1000000))

    dependencies = [(component['name'],
                     dep) for component in source.config['components']
                    for dep in component['source'].get('dependencies',
                                                       [])]

    def sort(name_dep):
        return tuple(assembler.parse_dependency(name_dep[1])[:-1])

    dependencies.sort(key=sort)
    names = [component['name'] for component in source.config['components']]
    name_to_source = {component['name']:component['source']
                      for component in source.config['components']}

    i = 0
    records = []
    # create mapping of unique key indices to unique keys
    unique_constraints = {tuple(constraint): set()
                          for constraint in (source.config.get('unique',
                                                               []))}
    while len(records) < source.config['number'] and i < limit:
        i += 1
        record = {}
        component_to_function_input = {}
        for (node_type, name), group in itertools.groupby(dependencies,
                                                          sort):
            node = assembler.blueprint.get_node(node_type, name)
            sample = node.data.sample(1)
            for component_name, dep in group:
                strategy = name_to_source[component_name]['strategy']
                if strategy == "knockoff":
                    (dep_type,
                     dep_name,
                     dep_sub_name) = assembler.parse_dependency(dep)
                    col = dep_sub_name or 0
                    record[component_name] = sample[col].values[0]
                elif strategy == "function":
                    (dep_type,
                     dep_name,
                     dep_sub_name) = assembler.parse_dependency(dep)
                    col = dep_sub_name or 0
                    (component_to_function_input
                     .setdefault(component_name,
                                 {}))[dep] = sample[col].values[0]
                else:
                    raise Exception("strategy not recognized: {}"
                                    .format(strategy))

        function_factory = ComponentFunctionFactory()

        for component_name, source_config in name_to_source.items():
            if component_name in record:
                continue
            strategy = source_config['strategy']
            if strategy == 'function':
                func = function_factory.get_resource(source_config['function'])
                record[component_name] = \
                    handle_function(func,
                                    input_args=(source_config
                                                .get('input_args')),
                                    input_kwargs=(source_config
                                                  .get('input_kwargs')),
                                    func_inputs_from_dependencies=
                                    component_to_function_input
                                    .get(component_name))

            else:
                node = assembler.blueprint.get_node("component", "{}.{}"
                                                    .format(node_name,
                                                            component_name))
                record[component_name] = next(node.generator)

        if not _satisfies_unique_constraints(record, unique_constraints):
            continue

        for constraint in unique_constraints.keys():
            unique_constraints[constraint].add(itemgetter(*constraint)(record))

        records.append(itemgetter(*names)(record))

    if i >= limit:
        logger.error("Could not generate prototype={}"
                     .format(node_name))
        raise Exception("Attempts to create unique set reached: {}"
                        .format(limit))
    return pd.DataFrame(records, columns=names)


def handle_function(func, input_args=None, input_kwargs=None,
                    func_inputs_from_dependencies=None):

    args = []
    kwargs = {}

    for input_cfg in input_args or []:
        if input_cfg['type'] == "constant":
            args.append(input_cfg['value'])
        elif input_cfg['type'] == 'dependency':
            args.append(func_inputs_from_dependencies[input_cfg['value']])
    for input_cfg in input_kwargs or []:
        if input_cfg['type'] == "constant":
            kwargs[input_cfg['key']] = input_cfg['value']
        elif input_cfg['type'] == 'dependency':
            kwargs[input_cfg['key']] = \
                func_inputs_from_dependencies[input_cfg['value']]
    return call_with_args_kwargs(func, tuple(args), kwargs)


def _satisfies_unique_constraints(record, constraints):
    valid_record = True
    for constraint in constraints.keys():
        if itemgetter(*constraint)(record) in constraints[constraint]:
            valid_record = False
        if not valid_record:
            break
    return valid_record
