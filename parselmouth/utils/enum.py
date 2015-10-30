#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Parselmouth utilities - Enum
"""

# Future-proof
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


class Enum(set):
    """
    Usage:
    MyEnum = Enum([
    'foo',
    'bar',
    ])

    Then you can do:
    MyEnum.foo and MyEnum.bar
    """
    def __getattr__(self, name):
        if name in self:
            return name
        raise KeyError('invalid name: %s' % name)

    def __getitem__(self, name):
        return self.__getattr__(name)
