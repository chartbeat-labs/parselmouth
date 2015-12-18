#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Parselmouth - Exceptions
"""

# Future-proof
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

# Third Party Library Imports
from stopit import TimeoutException


class ParselmouthException(Exception):
    """ Base Exception for the Parselmouth project
    """
    pass

class ParselmouthNetworkError(Exception):
    """ Base Exception for the Parselmouth Network Errors
    """
    pass

class ParselmouthTimeout(TimeoutException):
    """
    Raised when the block under context management takes longer to
    complete than the allowed maximum timeout value.
    """
    pass
