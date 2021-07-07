# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


import re
import operator
from datetime import datetime, date

import dateutil
import dateutil.parser
from dateutil.relativedelta import SU, MO, TU, WE, TH, FR, SA
from dateutil.relativedelta import relativedelta

from ..regex import RegexParser


class UnitSplitter(RegexParser):

    compiled_regex = re.compile(
        r'(?P<multiple>[-+]?[0-9]*)?(?P<unit>[a-zA-Z]+)'
    )

    @classmethod
    def make(cls, unit, multiple=None):
        if not multiple or multiple == '+':
            multiple = 1
        elif multiple == '-':
            multiple = -1
        else:
            multiple = int(multiple)
        return multiple, unit


# Units mapped to parameter in relativedelta
UNIT = {
    'y': 'years',
    'm': 'months',
    'w': 'weeks',
    'd': 'days',
    'H': 'hours',
    'M': 'minutes',
    's': 'seconds',
}

# Only allow units we know how to map
UNITS_RGX = r'[{}]'.format(''.join(UNIT.keys()))

WEEKDAY = {
    'SU': SU,
    'MO': MO,
    'TU': TU,
    'WE': WE,
    'TH': TH,
    'FR': FR,
    'SA': SA,
}


def now(utc=False):
    """Make easier to unittest"""
    return datetime.utcnow() if utc else datetime.now()


ISO8601_RGX = (r'(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])'
               r'-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):'
               r'([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-]'
               r'(?:2[0-3]|[01][0-9]):[0-5][0-9])?')
DATE_RGX = (r'(?:[12]\d{3}-(?:0[1-9]|1[0-2])'
            r'-(?:0[1-9]|[12]\d|3[01]))')

INTERVAL_DATE_RGX = (r'(?:today|now|TODAY|NOW|utctoday|utcnow|UTCTODAY|UTCNOW|{}|{})'
                     .format(ISO8601_RGX, DATE_RGX))
RDELTA_RGX = r'[-+]\d*{}'.format(UNITS_RGX)
WEEKDAY_RGX = r'[-+]\d*(?:MO|TU|WE|TH|FR|SA|SU)'


class Endpoint(RegexParser):

    compiled_regex = re.compile(
        (
            r'^(?P<reference>{})?'
            r'\s*(?P<rdelta>{})?\s*'
            r'\s*(?P<weekday>{})?\s*$'
        ).format(INTERVAL_DATE_RGX, RDELTA_RGX, WEEKDAY_RGX)
    )

    @classmethod
    def make(cls, reference=None, rdelta=None, weekday=None):
        kwargs = {}
        if rdelta:
            multiple, unit = UnitSplitter.parse(rdelta)
            kwargs[UNIT[unit]] = multiple
        if weekday:
            multiple, weekday = UnitSplitter.parse(weekday)
        if reference:
            reference = cls.parse_reference(reference)
        if rdelta and weekday:
            rdelta = relativedelta(weekday=WEEKDAY[weekday](multiple),
                                   **kwargs)
        elif rdelta:
            rdelta = relativedelta(**kwargs)
        elif weekday:
            rdelta = relativedelta(weekday=WEEKDAY[weekday](multiple))
        if rdelta and reference:
            return reference + rdelta
        return reference if reference else rdelta

    @staticmethod
    def parse_reference(reference_string):
        reference_string_lower = reference_string.lower()
        if reference_string_lower == 'today':
            return now().date()
        elif reference_string_lower == 'now':
            return now()
        elif reference_string_lower == 'utctoday':
            return now(utc=True).date()
        elif reference_string_lower == 'utcnow':
            return now(utc=True)
        return dateutil.parser.parse(reference_string)


class IntervalFrequency(RegexParser):

    regex = r'\d*{}'.format(UNITS_RGX)

    compiled_regex = re.compile(
        r'^(?:\s*(?P<interval_freq>{})\s*)$'.format(regex)
    )

    @classmethod
    def make(cls, interval_freq):
        multiple, unit = UnitSplitter.parse(interval_freq)
        return relativedelta(**{UNIT[unit]: int(multiple)})


class Interval(RegexParser):

    compiled_regex = re.compile(
        (
            r'^(?P<left>[\[(])\s*(?P<start>{0})'
            r'\s*,\s*'
            r'(?P<end>{0})\s*(?P<right>[)\]])'
            r'(?:\s*\|\s*(?P<interval_freq>{1})\s*)?$'
        ).format(r'.+', IntervalFrequency.regex)
    )

    @staticmethod
    def divisible_by_day(dt):
        seconds = (dt - datetime(1970, 1, 1)).total_seconds()
        return int(seconds) % 86400 == 0

    @staticmethod
    def _should_use_date(dates):
        is_first = (type(dates[0]) is date
                    or Interval.divisible_by_day(dates[0]))
        if len(dates) == 1:
            return is_first
        return is_first and (type(dates[1]) is date
                             or Interval.divisible_by_day(dates[1]))

    @staticmethod
    def to_datetime(dt):
        if type(dt) is datetime:
            return dt
        elif type(dt) is date:
            return datetime.fromordinal(dt.toordinal())
        else:
            raise ValueError('Unrecognized type: {}'.format(type(dt)))

    @staticmethod
    def to_date(dt):
        if type(dt) is datetime:
            return dt.date()
        elif type(dt) is date:
            return dt
        else:
            raise ValueError('Unrecognized type: {}'.format(type(dt)))

    @staticmethod
    def resolve_range(start, end):
        start = Endpoint.parse(start)
        end = Endpoint.parse(end)
        is_start_rel = isinstance(start, relativedelta)
        is_end_rel = isinstance(end, relativedelta)
        assert not (is_start_rel and is_end_rel)
        if not is_start_rel and not is_end_rel:
            return start, end
        if is_start_rel:
            return start + end, end
        return start, start + end

    @classmethod
    def make(cls, start, end, left='[', right=')', interval_freq='d'):

        start, end = cls.resolve_range(start, end)

        interval_freq = IntervalFrequency.parse(interval_freq)
        left_closed = left == '['
        right_closed = right == ']'

        # initialize as datetime for initial operators
        start = cls.to_datetime(start)
        end = cls.to_datetime(end)

        if start < end:
            increment = operator.add
            compare_open = operator.lt
            compare_closed = operator.le
        else:
            increment = operator.sub
            compare_open = operator.gt
            compare_closed = operator.ge

        cur = increment(start, interval_freq)

        if cls._should_use_date([start, cur]):
            start = cls.to_date(start)
            cur = cls.to_date(cur)
            end = cls.to_date(end)
        else:
            start = cls.to_datetime(start)
            cur = cls.to_datetime(cur)
            end = cls.to_datetime(end)

        dates = []

        if left_closed:
            dates.append(start)

        while ((compare_open(cur, end)
                and not right_closed)
               or (compare_closed(cur, end)
                   and right_closed)):
            dates.append(cur)
            cur = increment(cur, interval_freq)

        return dates
