#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Parseltongue - Configuration Utilities

These configuration utilities outline the way configurations may be
loaded into Parseltongue for authenticating different advertising client
APIs
"""

# Future-proof
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

# Standard Library Imports
from abc import ABCMeta
from abc import abstractmethod

# Third Party Imports
import yaml

# Parseltongue Imports
from parseltongue.exceptions import ParseltongueException


class ParseltongueConfig(object):
    """
    Abstract Configuration Container

    This class outlines an interface for loading provider-specific
    configurations. These classes can be extended to allow for alternate
    data sources such as an external credential database instead of a
    file for instance.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self):
        pass

    def __str__(self):
        """
        Human readable representation of this object
        @return: str
        """
        return "{class_name}({vars})".format(
            class_name=self.__class__.__name__,
            vars=str(vars(self))
        )

    def load_config_from_file(self, config_path):
        raise NotImplementedError(
            "This method must be written for this config container!"
        )

    def load_config_from_external_source(self, *args, **kwargs):
        raise NotImplementedError(
            "This method must be written for this config container!"
        )


class DFPConfig(ParseltongueConfig):
    """
    Configuration container specific to the DFP API
    """

    def __init__(self,
                 client_id=None,
                 client_secret=None,
                 refresh_token=None,
                 application_name=None,
                 network_code=None,
                 config_path=None):

        _credentials_manually_entered = all([
            client_id,
            client_secret,
            refresh_token,
            application_name,
            network_code
        ])

        if _credentials_manually_entered and not config_path:
            self.client_id = client_id
            self.client_secret = client_secret
            self.refresh_token = refresh_token
            self.network_code = network_code
            self.application_name = application_name
        elif not _credentials_manually_entered and config_path:
            self.load_config_from_file(config_path)
        else:
            raise ParseltongueException("Unexpected combination of credentials")

    def load_config_from_file(self, config_path):

        with open(config_path, 'r') as infile:
            config_dict = yaml.load(infile)

        self.client_id = config_dict['credentials']['client_id']
        self.client_secret = config_dict['credentials']['client_secret']
        self.refresh_token = config_dict['credentials']['refresh_token']
        self.network_code = config_dict['credentials']['network_code']
        self.application_name = config_dict['application_name']
