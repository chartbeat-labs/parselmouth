#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Parselmouth utilities
"""

# Future-proof
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

# Standard Library Imports
import signal

# Third Party Library Imports
import stopit

# Local Package Imports
from parselmouth.exceptions import ParselmouthTimeout


class Timeout(stopit.ThreadingTimeout):
    pass
