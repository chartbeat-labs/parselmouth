#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Parselmouth - Configuration Utilities

These configuration utilities outline the way configurations may be
loaded into Parselmouth for authenticating different advertising client
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

# Parselmouth Imports
from parselmouth.exceptions import ParselmouthException
from parselmouth.constants import ParselmouthProviders

# Parselmouth Imports - Adapter Imports
from parselmouth.adapters.dfp.config import DFPConfig


class ParselmouthConfig(object):
    """
    Abstract Configuration Container

    This class outlines an interface for loading provider-specific
    configurations. These classes can be extended to allow for alternate
    data sources such as an external credential database instead of a
    file for instance.
    """

    ProviderConfigInterfaceMap = {
        ParselmouthProviders.google_dfp_premium: DFPConfig,
        ParselmouthProviders.google_dfp_small_business: DFPConfig,
    }
    """
    dict, mapping between ad service providers and their configuration
    containers
    NOTES:
        * This doesn't serve much purpose right now since all we support
            is DFP...
    """

    def __init__(self,
                 provider_name,
                 config_path=None,
                 **kwargs):
        """
        @param provider_name: ParselmouthProviders
        """
        self.provider_name = provider_name
        self.provider_config = self.get_config_for_provider(
            self.provider_name,
        )

        if config_path:
            try:
                self.provider_config.load_config_from_file(
                    self.provider_name, config_path,
                )
            except:
                raise ParselmouthException("Invalid credential file.")
        else:
            try:
                self.provider_config.load_config_from_external_source(**kwargs)
            except Exception:
                raise ParselmouthException("Invalid credential arguments.")

        self.provider_config.validate_credentials()

    def __str__(self):
        """
        Human readable representation of this object
        @return: str
        """
        return "{class_name}({vars})".format(
            class_name=self.__class__.__name__,
            vars=str(vars(self))
        )

    @classmethod
    def get_config_for_provider(cls, provider_name):
        """
        Staticmethod, returns the interface class for a given ad service
        provider name

        @param provider_name: str, one of enum
            parselmouth.constants.ParselmouthProviders
        @return: descendant of
            parselmouth.adapters.abstract_config.AbstractConfig
        """
        client_config = cls.ProviderConfigInterfaceMap.get(provider_name)
        if not client_config:
            raise ValueError(
                "There is no config interface defined for provider: %s" %
                provider_name
            )
        return client_config()

    def get_credentials_arguments(self):
        """
        @return: dict, dictionary of all values needed to connect
            to the associated ad provider service
        """
        return self.provider_config.get_credentials_arguments()
