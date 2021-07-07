# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


from .date.interval import Interval


def generate_periods_from_intervals(bop_interval, eop_interval):
    """

    :param bop_interval: beginning of period interval
    :param eop_interval: end of period interval
    :return: list of tuple of (bop, eop) date objects
    """
    bop_dates = Interval.parse(bop_interval)
    eop_dates = Interval.parse(eop_interval)

    assert len(bop_dates) == len(eop_dates), \
        "Length mismatch: %s!=%s. bop and eop intervals must generate lists of" \
        " same length" % (len(bop_dates), len(eop_dates))

    return [
        (bop, eop) for bop, eop in zip(bop_dates, eop_dates)
    ]
