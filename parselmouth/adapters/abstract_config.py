#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Parselmouth Abstract Configuration
"""

# Future-proof
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

# Standard Library Imports
from abc import ABCMeta
from abc import abstractmethod


class AbstractConfig(object):
    """
    Abstract Configuration to all Ad Services

    This class outlines functions required to be implemented by ad
    service configuration classes. This class should serve as a way
    to authenticate to a given ad provider service.
    If that functionality is not provided by a specific ad
    service configuration then it needs to raise `NotImplementedError`.

    Right now most of this functionality follows the DFP implementation.
    It's likely that many of these functions will not be used by other
    ad services.
    """
    __metaclass__ = ABCMeta

    def __repr__(self):
        """
        Human readable representation of this object

        @return: str
        """
        return (
            "{class_name}("
            ")"
        ).format(
            class_name=self.__class__.__name__,
        )

    @abstractmethod
    def validate_credentials(self):
        pass

    @abstractmethod
    def get_credentials_arguments(self):
        pass

    @abstractmethod
    def load_config_from_file(self, config_path):
        pass

    @abstractmethod
    def load_config_from_external_source(self, *args, **kwargs):
        pass
