# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


from knockoff.testing_postgresql import get_postgresql


def postgres_setup_teardown(url):
    # setup
    postgresql = get_postgresql(url=url) # create the database
    new_url = postgresql.url() # get new url

    # return the new url
    yield new_url

    # teardown
    postgresql.stop()
