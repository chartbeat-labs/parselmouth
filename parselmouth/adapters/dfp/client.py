#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" DFP Native Client
"""

# Future-proof
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

# Standard Library Imports
import csv
import logging
from gzip import GzipFile
from tempfile import NamedTemporaryFile

# Third Party Library Imports
from googleads import DfpClient as GoogleDFPClient
from googleads.oauth2 import GoogleRefreshTokenClient
from googleads.dfp import FilterStatement
from googleads.dfp import SUGGESTED_PAGE_LIMIT
from googleads.errors import DfpReportError

# Parselmouth Imports
from parselmouth.exceptions import ParselmouthException

# Parselmouth Imports - Local DFP Adapter Imports
from parselmouth.adapters.dfp.constants import DFP_API_VERSION
from parselmouth.adapters.dfp.constants import DFP_CUSTOM_TARGETING_KEY_TYPES
from parselmouth.adapters.dfp.constants import DFP_QUERY_DEFAULTS
from parselmouth.adapters.dfp.constants import DFP_VALUE_MATCH_TYPES
from parselmouth.adapters.dfp.utils import format_pql_response
from parselmouth.adapters.dfp.utils import format_report_list
from parselmouth.adapters.dfp.utils import sanitize_report_response


class DFPClient(object):
    """
    Class retrieving and submitting data to the DFP API

    This is meant to be a pretty bare-bones class for simply building
    queries submittable to DFP.
    """

    def __init__(self,
                 client_id,
                 client_secret,
                 refresh_token,
                 application_name,
                 network_code,
                 version=DFP_API_VERSION):
        """
        https://developers.google.com/doubleclick-publishers/docs/authentication

        @param client_id: str
        @param client_secret: str
        @param refresh_token: str
        @param application_name: str
        @param network_code: str
        @param version: str
        """
        self.version = DFP_API_VERSION
        self.native_dfp_client = self._get_client(
            client_id,
            client_secret,
            refresh_token,
            application_name,
            network_code,
        )

    def __repr__(self):
        """
        Human readable representation of this object

        @return: str
        """
        return (
            "{class_name}("
                "version='{version}'"
            ")"
        ).format(
            class_name=self.__class__.__name__,
            version=self.version
        )

    def _get_client(self,
                    client_id,
                    client_secret,
                    refresh_token,
                    application_name,
                    network_code):
        """
        Create a client to connect the Google DFP API

        @param headers: dict, Oauth2 authorization header
        @return: googleads.DfpClient
        """
        client_token = GoogleRefreshTokenClient(
            client_id,
            client_secret,
            refresh_token,
        )
        return GoogleDFPClient(
            client_token,
            application_name,
            network_code,
        )

    def _format_query(self,
                      order=DFP_QUERY_DEFAULTS['order'],
                      limit=None,
                      offset=DFP_QUERY_DEFAULTS['offset'],
                      **filter_kwargs):
        """
        Query formatter

        @param query_dict: dictionary of query parameters to organize
            into a PQL statemente
        @param order: str, PQL key to sort on (default=ID)
        @param limit: int, number of PQL results to return
        @param offset: int, page in a stream of PQL results to return
        @param filter_kwargs: dict, keyword arguments on which to filter
            PQL results
        @return: FilterStatement, PQL statement

        ## TODO: We probably want to do some checking of `filter_kwargs`
            against available column names in DFP PQL tables
        """
        if order:
            query = "ORDER BY {order}".format(order=order)
        else:
            query = ""

        filters = []
        for key, val in filter_kwargs.iteritems():
            if isinstance(val, list):
                # gotta format that in query
                _dfp_list = ", ".join([str(x) for x in val])
                filters.append("{0} IN ({1})".format(key, _dfp_list))
                pass
            else:
                filters.append("{0}={1}".format(key, val))
        if filters:
            # Prepend the where parameters to the base query
            where_query = " AND ".join(filters)

            query = "WHERE {where} {order}".format(
                where=where_query,
                order=query,
            )

        statement = FilterStatement(query)
        if limit:
            statement.limit = limit
        if offset:
            statement.offset = offset

        return statement

    def _run_service_query(self, query, query_function):
        """
        Run a series of chunked DFP queries until all results
        are acquired

        @param query: FilterStatement
        @param query_function: Dfp service method
        @return: list
        """
        results = []
        while True:
            try:
                response = query_function(query.ToStatement())
            except Exception as e:
                raise ParselmouthException(
                    "Error running query: {0}. Got Error: {1}".format(
                        query.ToStatement(),
                        str(e)
                    )
                )
            if 'results' in response:
                logging.info(
                    'Statement %s returned %d results',
                    query.ToStatement(),
                    len(response['results']),
                )
                results += response['results']
                query.offset += SUGGESTED_PAGE_LIMIT
            else:
                break

        return results

    def get_network_data(self):
        """
        Get network data associated with dfp account

        @return: SUDS envelope
        """
        service = self.native_dfp_client.GetService(
            'NetworkService',
            version=self.version,
        )
        return service.getCurrentNetwork()

    def get_order(self, order_id):
        """
        Gets an order item by id

        @param order_id: str|int, the numerical id of the item
        @return: SUDS envelope
        """
        return self.get_orders(id=order_id)

    def get_orders(self,
                   order=DFP_QUERY_DEFAULTS['order'],
                   limit=DFP_QUERY_DEFAULTS['limit'],
                   offset=DFP_QUERY_DEFAULTS['offset'],
                   **filter_kwargs):
        """
        Get orders on filter keyword arguments other than id

        @param order: str, PQL key to sort on (default=ID)
        @param limit: int, number of PQL results to return
        @param offset: int, page in a stream of PQL results to return
        @param filter_kwargs: dict, keyword arguments on which to filter
            PQL results
        @return: SUDS envelope

        Example:
            * Get an order by id: `get_orders(id=ORDER_ID)`
        """
        query = self._format_query(
            order=order,
            limit=limit,
            offset=offset,
            **filter_kwargs
        )
        service = self.native_dfp_client.GetService(
            'OrderService',
            version=self.version
        )

        orders = self._run_service_query(
            query, service.getOrdersByStatement,
        )

        if not orders:
            logging.warning(
                'Results not found from query. Query: {0}'.format(query.ToStatement())
            )
            return []

        return orders

    def get_line_item(self, line_item_id):
        """
        Gets a line item by id

        @param item_id: str|int, the numerical id of the item
        @return: SUDS envelope
        """
        return self.get_line_items(id=line_item_id)

    def get_line_items(self,
                       order=DFP_QUERY_DEFAULTS['order'],
                       limit=DFP_QUERY_DEFAULTS['limit'],
                       offset=DFP_QUERY_DEFAULTS['offset'],
                       **filter_kwargs):
        """
        Get line items on filter keyword arguments other than id

        @param order: str, PQL key to sort on (default=ID)
        @param limit: int, number of PQL results to return
        @param offset: int, page in a stream of PQL results to return
        @param filter_kwargs: dict, keyword arguments on which to filter
            PQL results
        @return: SUDS envelope

        Example:
            * Get an order by id: `get_line_items(id=LINE_ITEM_ID)`
        """
        query = self._format_query(
            order=order,
            limit=limit,
            offset=offset,
            **filter_kwargs
        )
        service = self.native_dfp_client.GetService(
            'LineItemService',
            version=self.version
        )

        line_items = self._run_service_query(
            query, service.getLineItemsByStatement,
        )

        if not line_items:
            logging.warning(
                'Results not found from query. Query: {0}'.format(query)
            )
            return []

        return line_items

    def get_advertisers(self):
        """
        Queries dfp for all advertisers within their account

        @return: list(dict), returns a list of company dictionaries
        """
        service = self.native_dfp_client.GetService(
            'CompanyService',
            version=self.version,
        )

        # Create statement object to only select companies that are advertisers
        values = [{
            'key': 'type',
            'value': {
                'xsi_type': 'TextValue',
                'value': 'ADVERTISER'

            }
        }]
        query = 'WHERE type = :type'
        statement = FilterStatement(query, values)
        results = self._run_service_query(statement, service.getCompaniesByStatement)
        advertisers = [
            {'id': advertiser['id'],
             'name': advertiser['name']
             }
            for advertiser in results
        ]
        return advertisers

    def forecast_line_item(self, dfp_line_item):
        """
        @param line_item: LineItem
        @return: SUDS envelope
        """
        service = self.native_dfp_client.GetService(
            'ForecastService',
            version=self.version,
        )
        prospective_line_item = {
            'lineItem': dfp_line_item,
        }
        forecast_options = {
            'includeContendingLineItems': False,
            'includeTargetingCriteriaBreakdown': False,
        }
        return service.getAvailabilityForecast(
            prospective_line_item,
            forecast_options,
        )

    def get_creative(self, creative_id):
        """
        Gets a creative by id

        @param item_id: str|int, the numerical id of the item
        @return: SUDS envelope
        """
        return self.get_creatives(id=creative_id)

    def get_creatives(self,
                      order=DFP_QUERY_DEFAULTS['order'],
                      limit=DFP_QUERY_DEFAULTS['limit'],
                      offset=DFP_QUERY_DEFAULTS['offset'],
                      **filter_kwargs):
        """
        Get creatives on filter keyword arguments other than id

        @param order: str, PQL key to sort on (default=ID)
        @param limit: int, number of PQL results to return
        @param offset: int, page in a stream of PQL results to return
        @param filter_kwargs: dict, keyword arguments on which to filter
            PQL results
        @return: SUDS envelope

        Example:
            * Get an order by id: `get_creatives(id=CREATIVE_ID)`
        """
        query = self._format_query(
            order=order,
            limit=limit,
            offset=offset,
            **filter_kwargs
        )
        service = self.native_dfp_client.GetService(
            'CreativeService',
            version=self.version
        )

        creatives = self._run_service_query(
            query, service.getCreativesByStatement,
        )

        if not creatives:
            logging.warning(
                'Results not found from query. Query: {0}'.format(query)
            )
            return []

        return creatives

    def get_line_item_creatives(self, line_item_id):
        """
        Get the creatives assoicated with a particular line item

        @param line_item_id: int, the line item id
        @return: list(str), list of creative ids associated with the
            given line item
        """
        values = [{
              'key': 'lineItemId',
              'value': {
                  'xsi_type': 'NumberValue',
                  'value': line_item_id
              }
          }]
        query = 'WHERE lineItemId = :lineItemId'
        statement = FilterStatement(where_clause=query, values=values)
        service = self.native_dfp_client.GetService(
            'LineItemCreativeAssociationService',
            version=self.version
        )

        creatives = self._run_service_query(
            statement, service.getLineItemCreativeAssociationsByStatement,
        )

        if creatives:
            if 'results' in creatives:
                return [
                    str(creative['creativeId'])
                    for creative in creatives['results']
                ]
            else:
                return [
                    str(creative['creativeId'])
                    for creative in creatives
                ]
        else:
            return []

    def _run_pql_query(self, pql_query, values=None):
        """
        Get a list of contents of a DFP table for the specific pql query

        @param pql_query: str
        @param values: list(dict)
        @return: list
        """
        report_downloader = self.native_dfp_client.GetDataDownloader(
            version=self.version,
        )
        raw_list = report_downloader.DownloadPqlResultToList(
            pql_query, values,
        )
        return format_pql_response(raw_list)

    def get_geography_targets(self):
        """
        Get a list of DFP geography ids

        @return: list(dict)
        """
        pql_query = """
        SELECT Id, Name, CountryCode, Type
        FROM Geo_Target
        WHERE type='country'
            AND targetable=true
        """
        return self._run_pql_query(pql_query)

    def get_adunit_targets(self):
        """
        Get a list of DFP geography ids

        @return: list(dict)
        """
        pql_query = """
        SELECT Id, Name, ParentId
        FROM Ad_Unit
        """
        return self._run_pql_query(pql_query)

    def get_custom_targets(self, key_name=None, value_name=None):
        """
        Get all custom targeting key and value data

        @param key_name: str|None, if present only return
            targeting with the given key name
        @param value_name: str|None, if present only return
            targeting with the given value name
        @return: list(dict)
        """
        service = self.native_dfp_client.GetService(
            'CustomTargetingService',
            version=self.version,
        )

        if key_name:
            values = [{
                'key': 'name',
                'value': {
                    'xsi_type': 'TextValue',
                    'value': key_name,
                }
            }]
            query = 'WHERE name = :name'
            key_statement = FilterStatement(query, values)
        else:
            key_statement = FilterStatement()

        key_results = self._run_service_query(
            key_statement, service.getCustomTargetingKeysByStatement,
        )

        custom_data = []
        if not key_results:
            return custom_data

        if not value_name:
            # In the case when value_name is given, do not include
            # the key target
            custom_data += key_results

        # Create statement to get all targeting values.
        query = 'WHERE customTargetingKeyId IN ({})'.format(
            ', '.join([str(key['id']) for key in key_results]),
        )

        if value_name:
            values = [{
                'key': 'name',
                'value': {
                    'xsi_type': 'TextValue',
                    'value': value_name,
                }
            }]
            query += ' AND name = :name'
            value_statement = FilterStatement(query, values)
        else:
            value_statement = FilterStatement(query)

        # Get custom targeting values by statement.
        value_results = self._run_service_query(
            value_statement, service.getCustomTargetingValuesByStatement,
        )
        custom_data += value_results
        return custom_data

    def create_custom_target(self,
                             key_name,
                             key_type,
                             value_name,
                             key_display_name=None,
                             value_display_name=None,
                             value_match_type=None):
        """
        Add a custom target to DFP

        NOTE: Since DFP is responsible for creating the custom target
            key and value ids we must first create the key to get its id
            before creating the value

        DFP custom targeting keys are paraphrased here:
            {
                id: int- id of custom targeting value (assigned by DFP)
                name: str- name of the value, can be used for encoding
                displayName: str|None- descriptive name of the value
                type: ENUM(PREDEFINED, FREEFORM), see docs
            }
        The full spec can be found here:
            https://developers.google.com/doubleclick-publishers/docs/reference/v201408/CustomTargetingService.CustomTargetingKey

        DFP custom targeting values are paraphrased here:
            {
                customTargetingKeyId: int- id of custom targeting key
                id: int- id of custom targeting value (assigned by DFP)
                name: str- name of the value, can be used for encoding
                displayName: str|None- descriptive name of the value
                matchType: ENUM(EXACT, BROAD, PREFIX, BROAD_PREFIX,
                           SUFFIX, CONTAINS, UNKNOWN)|None, see docs
            }
        The full outline can be found here:
            https://developers.google.com/doubleclick-publishers/docs/reference/v201408/CustomTargetingService.CustomTargetingValue

        @param key_name: str, encoded name for the key
        @param key_type: str, type of the custom targeting key
        @param value_name: str, encoded name for the value
        @param key_display_name: str|None, descriptive name for key
        @param value_display_name: str|None, descriptive name for value
        @return: list(dict)
        """

        # Input checking
        if key_type not in DFP_CUSTOM_TARGETING_KEY_TYPES:
            raise ParselmouthException(
                "Provided key type ({0}) not one of a valid type ({1})".format(
                    key_type, DFP_CUSTOM_TARGETING_KEY_TYPES
                ))
        if value_match_type and value_match_type not in DFP_VALUE_MATCH_TYPES:
            raise ParselmouthException(
                "Provided val type ({0}) not one of a valid type ({1})".format(
                    value_match_type, DFP_VALUE_MATCH_TYPES
                ))

        existing_values = self.get_custom_targets(
            key_name=key_name,
            value_name=value_name
        )

        # Return if we already have a custom targeting keypair for key:value
        if existing_values:
            logging.info("Custom target key+value already exists in DFP")
            return existing_values

        service = self.native_dfp_client.GetService(
            'CustomTargetingService',
            version=self.version,
        )

        # Check if the key already exists in DFP, if not then create it
        # We need to do this first since DFP handles id assignment
        existing_keys = self.get_custom_targets(key_name=key_name)
        if not existing_keys:
            logging.info("Key ({0}) does not exist in DFP".format(key_name))
            key = {
                'name': key_name,
                'type': key_type,
            }
            if key_display_name:
                key['displayName'] = key_display_name
            keys = service.createCustomTargetingKeys([key])
        else:
            logging.info("Key ({0}) already exists in DFP".format(key_name))
            keys = existing_keys

        # Extract the key we want
        if len(keys) == 0:
            raise ParselmouthException("No keys returned by DFP")
        elif len(keys) > 1:
            raise ParselmouthException("Too many keys returned by DFP")
        key = keys[0]

        # Create the new value in DFP
        logging.info("Value ({0}) does not exist in DFP".format(value_name))
        value = {
            'customTargetingKeyId': key['id'],
            'name': value_name,
        }
        if value_display_name:
            value['displayName'] = value_display_name
        if value_match_type:
            value['matchType'] = value_match_type
        values = service.createCustomTargetingValues([value])

        # Extract the value we want
        if len(values) == 0:
            raise ParselmouthException("No values returned by DFP")
        elif len(values) > 1:
            raise ParselmouthException("Too many values returned by DFP")
        value = values[0]

        if value['customTargetingKeyId'] != key['id']:
            raise ParselmouthException((
                "Value custom target key id ({0}) does not equal the Key id "
                "({1})".format(value['customTargetingKeyId'], key['id'])
            ))

        return [key, value]

    def _generate_report_as_list(self, report_query):
        """
        Generates a report from a report query.  This
        function will hang until the report has finished processing.
        This function does not return the report, but a pointer
        to this report

        @param report_query: dict
        @return: list(dict)
        """
        logging.info('Generating report with query: %s', report_query)
        report_downloader = self.native_dfp_client.GetDataDownloader(
            version=self.version,
        )
        try:
            # Run the report and wait for it to finish.
            report_id = report_downloader.WaitForReport(
                {'reportQuery': report_query},
            )
        except DfpReportError, e:
            logging.exception(e)
            return None

        with NamedTemporaryFile(suffix='.csv.gz', delete=True) as report_file:
            # Download report data.
            report_downloader.DownloadReportToFile(
                report_id, 'CSV_DUMP', report_file
            )
            # Go to top of file
            report_file.seek(0)
            # Unzip contents and read
            with GzipFile(fileobj=report_file, mode='r') as unzipped:
                csvfile = csv.reader(unzipped)
                parsed_data = [
                    [cell.decode('utf-8') for cell in row]
                    for row in csvfile
                ]

        logging.info('Report download completed with %d results', len(parsed_data))
        return format_report_list(parsed_data)

    def generate_report(self,
                        dimensions,
                        columns,
                        date_range_type,
                        start_date=None,
                        end_date=None,
                        filter_query=None):
        """
        https://developers.google.com/doubleclick-publishers/docs/reference/v201408/ReportService.ReportQuery

        @param dimensions: list(str), list of DFP dimensions
        @param columns: list(str), list of DFP columns
        @param date_range_type: str, e.g. LAST_WEEK, CUSTOM_DATE
        @param start_date: datetime|None, if date_range_type is CUSTOM_DATE, this is required
        @param end_date: datetime|None, if date_range_type is CUSTOM_DATE, this is required
        @param filter_statement: str|None, filter to apply to report query
        @return: list(dict)
        """
        report_query = {
            'dimensions': dimensions,
            'columns': columns,
            'dateRangeType': date_range_type,
        }

        if date_range_type == 'CUSTOM_DATE':
            assert start_date and end_date
            report_query['startDate'] = {
                'year': start_date.year,
                'month': start_date.month,
                'day': start_date.day,
            }
            report_query['endDate'] = {
                'year': end_date.year,
                'month': end_date.month,
                'day': end_date.day,
            }

        if filter_query:
            report_query['statement'] = filter_query

        raw_list = self._generate_report_as_list(report_query)
        return [sanitize_report_response(i) for i in raw_list]

    def update_line_items(self, line_items):
        """
        Update a list of line items in DFP

        @param line_items: L{dict}
        """

        service = self.native_dfp_client.GetService(
            'LineItemService',
            version=self.version
        )
        service.updateLineItems(line_items)
