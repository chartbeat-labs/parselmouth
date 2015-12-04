#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Google DFP Utils
"""

# Future-proof
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

# Standard Library Imports
import logging
from datetime import datetime

# Third Party Library Imports
import pytz

# Parselmouth Imports
from parselmouth.delivery import Campaign
from parselmouth.delivery import Creative
from parselmouth.delivery import Cost
from parselmouth.delivery import DeliveryMeta
from parselmouth.delivery import Goal
from parselmouth.delivery import LineItem
from parselmouth.delivery import Stats
from parselmouth.adapters.dfp.constants import SELL_TYPE_MAP
from parselmouth.adapters.dfp.targeting_utils import transform_targeting_data_from_dfp
from parselmouth.adapters.dfp.targeting_utils import transform_targeting_data_to_dfp


def dfp_date_to_datetime(dfp_date_dict):
    """
    Convert a DFP dictionary representation of a date into a native
    python datetime object

    @param dfp_date_dict: dict, dictionary representation of a date
    @return: datetime.datetime, native datetime object of the input date
    """

    # Extract
    year = dfp_date_dict['date']['year']
    month = dfp_date_dict['date']['month']
    day = dfp_date_dict['date']['day']
    hour = dfp_date_dict['hour']
    minute = dfp_date_dict['minute']
    second = dfp_date_dict['second']
    timezone_id = dfp_date_dict['timeZoneID']

    # Validate and cast
    year = int(year)
    month = int(month)
    day = int(day)
    hour = int(hour)
    minute = int(minute)
    second = int(second)
    tzinfo = pytz.timezone(timezone_id)

    return datetime(
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        second=second,
        tzinfo=tzinfo
    )


def datetime_to_dfp_date(dt):
    """
    Convert datetime to dfp style date. If there is no tz
    UTC is assumed

    @param dt: datetime
    @return: dict
    """
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=pytz.utc)

    dfp_date = {
        'timeZoneID': str(dt.tzinfo),
        'date': {
            'year': dt.year,
            'day': dt.day,
            'month': dt.month,
        },
        'second': dt.second,
        'minute': dt.minute,
        'hour': dt.hour,
    }
    return dfp_date


def _get_dfp_dates_from_object(dfp_dict):
    """
    Helper function for extracting dfp datetimes from DFP responses

    @param dfp_dict: dictionary with one of the keys `startDateTime`,
        `endDateTime`, `lastModifiedDateTime`
    @return: (start_date, end_date, last_modified_date)
    """

    start_datetime_dict = dfp_dict.get('startDateTime')
    if start_datetime_dict:
        start_datetime = dfp_date_to_datetime(start_datetime_dict)
    else:
        start_datetime = None

    end_datetime_dict = dfp_dict.get('endDateTime')
    if end_datetime_dict:
        end_datetime = dfp_date_to_datetime(end_datetime_dict)
    else:
        end_datetime = None

    last_modified_datetime = \
        dfp_date_to_datetime(dfp_dict.get('lastModifiedDateTime'))

    return (start_datetime, end_datetime, last_modified_datetime)


def transform_campaign_from_dfp(order):
    """
    Convert dictionary-representation for a SUDS order object into a
    Parselmouth representation of an order
    @param order: dict, dictionary-representation of a DFP SUDS response
        for a single order
    @return: parselmouth.delivery.Campaign
    """
    # Sanitize and cast inputs
    start_datetime, end_datetime, last_modified_datetime = \
        _get_dfp_dates_from_object(order)

    stats = Stats(
        impressions=order.get('totalImpressionsDelivered'),
        clicks=order.get('totalClicksDelivered')
    )
    total_budget = Cost(
        budget_micro_amount=order['totalBudget']['microAmount'],
        budget_currency_code=order['totalBudget']['currencyCode']
    )

    return Campaign(
        advertiser_id=order['advertiserId'],
        agency_id=order.get('agencyId'),
        creator_id=order['creatorId'],
        currency_code=order['currencyCode'],
        end=end_datetime,
        external_campaign_id=order['externalOrderId'],
        id=order['id'],
        last_modified=last_modified_datetime,
        last_modified_by=order['lastModifiedByApp'],
        name=order['name'],
        start=start_datetime,
        status=order['status'],
        stats=stats,
        total_budget=total_budget,
    )


def transform_campaign_to_dfp(campaign):
    """
    Transform a Campaign delivery object into
    a dictionary that will be accepted by dfp,

    @param campaign: Campaign
    @return: dict
    """
    return {
        'id': campaign.id,
        'name': campaign.name,
        'advertiserId': campaign.advertiser_id,
        'creatorId': campaign.creator_id,
        'status': campaign.status,
        'currencyCode': campaign.currency_code,
        'startDateTime': datetime_to_dfp_date(campaign.start),
        'endDateTime': datetime_to_dfp_date(campaign.end),
        'lastModifiedDateTime': datetime_to_dfp_date(campaign.last_modified),
        'lastModifiedByApp': campaign.last_modified_by,
        'totalBudget': {
            'microAmount': campaign.total_budget.budget_micro_amount,
            'currencyCode': campaign.total_budget.budget_currency_code,
        },
        'totalClicksDelivered': campaign.stats.clicks,
        'totalImpressionsDelivered': campaign.stats.impressions,
        'externalOrderId': campaign.external_campaign_id,
    }


def transform_line_item_from_dfp(line_item):
    """
    Convert dictionary-representation for a SUDS line item object into a
    Parselmouth representation of a Line Item

    @param order: dict, dictionary-representation of a DFP SUDS response
        for a single line item
    @return: parselmouth.delivery.LineItem
    """
    # Sanitize and cast inputs
    start_datetime, end_datetime, last_modified_datetime = \
        _get_dfp_dates_from_object(line_item)

    _delivery = line_item.get('deliveryIndicator', {})
    _stats = line_item.get('stats', {})
    stats = Stats(
        impressions=_stats.get('impressionsDelivered', 0),
        clicks=_stats.get('clicksDelivered', 0),
        video_starts=_stats.get('videoStartsDelivered', 0),
        video_completions=_stats.get('videoCompletionsDelivered', 0)
    )
    delivery_meta = DeliveryMeta(
        stats=stats,
        delivery_rate_type=line_item.get('deliveryRateType'),
        actual_delivery_percent=_delivery.get('actualDeliveryPercentage', 0),
        expected_delivery_percent=_delivery.get('expectedDeliveryPercentage', 0)
    )

    budget = Cost(
        budget_micro_amount=line_item['budget']['microAmount'],
        budget_currency_code=line_item['budget']['currencyCode']
    )
    cost_per_unit = Cost(
        budget_micro_amount=line_item['costPerUnit']['microAmount'],
        budget_currency_code=line_item['costPerUnit']['currencyCode']
    )
    value_cost_per_unit = Cost(
        budget_micro_amount=line_item['valueCostPerUnit']['microAmount'],
        budget_currency_code=line_item['valueCostPerUnit']['currencyCode']
    )
    primary_goal = Goal(
        goal_type=line_item['primaryGoal']['goalType'],
        unit_type=line_item['primaryGoal']['unitType'],
        units=int(line_item['primaryGoal']['units'])
    )

    targeting = transform_targeting_data_from_dfp(
        line_item['targeting'],
    )

    return LineItem(
        budget=budget,
        cost_per_unit=cost_per_unit,
        cost_type=line_item['costType'],
        delivery=delivery_meta,
        end=end_datetime,
        id=line_item['id'],
        last_modified=last_modified_datetime,
        last_modified_by=line_item['lastModifiedByApp'],
        type=SELL_TYPE_MAP.get(line_item['lineItemType']),
        name=line_item['name'],
        campaign_id=line_item['orderId'],
        campaign_name=line_item['orderName'],
        primary_goal=primary_goal,
        start=start_datetime,
        status=line_item['status'],
        targeting=targeting,
        value_cost_per_unit=value_cost_per_unit,
        creative_placeholder=line_item.get('creativePlaceholders'),
        target_platform=line_item.get('targetPlatform'),
    )


def _sell_type_reverse_lookup(line_item):
    """
    Get the dfp name for the given sell type

    @param line_item: LineItem
    @return: str
    """
    for dfp_type, native_type in SELL_TYPE_MAP.items():
        if line_item.type == native_type:
            return dfp_type

    return (line_item.type or '').upper()


def transform_line_item_to_dfp(line_item):
    """
    Transform a LineItem delivery object into
    a dictionary that will be accepted by dfp,

    @param line_item: LineItem
    @return: dict
    """
    return {
        'id': line_item.id,
        'name': line_item.name,
        'orderId': line_item.campaign_id,
        'orderName': line_item.campaign_name,
        'lineItemType': _sell_type_reverse_lookup(line_item),
        'costType': line_item.cost_type,
        'startDateTime': datetime_to_dfp_date(line_item.start),
        'endDateTime': datetime_to_dfp_date(line_item.end),
        'lastModifiedDateTime': datetime_to_dfp_date(line_item.last_modified),
        'lastModifiedByApp': line_item.last_modified_by,
        'budget': {
            'microAmount': "%.0f" % line_item.budget.budget_micro_amount,
            'currencyCode': line_item.budget.budget_currency_code,
        },
        'valueCostPerUnit': {
            'microAmount': "%.0f" % line_item.value_cost_per_unit.budget_micro_amount,
            'currencyCode': line_item.value_cost_per_unit.budget_currency_code,
        },
        'costPerUnit': {
            'microAmount': "%.0f" % line_item.cost_per_unit.budget_micro_amount,
            'currencyCode': line_item.cost_per_unit.budget_currency_code,
        },
        'primaryGoal': {
            'goalType': line_item.primary_goal.goal_type,
            'unitType': line_item.primary_goal.unit_type,
            'units': "%.0f" % line_item.primary_goal.units,
        },
        'creativePlaceholders': line_item.creative_placeholder,
        'stats': {
            'impressionsDelivered': line_item.delivery.stats.impressions,
            'clicksDelivered': line_item.delivery.stats.clicks,
            'videoStartsDelivered': line_item.delivery.stats.video_starts,
            'videoCompletionsDelivered': line_item.delivery.stats.video_completions,
        },
        'deliveryRateType': line_item.delivery.delivery_rate_type,
        'targetPlatform': line_item.target_platform,
        'targeting': transform_targeting_data_to_dfp(line_item.targeting),
        'status': line_item.status,
    }


def transform_forecast_line_item_to_dfp(line_item,
                                        use_start=False,
                                        preserve_id=False):
    """
    Transform a Line Item delivery object into
    a dictionary that will be accepted by dfp
    availability check

    @param line_item: LineItem
    @param use_start: bool
    @param preserve_id: bool, communicate the id of the line item being
        forecasted to DFP. This is used in the case where we want to get
        a forecast on a line item in flight. This way, a domain doesn't
        need to have enough spare inventory to accommodate the two line
        items simultaneously. NOTE: If this is true then use_start is
        necessarily true.
    @return: dict
    """
    assert line_item.type
    assert line_item.cost_type
    assert line_item.end
    # Inventory targeting is required for availability checks
    assert line_item.targeting.inventory

    dfp_doc = {
        'lineItemType': _sell_type_reverse_lookup(line_item),
        'costType': line_item.cost_type,
        'endDateTime': datetime_to_dfp_date(line_item.end),
        'targeting': transform_targeting_data_to_dfp(line_item.targeting),
    }

    if preserve_id:
        assert use_start
        if not line_item.id:
            logging.warning((
                "This line item (%s) does not have an existing id to "
                "query DFP with"
            ), line_item.id)
        elif not line_item.campaign_id:
            logging.warning((
                "This line item (%s) does not have an existing order "
                "id to query DFP with"
            ), line_item.id)
        else:
            # Set the existing DFP ids associating this line item object
            # with the line item and order already booked in DFP
            dfp_doc['id'] = line_item.id
            dfp_doc['orderId'] = line_item.campaign_id

    # indicate whether to check for immediate availability or not
    if use_start:
        assert line_item.start

        dfp_doc['startDateTimeType'] = 'USE_START_DATE_TIME'
        dfp_doc['startDateTime'] = datetime_to_dfp_date(line_item.start)
    else:
        dfp_doc['startDateTimeType'] = 'IMMEDIATELY'

    if line_item.creative_placeholder:
        dfp_doc['creativePlaceholders'] = line_item.creative_placeholder

    if line_item.primary_goal:
        dfp_doc['primaryGoal'] = {
            'goalType': line_item.primary_goal.goal_type,
            'unitType': line_item.primary_goal.unit_type,
            'units': line_item.primary_goal.units,
        }
    else:
        dfp_doc['primaryGoal'] = {
            'units': 100,
            'unitType': 'IMPRESSIONS'
        }

    if line_item.target_platform:
        dfp_doc['targetPlatform'] = line_item.target_platform

    return dfp_doc


def transform_creative_from_dfp(creative):
    """
    Convert dictionary-representation for a SUDS creative object into a
    Parselmouth representation of a Creative
    @param order: dict, dictionary-representation of a DFP SUDS response
        for a single creative
    @return: parselmouth.delivery.Creative
    """

    _, _, last_modified_datetime = _get_dfp_dates_from_object(creative)

    return Creative(
        advertiser_id=creative['advertiserId'],
        id=creative['id'],
        last_modified=last_modified_datetime,
        name=creative['name'],
        preview_url=creative['previewUrl'],
        size=creative['size']
    )


def transform_creative_to_dfp(creative):
    """
    Transform a Creative delivery object into
    a dictionary that will be accepted by dfp,

    @param creative: Creative
    @return: dict
    """
    return {
        'id': creative.id,
        'advertiserId': creative.advertiser_id,
        'name': creative.name,
        'previewUrl': creative.preview_url,
        'size': creative.size,
        'lastModifiedDateTime': datetime_to_dfp_date(creative.last_modified),
    }
