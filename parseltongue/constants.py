#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Parseltongue - Contants

Constants related to Parseltongue and the providers that use it
"""

# Future-proof
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

# Parseltongue Imports
from parseltongue.utils.enum import Enum


ParseltongueProviders = Enum([
    'google_dfp_premium',
    'google_dfp_small_business',
])
"""
Enum, List of providers that Parseltongue interfaces with
"""

ParseltongueTargetTypes = Enum([
    'adunit',
    'geography',
    'demographics',
    'ad_position',
    'custom',
])
"""
Enum, list of target types
"""

TechnologyTargetTypes = Enum([
    'bandwidth_group',
    'browser',
    'browser_language',
    'device_capability',
    'device_category',
    'device_manufacturer',
    'mobile_carrier',
    'mobile_device',
    'mobile_device_submodel',
    'operating_system',
    'operating_system_version',
])
"""
Enum, list of valid technology types for targeting
"""


ParseltongueReportMetrics = Enum([
    'ad_impressions',
    'ad_viewable_impressions',
    'line_item_id',
    'line_item_name',
    'delivery_percentage',
])
"""
Enum, metrics which can be pulled from ad provider reports
"""


AdProviderSellTypes = Enum([
    'sponsorship',
    'standard',
    'network',
    'house',
    'price_priority',
])
"""
Enum, sales categories for campaigns
"""


MAX_REQUEST_ATTEMPTS = 3
