#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Parselmouth Abstract Interface
"""

# Future-proof
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

# Standard Library Imports
from abc import ABCMeta
from abc import abstractmethod


class AbstractInterface(object):
    """
    Abstract Interface to all Ad Services

    This class outlines functions required to be implemented by ad
    services. If that functionality is not provided by a specific ad
    service then it needs to raise `NotImplementedError`.

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
    def get_network_timezone(self):
        pass

    @abstractmethod
    def get_campaign(self, creative_id):
        pass

    @abstractmethod
    def get_campaigns(self):
        pass

    @abstractmethod
    def get_line_item(self, line_item_id):
        pass

    @abstractmethod
    def get_line_items(self):
        pass

    @abstractmethod
    def get_campaign_line_items(self, campaign_id):
        pass

    @abstractmethod
    def get_line_item_available_inventory(self, line_item):
        pass

    @abstractmethod
    def get_advertisers(self, line_item):
        pass

    @abstractmethod
    def get_creative(self, creative_id):
        pass

    @abstractmethod
    def get_creatives(self):
        pass

    @abstractmethod
    def get_line_item_creatives(self, line_item_id):
        pass

    @abstractmethod
    def get_geography_targets(self):
        pass

    @abstractmethod
    def get_adunit_targets(self):
        pass

    @abstractmethod
    def get_custom_targets(self):
        pass

    @abstractmethod
    def get_line_item_report(self):
        pass

    @abstractmethod
    def update_line_items(self):
        pass

    @abstractmethod
    def create_custom_target(self):
        pass
