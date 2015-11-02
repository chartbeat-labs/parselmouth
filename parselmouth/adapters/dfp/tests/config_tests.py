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

# Parselmouth imports
from parselmouth import __file__ as PARSELTOUNGE_PACKAGE_PATH
from parselmouth.config import ParselmouthConfig
from parselmouth.adapters.dfp.config import DFPConfig
from parselmouth.exceptions import ParselmouthException
from parselmouth.constants import ParselmouthProviders


class TestParselmouthConfig(unittest.TestCase):

    def setUp(self):
        # Dummy credentials
        self.credentials = {
            'client_id': 'ID',
            'client_secret': 'SECRET',
            'refresh_token': 'REFRESH_TOKEN',
            'application_name': 'APPLICATION_NAME',
            'network_code': 'NETWORK_CODE',
        }

        # Dummy credentials file
        self.config_path = os.path.join(
            os.path.dirname(os.path.realpath(PARSELTOUNGE_PACKAGE_PATH)),
            'adapters',
            'dfp',
            'tests',
            'test_config.yaml',
        )

    def test_load_config_from_external_source(self):
        config = DFPConfig()
        config.load_config_from_external_source(
            **self.credentials
        )
        config.validate_credentials()

        self.assertDictEqual(self.credentials, config.get_credentials_arguments())

    def test_load_config_from_file(self):
        config1 = DFPConfig()
        config1.load_config_from_file(
            ParselmouthProviders.google_dfp_premium, self.config_path
        )
        config1.validate_credentials()

        self.assertDictEqual(self.credentials, config1.get_credentials_arguments())

        config2 = DFPConfig()
        config2.load_config_from_file(
            ParselmouthProviders.google_dfp_small_business, self.config_path
        )
        config2.validate_credentials()

        self.assertDictEqual(self.credentials, config2.get_credentials_arguments())

    def test_no_config_params(self):
        with self.assertRaises(ParselmouthException):
            config = ParselmouthConfig(
                ParselmouthProviders.google_dfp_premium,
            )

    def test_config_init(self):
        config1 = ParselmouthConfig(
            ParselmouthProviders.google_dfp_premium,
            config_path=self.config_path,
        )
        self.assertDictEqual(self.credentials, config1.get_credentials_arguments())

        config2 = ParselmouthConfig(
            ParselmouthProviders.google_dfp_premium,
            client_id='ID',
            client_secret='SECRET',
            refresh_token='REFRESH_TOKEN',
            network_code='NETWORK_CODE',
            application_name='APPLICATION_NAME',
        )
        self.assertDictEqual(self.credentials, config2.get_credentials_arguments())


if __name__ == '__main__':
    unittest.main()
