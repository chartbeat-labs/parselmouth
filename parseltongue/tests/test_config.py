#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Acceptance checks to determine if API responses are compatible with the
current interface implementation
"""

# Future-proof
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

# Standard Library Imports
import os.path
import unittest

# Parseltongue imports
from parseltongue import __file__ as PARSELTOUNGE_PACKAGE_PATH
from parseltongue.config import DFPConfig
from parseltongue.exceptions import ParseltongueException


def _verify_credentials(config):
    """
    Helper for validating that correct credentials were loaded into the
    config object

    @param config: child(parseltongue.config.ParseltongueConfig)
    @raises: AssertionError if credentials don't match expected
    """
    assert config.client_id == 'ID'
    assert config.client_secret == 'SECRET'
    assert config.refresh_token == 'REFRESH_TOKEN'
    assert config.application_name == 'APPLICATION_NAME'
    assert config.network_code == 'NETWORK_CODE'


class TestParseltoungDFPConfig(unittest.TestCase):

    def setUp(self):
        # Dummy credentials
        self.client_id='ID'
        self.client_secret='SECRET'
        self.refresh_token='REFRESH_TOKEN'
        self.application_name='APPLICATION_NAME'
        self.network_code='NETWORK_CODE'

        # Dummy credentials file
        self.config_path = os.path.join(
            os.path.join(
                os.path.dirname(os.path.realpath(PARSELTOUNGE_PACKAGE_PATH)),
                "tests"
            ),
            "test_config.yaml"
        )

    def test_basic_config(self):
        config = DFPConfig(
            client_id=self.client_id,
            client_secret=self.client_secret,
            refresh_token=self.refresh_token,
            application_name=self.application_name,
            network_code=self.network_code,
        )
        _verify_credentials(config)

    def test_config_load(self):
        config = DFPConfig(config_path=self.config_path)
        _verify_credentials(config)

    def test_invalid_config_param_combination(self):
        with self.assertRaises(ParseltongueException):
            config = DFPConfig(
                client_id=self.client_id,
                client_secret=self.client_secret,
                refresh_token=self.refresh_token,
                application_name=self.application_name,
                network_code=self.network_code,
                config_path=self.config_path,
            )

    def test_no_config_params(self):
        with self.assertRaises(ParseltongueException):
            config = DFPConfig()



if __name__ == '__main__':
    unittest.main()
