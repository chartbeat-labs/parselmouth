#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Parselmouth - Delivery Models
Base Interfaces for delivery items
"""

# Future-proof
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

# Standard Library Imports
from datetime import datetime

# Parselmouth Imports
from parselmouth.targeting import TargetingData
from parselmouth.model import ObjectModel


class Cost(ObjectModel):
    """
    Container class for modeling Campaign and Line Item Budgets and
    Costs
    """

    def __init__(self,
                 budget_micro_amount,
                 budget_currency_code):
        """
        @param budget_micro_amount: str|int
        @param budget_currency_code: str
        """
        self.budget_micro_amount = float(budget_micro_amount)
        self.budget_currency_code = budget_currency_code


class Goal(ObjectModel):
    """
    Container class for modeling delivery goals
    """

    def __init__(self,
                 goal_type=None,
                 unit_type=None,
                 units=None):

        self.goal_type = goal_type
        self.unit_type = unit_type
        self.units = units


class Stats(ObjectModel):
    """
    Class for tracking a container's delivery performance
    """

    def __init__(self,
                 impressions,
                 clicks,
                 video_starts=0,
                 video_completions=0,
                 **kwargs):
        """
        @param impressions: str|int, number of impressions delivered
        @param clicks: str|int, number of clicks delivered
        """
        self.impressions = int(impressions)
        self.clicks = int(clicks)
        self.video_starts = int(video_starts)
        self.video_completions = int(video_completions)
        if self.clicks and self.impressions:
            self.click_through_rate = self.clicks / self.impressions
        else:
            self.click_through_rate = 0


class DeliveryMeta(ObjectModel):
    """
    Class for tracking delivery expectations
    """

    def __init__(self,
                 stats,
                 delivery_rate_type,
                 actual_delivery_percent,
                 expected_delivery_percent,
                 **kwargs):
        """
        @param stats: parselmouth.delivery.Stats
        @param delivery_rate_type: str
        @param actual_delivery_percent: str|float
        @param expected_delivery_percent: str|float
        """

        assert isinstance(stats, Stats)

        self.stats = stats
        self.delivery_rate_type = delivery_rate_type
        self.actual_delivery_percent = float(actual_delivery_percent)
        self.expected_delivery_percent = float(expected_delivery_percent)
        if actual_delivery_percent > 0 and expected_delivery_percent > 0:
            self.pace = \
                self.actual_delivery_percent / self.expected_delivery_percent
        else:
            self.pace = 0


class Creative(ObjectModel):
    """
    Abstract Class for creative containers
    A creative is a specific advertisement, such as an image file, video
    file, or other content that gets delivered to end users. A creative
    can be associated with one or more line items.
    """

    def __init__(self,
                 advertiser_id=None,
                 type=None,
                 id=None,
                 last_modified=None,
                 name=None,
                 preview_url=None,
                 size=None):

        assert isinstance(last_modified, datetime) or last_modified is None

        self.advertiser_id = advertiser_id
        self.type = type
        self.id = id
        self.last_modified = last_modified
        self.name = name
        self.preview_url = preview_url
        self.size = size


class LineItem(ObjectModel):
    """
    Abstract Class for Line Items
    A line item represents an atomically purchased set of ads over a
    period of time. An individual line item has its own targeting,
    impression goal, and cost. This is most basic unit that is purchased
    when building an ad campaign for a particular campaign. Every line
    item is contained within a campaign or order. A line item contains
    one or more creatives.
    """

    def __init__(self,
                 budget=None,
                 cost_per_unit=None,
                 cost_type=None,
                 delivery=None,
                 domain=None,
                 end=None,
                 id=None,
                 last_modified=None,
                 last_modified_by=None,
                 type=None,
                 name=None,
                 campaign_id=None,
                 campaign_name=None,
                 primary_goal=None,
                 start=None,
                 status=None,
                 targeting=None,
                 value_cost_per_unit=None,
                 creative_placeholder=None,
                 target_platform=None):

        assert isinstance(start, datetime) or start is None
        assert isinstance(last_modified, datetime) or last_modified is None
        assert isinstance(end, datetime) or end is None
        assert isinstance(budget, Cost) or budget is None
        assert isinstance(cost_per_unit, Cost) or cost_per_unit is None
        assert isinstance(value_cost_per_unit, Cost) or value_cost_per_unit is None
        assert isinstance(primary_goal, Goal) or primary_goal is None
        assert isinstance(delivery, DeliveryMeta) or delivery is None
        assert isinstance(targeting, TargetingData) or targeting is None

        if start and end:
            assert start <= end

        self.budget = budget
        self.cost_per_unit = cost_per_unit
        self.cost_type = cost_type
        self.delivery = delivery
        self.domain = domain
        self.end = end
        self.id = id
        self.last_modified = last_modified
        self.last_modified_by = last_modified_by
        self.type = type
        self.name = name
        self.campaign_id = campaign_id
        self.campaign_name = campaign_name
        self.primary_goal = primary_goal
        self.start = start
        self.status = status
        self.targeting = targeting
        self.value_cost_per_unit = value_cost_per_unit
        self.creative_placeholder = creative_placeholder
        self.target_platform = target_platform

    @property
    def stats(self):
        """
        Proxy to the self.delivery.stats object that reports a line
        item's delivered impressions and clicks. This is mainly here so
        we can treat Campaign.stats and LineItem.stats the same...
        Makes self.delivery.stats accessible by just self.stats
        """
        return self.delivery.stats


class Campaign(ObjectModel):
    """
    Abstract Class for Campaigns
    A campaign is an object with a start and end date, and is a
    container for one or more line items.
    """

    def __init__(self,
                 advertiser_id=None,
                 agency_id=None,
                 creator_id=None,
                 currency_code=None,
                 domain=None,
                 end=None,
                 external_campaign_id=None,
                 id=None,
                 last_modified=None,
                 last_modified_by=None,
                 name=None,
                 start=None,
                 status=None,
                 stats=None,
                 total_budget=None,
                 line_items=None):

        assert isinstance(start, datetime) or start is None
        assert isinstance(last_modified, datetime) or last_modified is None
        assert isinstance(end, datetime) or end is None
        assert isinstance(stats, Stats) or stats is None

        if start and end:
            assert start <= end

        self.advertiser_id = advertiser_id
        self.agency_id = agency_id
        self.creator_id = creator_id
        self.currency_code = currency_code
        self.domain = domain
        self.end = end
        self.external_campaign_id = external_campaign_id
        self.id = id
        self.last_modified = last_modified
        self.last_modified_by = last_modified_by
        self.name = name
        self.start = start
        self.status = status
        self.stats = stats
        self.total_budget = total_budget
        self.line_items = line_items
