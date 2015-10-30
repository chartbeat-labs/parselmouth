#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Parselmouth utilities - check_equal
"""

# Future-proof
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


def check_equal(obj1, obj2):
    """
    Check if two objects are equivalent

    @param obj1
    @parma obj2
    @return: bool
    """
    if type(obj1) != type(obj2):
        return False

    if isinstance(obj1, dict):
        if sorted(obj1.keys()) != sorted(obj2.keys()):
            return False

        for _key in obj1.keys():
            if not check_equal(obj1[_key], obj2[_key]):
                return False

    elif isinstance(obj1, list):
        if len(obj1) != len(obj2):
            return False

        for item1 in obj1:
            is_match = False
            for item2 in obj2:
                if check_equal(item1, item2):
                    is_match = True

            if not is_match:
                return False
    else:
        return obj1 == obj2

    return True
