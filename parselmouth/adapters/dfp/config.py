#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Parselmouth - DFP Configuration

These configuration utilities outline the way configurations may be
loaded into Parselmouth for authenticating different advertising client
APIs
"""

# Future-proof
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

# Third Party Imports
import yaml

# Parselmouth Imports
from parselmouth.exceptions import ParselmouthException
from parselmouth.adapters.abstract_config import AbstractConfig


class DFPConfig(AbstractConfig):
    """
    Configuration container specific to the DFP API
    """

    _credentials = {
        'client_id': None,
        'client_secret': None,
        'refresh_token': None,
        'application_name': None,
        'network_code': None,
    }
    """
    dict, key/value pairs required to connect to DFP service
    """

    def validate_credentials(self):
        """
        Make sure all credentials have been populated correctly
        """
        for _key, _val in self._credentials.items():
            if _val is None:
                raise ParselmouthException("{} field is missing".format(_key))

    def get_credentials_arguments(self):
        """
        @return: dict
        """
        return self._credentials

    def load_config_from_file(self, provider_name, config_path):

        with open(config_path, 'r') as infile:
            config_dict = yaml.load(infile)

        self._credentials = {
            'client_id': config_dict[provider_name]['client_id'],
            'client_secret': config_dict[provider_name]['client_secret'],
            'refresh_token': config_dict[provider_name]['refresh_token'],
            'network_code': config_dict[provider_name]['network_code'],
            'application_name': config_dict[provider_name]['application_name'],
        }

    def load_config_from_external_source(self,
                                         client_id,
                                         client_secret,
                                         refresh_token,
                                         application_name,
                                         network_code):
        """
        https://developers.google.com/doubleclick-publishers/docs/authentication

        @param client_id: str
        @param client_secret: str
        @param refresh_token: str
        @param application_name: str
        @param network_code: str
        @param version: str
        """
        self._credentials = {
            'client_id': client_id,
            'client_secret': client_secret,
            'refresh_token': refresh_token,
            'application_name': application_name,
            'network_code': network_code,
        }
