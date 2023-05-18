# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


def call_with_args_kwargs(function, args, kwargs):
    has_args = args is not None and len(args) > 0
    has_kwargs = kwargs is not None and len(kwargs) > 0
    if has_args and has_kwargs:
        return function(*args, **kwargs)
    elif has_args:
        return function(*args)
    elif has_kwargs:
        return function(**kwargs)
    return function()
