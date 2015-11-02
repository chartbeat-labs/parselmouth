#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Parselmouth DFP Interface
"""

# Future-proof
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

# Standard Imports
import logging
from datetime import timedelta
from pytz import timezone
from urllib import quote

# Parselmouth Imports
from parselmouth.adapters.abstract_interface import AbstractInterface
from parselmouth.delivery import Campaign
from parselmouth.delivery import LineItem
from parselmouth.exceptions import ParselmouthException
from parselmouth.targeting import AdUnit
from parselmouth.targeting import Custom
from parselmouth.targeting import Geography
from parselmouth.utils.dateutils import align_to_day

# Parselmouth Imports - Local DFP Adapter Imports
from parselmouth.adapters.dfp.constants import DFP_API_VERSION
from parselmouth.adapters.dfp.constants import DFP_QUERY_DEFAULTS
from parselmouth.adapters.dfp.constants import DFP_REPORT_METRIC_MAP
from parselmouth.adapters.dfp.client  import DFPClient
from parselmouth.adapters.dfp.utils import recursive_asdict
from parselmouth.adapters.dfp.delivery_utils import transform_line_item_from_dfp
from parselmouth.adapters.dfp.delivery_utils import transform_line_item_to_dfp
from parselmouth.adapters.dfp.delivery_utils import transform_forecast_line_item_to_dfp
from parselmouth.adapters.dfp.delivery_utils import transform_campaign_from_dfp
from parselmouth.adapters.dfp.delivery_utils import transform_creative_from_dfp


class DFPInterface(AbstractInterface):
    """
    Implementation of the DFP Ad service interface

    Serializes native Parselmouth objects into the PQL (Publisher
    Query Language) representations for querying objects
    """

    def __init__(self,
                 client_id,
                 client_secret,
                 refresh_token,
                 application_name,
                 network_code):
        """
        Constructor

        @param provider_config: child(parselmouth.config.ParselmouthConfig)
        """
        self.dfp_client = DFPClient(
            client_id,
            client_secret,
            refresh_token,
            application_name,
            network_code,
            version=DFP_API_VERSION,
        )

    def _convert_response_to_dict(self, dfp_data):
        """
        @param dfp_data: list(SUDS)
        @return: list(dict)
        """
        return [recursive_asdict(d) for d in dfp_data]

    def get_network_timezone(self):
        """
        Get the DFP network timezone for
        the host this client is connected to

        @return: pytz.timezone
        """
        dfp_data = self.dfp_client.get_network_data()
        data = recursive_asdict(dfp_data)
        return timezone(data['timeZone'])

    def get_campaign(self, campaign_id):
        """
        Return a campaign object given an id

        @param campaign_id: str, id of the campaign to return
        @return: parselmouth.delivery.Campaign
        """
        # Fetch the SUDS object and convert to a proper dictionary
        dfp_order = self.dfp_client.get_order(campaign_id)
        results = self._convert_response_to_dict(dfp_order)

        if len(results) == 0:
            raise ParselmouthException(
                "No results for campaign with id: {0}".format(campaign_id)
            )
        elif len(results) > 1:
            raise ParselmouthException(
                "More than one result for campaign with id: {0}".format(
                    campaign_id
                )
            )

        return transform_campaign_from_dfp(results[0])

    def get_campaigns(self,
                      order=DFP_QUERY_DEFAULTS['order'],
                      limit=None,
                      offset=DFP_QUERY_DEFAULTS['offset'],
                      **filter_kwargs):
        """
        Get campaigns on optional filters

        @param order: str, PQL key to sort on (default=ID)
        @param limit: int, number of PQL results to return
        @param offset: int, page in a stream of PQL results to return
        @param filter_kwargs: dict, keyword arguments on which to filter
            PQL results
        @return: L{parselmouth.delivery.Campaign}

        Example:
            * Get an order by id: `get_campaigns(id=ORDER_ID)`
            * Get orders by advertiser id:
                `get_campaigns(advertiserId=ADVERTISER_ID, limit=10)`
        """
        # Fetch the SUDS object and convert to a proper dictionary
        dfp_orders = self.dfp_client.get_orders(
            order=order,
            limit=limit,
            offset=offset,
            **filter_kwargs
        )
        results = self._convert_response_to_dict(dfp_orders)

        campaigns = []
        for order in results:
            campaigns.append(
                transform_campaign_from_dfp(order)
            )
        return campaigns

    def get_line_item(self, line_item_id):
        """
        Return a line item object given an id

        @param line_item_id: str, id of the LineItem to return
        @return: parselmouth.delivery.LineItem
        """
        dfp_line_item = self.dfp_client.get_line_item(line_item_id)
        results = self._convert_response_to_dict(dfp_line_item)

        if len(results) == 0:
            raise ParselmouthException(
                "No results for line item with id: {0}".format(line_item_id)
            )
        elif len(results) > 1:
            raise ParselmouthException(
                "More than one result for line item with id: {0}".format(
                    line_item_id
                )
            )

        return transform_line_item_from_dfp(results[0])

    def get_line_items(self,
                       order=DFP_QUERY_DEFAULTS['order'],
                       limit=None,
                       offset=DFP_QUERY_DEFAULTS['offset'],
                       **filter_kwargs):
        """
        Get line items on optional filters

        @param order: str, PQL key to sort on (default=ID)
        @param limit: int, number of PQL results to return
        @param offset: int, page in a stream of PQL results to return
        @param filter_kwargs: dict, keyword arguments on which to filter
            PQL results
        @return: L{parselmouth.delivery.LineItem}
        """

        # Fetch the SUDS object and convert to a proper dictionary
        dfp_line_items = self.dfp_client.get_line_items(
            order=order,
            limit=limit,
            offset=offset,
            **filter_kwargs
        )
        results = self._convert_response_to_dict(dfp_line_items)

        line_items = []
        for line_item in results:
            line_items.append(
                transform_line_item_from_dfp(line_item)
            )
        return line_items

    def get_campaign_line_items(self, campaign):
        """
        Get line items on optional filters

        @param campaign: Campaign|str
        @return: L{parselmouth.delivery.LineItem}
        """
        if isinstance(campaign, Campaign):
            _id = campaign.id
        else:
            _id = int(campaign)

        return self.get_line_items(orderId=_id)

    def get_line_item_available_inventory(self,
                                          line_item,
                                          use_start=False,
                                          preserve_id=False):
        """
        Get number of impressions available for line item

        @param line_item: LineItem
        @param use_start: bool, if False, checks availability from right
            now
        @param preserve_id: bool, communicate the id of the line item
            being forecasted to DFP. This is used in the case where we
            want to get a forecast on a line item in flight. This way, a
            domain doesn't need to have enough spare inventory to
            accommodate the two line items simultaneously. NOTE: If this
            is true then use_start is necessarily true.
        @return: int|None, number of available impressions
        """
        dfp_line_item = transform_forecast_line_item_to_dfp(
            line_item, use_start, preserve_id
        )
        logging.info(
            "Obtaining forecast data for line item %s",
            line_item.id or line_item
        )
        try:
            dfp_forecast = self.dfp_client.forecast_line_item(dfp_line_item)
        except Exception as e:
            raise ParselmouthException(e)

        forecast = recursive_asdict(dfp_forecast)
        if forecast and forecast.get('availableUnits'):
            available_units = int(forecast['availableUnits'])
        else:
            available_units = None

        logging.info(
            "%s available impressions",
            str(available_units)
        )
        return available_units

    def get_advertisers(self):
        """
        Queries dfp for all advertisers within their account

        @return: list(dict), returns a list of company dictionaries
        """
        brands = self.dfp_client.get_advertisers()

        if len(brands) == 0:
            raise ParselmouthException(
                "No brands found"
            )
        else:
            return brands

    def get_creative(self, creative_id):
        """
        Return a creative object given an id

        @param creative_id: str, id of the campaign to return
        @return: parselmouth.delivery.Creative
        """
        dfp_creative = self.dfp_client.get_creative(creative_id)
        creatives = self._convert_response_to_dict(dfp_creative)

        if len(creatives) == 0:
            raise ParselmouthException(
                "No results for creative with id: {0}".format(creative_id)
            )
        elif len(creatives) > 1:
            raise ParselmouthException(
                "More than one result for creative with id: {0}".format(
                    creative_id
                )
            )

        return transform_creative_from_dfp(creatives[0])

    def get_creatives(self,
                      order=DFP_QUERY_DEFAULTS['order'],
                      limit=None,
                      offset=DFP_QUERY_DEFAULTS['offset'],
                      **filter_kwargs):
        """
        Get creatives on optional filters

        @param order: str, PQL key to sort on (default=ID)
        @param limit: int, number of PQL results to return
        @param offset: int, page in a stream of PQL results to return
        @param filter_kwargs: dict, keyword arguments on which to filter
            PQL results
        @return: L{parselmouth.delivery.LineItem}
        """

        # Fetch the SUDS object and convert to a proper dictionary
        dfp_creatives = self.dfp_client.get_creatives(
            order=order,
            limit=limit,
            offset=offset,
            **filter_kwargs
        )
        results = self._convert_response_to_dict(dfp_creatives)

        creatives = []
        for creative in results:
            creatives.append(
                transform_creative_from_dfp(creative)
            )
        return creatives

    def get_line_item_creatives(self, line_item):
        """
        Return the creatives associated with a given line item

        @param line_item: str|int|parselmouth.delivery.LineItem,
            either the id of the lineitem or an object with the id
        @return: list(parselmouth.delivery.Creative)
        """

        if isinstance(line_item, LineItem):
            _id = line_item.id
        else:
            _id = int(line_item)
        creatives_to_fetch = self.dfp_client.get_line_item_creatives(_id)
        if len(creatives_to_fetch) == 0:
            raise ParselmouthException(
                "No creatives associated with line item: {0}".format(_id)
            )
        creatives = self.get_creatives(
            id=creatives_to_fetch,
            limit=len(creatives_to_fetch)
        )
        return creatives

    def get_geography_targets(self):
        """
        Get a list of DFP geography ids

        @return: list(dict)
        """
        geo_list = self.dfp_client.get_geography_targets()

        # The type field is in all caps, we want to
        # lower case this to be consistent with other systems
        output_list = []
        for item in geo_list:
            # Convert to Geography Target objects
            geo = Geography(
                id=item['id'],
                parent_id=item['countrycode'],
                type=item['type'].lower(),
                name=item['name'],
                external_name=quote(item['name'], ''),
            )
            output_list.append(geo)

        return output_list

    def get_adunit_targets(self):
        """
        Get a list of DFP adunit ids

        @return: list(dict)
        """
        adunit_list = self.dfp_client.get_adunit_targets()

        output_list = []
        for item in adunit_list:
            # Convert to Geography Target objects
            adunit = AdUnit(
                id=item['id'],
                parent_id=item['parentid'],
                name=item['name'],
                external_name=item['id'],
            )
            output_list.append(adunit)

        return output_list

    def _parse_custom_targets(self, custom_targets):
        """
        Helper function for converting native DFP custom targets into
        Parselmouth types

        @param custom_targets: list(dict)
        @return: list(parselmouth.targeting.Custom)
        """

        custom_targets = self._convert_response_to_dict(custom_targets)

        output_list = []
        for item in custom_targets:
            _external_id = item.get('name')
            if isinstance(_external_id, str):
                # Must be upper case to be consistent with redshift data
                _external_name = _external_id.upper()
            else:
                _external_name = _external_id

            display_name = item.get('displayName')
            if display_name == 'None':
                display_name = None

            output_list.append(
                Custom(
                    id=item['id'],
                    parent_id=item.get('customTargetingKeyId'),
                    name=item['name'],
                    type=item.get('type'),
                    external_id=_external_id,
                    external_name=_external_name,
                    descriptive_name=display_name,
                    # Fields needed for reconstructing dfp custom criterion
                    id_key='valueIds',
                    node_key='CustomCriteria',
                )
            )

        return output_list

    def get_custom_targets(self, key_name=None, value_name=None):
        """
        Get all key and value data from the custom
        targeting service

        @param key_name: str|None, if present only return
            targeting with the given key name
        @param value_name: str|None, if present only return
            targeting with the given value name
        @return: list(parselmouth.targeting.Custom)
        """
        dfp_custom_targets = self.dfp_client.get_custom_targets(
            key_name, value_name,
        )
        return self._parse_custom_targets(dfp_custom_targets)

    def create_custom_target(self, key, value):
        """
        Add a custom target to this domain's ad service provider

        @param key: parselmouth.targeting.Custom
        @param value: parselmouth.targeting.Custom
        @return: list(parselmouth.targeting.Custom)
        """
        assert isinstance(key, Custom)
        assert isinstance(value, Custom)

        dfp_custom_targets = self.dfp_client.create_custom_target(
            key_name=key.name,
            key_type=key.type,
            key_display_name=key.descriptive_name,
            value_name=value.name,
            value_match_type=value.type,
            value_display_name=value.descriptive_name,
        )
        return self._parse_custom_targets(dfp_custom_targets)

    def get_line_item_report(self,
                             start,
                             end,
                             columns=['ad_impressions']):
        """
        Get the number of impressions served by DFP
        for all line items between the two datetimes.

        Note: These datetimes are assumed to be in the timezone
        of the host and will be aligned to day

        Note: This API has a strange behavior where the date
        inputs only allow for a calendar day.
        This means start=1/1, end=1/1 will query against
        the entire day of 1/1

        @param start: datetime,
        @param end: datetime,
        @param columns: list(str), list of columns to include
        @return: list(dict)
        """
        assert [DFP_REPORT_METRIC_MAP[c] for c in columns]

        dfp_start = align_to_day(start)
        # You must subtract one day because the entire end
        # date will be included in the query result
        dfp_end = align_to_day(end) - timedelta(days=1)

        results = self.dfp_client.generate_report(
            dimensions=[
                DFP_REPORT_METRIC_MAP['line_item_id'],
                DFP_REPORT_METRIC_MAP['line_item_name'],
            ],
            columns=[DFP_REPORT_METRIC_MAP[c] for c in columns],
            date_range_type='CUSTOM_DATE',
            start_date=dfp_start,
            end_date=dfp_end,
        )

        result = []
        for _item in results:
            # Translate to chartbeat keys
            doc = {}
            for _key, dfp_key in DFP_REPORT_METRIC_MAP.items():
                if _item.get(dfp_key) is not None and _key in columns:
                    try:
                        doc[_key] = int(_item[dfp_key])
                    except ValueError:
                        doc[_key] = _item[dfp_key]
                elif _item.get(dfp_key) is not None:
                    doc[_key] = _item[dfp_key]

            result.append(doc)

        return result

    def update_line_items(self, line_items):
        """
        Update multiple Line Item for a provider

        @param line_items: L{parselmouth.delivery.LineItem}
        """
        # Convert line items into native format for the dfp client to use
        native_line_items = [
            transform_line_item_to_dfp(line_item)
            for line_item in line_items
        ]
        self.dfp_client.update_line_items(native_line_items)
