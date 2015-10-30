#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Parseltongue

This package serves as the base interface from third-party ad servers to
python object-oriented classes. This file exposes only the objects
clients should use.

Parseltongue should be imported in the following way:
    `from parseltongue import Parseltongue`
"""

# Future-proof
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

# Expose package interfaces
__all__ = ['Parseltongue', 'ParseltongueException']

from parseltongue.base import Parseltongue
from parseltongue.exceptions import ParseltongueException
