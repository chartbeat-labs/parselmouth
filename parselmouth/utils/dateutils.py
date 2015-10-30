#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Parselmouth utilities - Date Utilites
"""

# Future-proof
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

# Standard Library Imports
import time
from datetime import timedelta


def align_to_day(d, fix_utc_offset=False):
    """Align a datetime to a day boundary.

    @param d: datetime to align
    @param fix_utc_offset: bool, converts `d` from America/New_York to UTC
    @return datetime
    """
    if not d:
        return d

    hour_offset = 0
    if fix_utc_offset:
        hour_offset = get_et_utc_offset()

    return d - timedelta(hours=d.hour + hour_offset,
                         minutes=d.minute,
                         seconds=d.second,
                         microseconds=d.microsecond)


def get_et_utc_offset():
    """
    Returns number of hours we need to substract from a timestamp
    to account for utc/et issues in our code.
    """
    if is_localtime_dst():
        return 4
    return 5


def is_localtime_dst():
    """
    Check if the local time is using daylight savings.

    @return: bool
    """
    current_time = time.localtime()
    return True if current_time.tm_isdst else False
