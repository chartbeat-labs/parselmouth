#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Parseltongue - Exceptions
"""

# Future-proof
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


class ParseltongueException(Exception):
    """ Base Exception for the Parseltongue project
    """
    pass

class ParseltongueNetworkError(Exception):
    """ Base Exception for the Parseltongue Network Errors
    """
    pass

class ParseltongueTimeout(ParseltongueNetworkError):
    """
    Raised when the block under context management takes longer to
    complete than the allowed maximum timeout value.
    """
    pass
