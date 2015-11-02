"""
Set of constants for pulling data from DFP
"""

# Chartbeat Imports
from parselmouth.constants import AdProviderSellTypes
from parselmouth.constants import ParselmouthReportMetrics
from parselmouth.utils.enum import Enum


DFP_API_VERSION = 'v201508'
"""
str, version of the DFP API to use
https://developers.google.com/doubleclick-publishers/
"""

DFP_QUERY_DEFAULTS = {
    'order': 'ID',
    'limit': 1,
    'offset': 0
}
"""
dict, default query params for the DFP API
"""

SELL_TYPE_MAP = {
    'SPONSORSHIP': AdProviderSellTypes.sponsorship,
    'STANDARD': AdProviderSellTypes.standard,
    'NETWORK': AdProviderSellTypes.network,
    'HOUSE': AdProviderSellTypes.house,
    'PRICE_PRIORITY': AdProviderSellTypes.price_priority,
}
"""
dict, map dfp sell type names -> AD_PROVIDER_SELL_TYPES
"""

DFP_REPORT_METRIC_MAP = {
    ParselmouthReportMetrics.ad_impressions: "AD_SERVER_IMPRESSIONS",
    ParselmouthReportMetrics.ad_viewable_impressions: "AD_SERVER_ACTIVE_VIEW_VIEWABLE_IMPRESSIONS",
    ParselmouthReportMetrics.line_item_id: "LINE_ITEM_ID",
    ParselmouthReportMetrics.line_item_name: "LINE_ITEM_NAME",
    ParselmouthReportMetrics.delivery_percentage: "AD_SERVER_DELIVERY_INDICATOR",
}
"""
dict, map to column/dimension names in the dfp report api
"""

DFP_CUSTOM_TARGETING_KEY_TYPES = Enum([
    'PREDEFINED',
    'FREEFORM'
])
"""
Enum, list of the available custom targeting key types
"""

DFP_VALUE_MATCH_TYPES = Enum([
    'EXACT',
    'BROAD',
    'PREFIX',
    'BROAD_PREFIX',
    'SUFFIX',
    'CONTAINS',
    'UNKNOWN'
])
"""
Enum, list of the available custom targeting value match types
"""
