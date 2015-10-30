#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Parselmouth

This package serves as the base interface from third-party ad servers to
python object-oriented classes. This file exposes only the objects
clients should use.

Parselmouth should be imported in the following way:
    `from parselmouth import Parselmouth`
"""

# Future-proof
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

# Expose package interfaces
__all__ = ['Parselmouth', 'ParselmouthException']

from parselmouth.base import Parselmouth
from parselmouth.exceptions import ParselmouthException
