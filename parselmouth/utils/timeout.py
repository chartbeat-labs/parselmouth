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

# Local Package Imports
from parselmouth.exceptions import ParselmouthTimeout


class Timeout(object):
    """
    Timeout context manager class for wrapping function calls that may
    not complete.

    This code is adapted from the gist available here:
        https://gist.github.com/glenfant/7501911

    Warnings:
    - This does not work with Windows that does not handle the signals we need.
    - This is not thead safe since the signal will get caught by a random thread.
    - Tested on MacOSX with Python 2.6, 2.7 and 3.3 (may or not work eslsewhere)
    """

    def __init__(self, timeout, swallow_exception=False):
        """
        @param timeout: int, seconds enabled for processing the block
            under our context manager
        @param swallow_exception: bool, do not raise the exception on
            timeout
        """
        self._timeout = timeout
        self._swallow_exception = swallow_exception

    def __enter__(self):
        self.setup_timeout()

    def __exit__(self, exc_type, value, traceback):
        # Always cancel immediately, since we're done
        try:
            self.cancel_timeout()
        except ParselmouthTimeout:
            # Weird case: we're done with the with body, but now the
            # alarm is fired.  We may safely ignore this situation and
            # consider the body done.
            pass

        # __exit__ may return True to supress further exception
        # handling.  We don't want to suppress any exceptions here,
        # since all errors should just pass through, ParselmouthTimeout
        # being handled normally to the invoking context.
        if exc_type is ParselmouthTimeout and self._swallow_exception:
            return True
        return False

    def handle_timeout(self, signum, frame):
        raise ParselmouthTimeout(
            '%s exceeded maximum timeout value (%d seconds).' % (
                frame.f_code.co_name,
                self._timeout
            )
        )

    def setup_timeout(self):
        """
        Sets up an alarm signal and a signal handler that raises a
        ParselmouthTimeout after the timeout amount (expressed in
        seconds).
        """
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self._timeout)

    def cancel_timeout(self):
        """
        Removes the death penalty alarm and puts back the system into
        default signal handling.
        """
        signal.alarm(0)
        signal.signal(signal.SIGALRM, signal.SIG_DFL)
