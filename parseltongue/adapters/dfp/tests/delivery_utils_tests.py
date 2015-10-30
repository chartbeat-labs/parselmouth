import unittest
from datetime import datetime
from pytz import timezone

from parseltongue.delivery import Cost
from parseltongue.delivery import Creative
from parseltongue.delivery import DeliveryMeta
from parseltongue.delivery import Goal
from parseltongue.delivery import LineItem
from parseltongue.delivery import Campaign
from parseltongue.delivery import Stats
from parseltongue.targeting import AdUnit
from parseltongue.targeting import TargetingCriterion
from parseltongue.targeting import TargetingData

from parseltongue.adapters.dfp.delivery_utils import dfp_date_to_datetime
from parseltongue.adapters.dfp.delivery_utils import datetime_to_dfp_date
from parseltongue.adapters.dfp.delivery_utils import transform_campaign_from_dfp
from parseltongue.adapters.dfp.delivery_utils import transform_campaign_to_dfp
from parseltongue.adapters.dfp.delivery_utils import transform_line_item_from_dfp
from parseltongue.adapters.dfp.delivery_utils import transform_line_item_to_dfp
from parseltongue.adapters.dfp.delivery_utils import transform_forecast_line_item_to_dfp
from parseltongue.adapters.dfp.delivery_utils import transform_creative_to_dfp
from parseltongue.adapters.dfp.delivery_utils import transform_creative_from_dfp


TEST_LINE_ITEM = LineItem(
    budget=Cost(
        budget_micro_amount=0.0,
        budget_currency_code='USD',
    ),
    cost_per_unit=Cost(
        budget_micro_amount=0.0,
        budget_currency_code='USD',
    ),
    cost_type='CPM',
    creative_placeholder=[{
        'creativeSizeType': 'PIXEL',
        'expectedCreativeCount': '1',
        'size': {
            'height': '768',
            'isAspectRatio': False,
            'width': '1024',
        }
    }],
    delivery=DeliveryMeta(
        actual_delivery_percent=0.0,
        delivery_rate_type='FRONTLOADED',
        expected_delivery_percent=0.0,
        stats=Stats(
            impressions=0,
            clicks=0,
        ),
    ),
    end=datetime(
        2014, 5, 31, 23, 59, tzinfo=timezone('America/New_York')
    ),
    id='line_item_id',
    name='line_item_name',
    campaign_id='campaign_id',
    campaign_name='campaign_name',
    primary_goal=Goal(
        goal_type='LIFETIME',
        unit_type='IMPRESSIONS',
        units=1000000,
    ),
    start=datetime(
        2014, 4, 23, 15, 50, tzinfo=timezone('America/New_York')
    ),
    last_modified=datetime(
        2014, 4, 23, 15, 50, tzinfo=timezone('America/New_York')
    ),
    status='DRAFT',
    targeting=TargetingData(
        custom=None,
        day_part=None,
        geography=None,
        inventory=TargetingCriterion(
            [AdUnit(id='adunit', include_descendants=True)],
            TargetingCriterion.OPERATOR.OR,
        ),
        user_domain=None,
        technology=None,
        video_content=None,
        video_position=None,
    ),
    target_platform='ANY',
    type='standard',
    value_cost_per_unit=Cost(
        budget_micro_amount=0.0,
        budget_currency_code='USD',
    ),
)


class DeliveryUtilsTest(unittest.TestCase):

    def test_date_utils(self):
        native_dt = datetime(2015, 1, 1, 8, 11, 32).replace(tzinfo=timezone('EST'))
        dfp_dt = {
            'timeZoneID': 'EST',
            'date': {
                'year': 2015,
                'day': 1,
                'month': 1,
            },
            'second': 32,
            'minute': 11,
            'hour': 8,
        }

        # Check dfp_date_to_datetime
        self.assertEqual(
            native_dt,
            dfp_date_to_datetime(dfp_dt),
        )

        # Check datetime_to_dfp_date
        self.assertDictEqual(
            dfp_dt,
            datetime_to_dfp_date(native_dt),
        )

        # Check inversion of dfp datetime
        self.assertDictEqual(
            dfp_dt,
            datetime_to_dfp_date(dfp_date_to_datetime(dfp_dt)),
        )

        # Check inversion of native datetime
        self.assertEqual(
            native_dt,
            dfp_date_to_datetime(datetime_to_dfp_date(native_dt)),
        )

        # Check default tz behavior
        notz_dt = datetime(2011, 8, 12)
        notz_dfp_dt = {
            'timeZoneID': 'UTC',
            'date': {
                'year': 2011,
                'day': 12,
                'month': 8,
            },
            'second': 0,
            'minute': 0,
            'hour': 0,
        }

        self.assertDictEqual(
            notz_dfp_dt,
            datetime_to_dfp_date(notz_dt),
        )

    def test_campaign_utils(self):
        campaign = Campaign(
            advertiser_id='ad_id',
            creator_id='cr_id',
            currency_code='USD',
            end=datetime(
                2015, 8, 14, 23, 59, tzinfo=timezone('America/New_York')
            ),
            external_campaign_id='0',
            id='campaign_id',
            name='campaign_name',
            start=datetime(
                2015, 3, 3, 15, 57, tzinfo=timezone('America/New_York')
            ),
            status='DRAFT',
            stats=Stats(
                impressions=0,
                clicks=0,
            ),
            last_modified=datetime(
                2015, 3, 3, 15, 57, tzinfo=timezone('America/New_York')
            ),
            total_budget=Cost(
                budget_micro_amount=10000.0,
                budget_currency_code='USD',
            ),
        )

        dfp_campaign = {
            'advertiserId': 'ad_id',
            'creatorId': 'cr_id',
            'currencyCode': 'USD',
            'endDateTime': {
                'date': {
                    'day': 14,
                    'month': 8,
                    'year': 2015,
                },
                'hour': 23,
                'minute': 59,
                'second': 0,
                'timeZoneID': 'America/New_York',
            },
            'id': 'campaign_id',
            'externalOrderId': '0',
            'lastModifiedByApp': None,
            'lastModifiedDateTime': {
                'date': {
                    'day': 3,
                    'month': 3,
                    'year': 2015,
                },
                'hour': 15,
                'minute': 57,
                'second': 0,
                'timeZoneID': 'America/New_York',
            },
            'name': 'campaign_name',
            'startDateTime': {
                'date': {
                    'day': 3,
                    'month': 3,
                    'year': 2015,
                },
                'hour': 15,
                'minute': 57,
                'second': 0,
                'timeZoneID': 'America/New_York',
            },
            'status': 'DRAFT',
            'totalBudget': {
                'currencyCode': 'USD',
                'microAmount': 10000.0,
            },
            'totalClicksDelivered': 0,
            'totalImpressionsDelivered': 0
        }

        # Check transform_campaign_to_dfp
        self.assertDictEqual(
            dfp_campaign,
            transform_campaign_to_dfp(campaign),
        )

        # Check transform_campaign_from_dfp
        self.assertEqual(
            campaign,
            transform_campaign_from_dfp(dfp_campaign),
        )

        # Check inversion of dfp campaign
        self.assertDictEqual(
            dfp_campaign,
            transform_campaign_to_dfp(transform_campaign_from_dfp(dfp_campaign)),
        )

        # Check inversion of native campaign
        self.assertEqual(
            campaign,
            transform_campaign_from_dfp(transform_campaign_to_dfp(campaign)),
        )

    def test_line_item_utils(self):
        dfp_line_item = {
            'budget': {
                'currencyCode': 'USD',
                'microAmount': '0',
            },
            'costPerUnit': {
                'currencyCode': 'USD',
                'microAmount': '0',
            },
            'costType': 'CPM',
            'creativePlaceholders': [{
                'creativeSizeType': 'PIXEL',
                'expectedCreativeCount': '1',
                'size': {
                    'height': '768',
                    'isAspectRatio': False,
                    'width': '1024',
                },
            }],
            'deliveryRateType': 'FRONTLOADED',
            'endDateTime': {
                'date': {
                    'day': 31,
                    'month': 5,
                    'year': 2014,
                },
                'hour': 23,
                'minute': 59,
                'second': 0,
                'timeZoneID': 'America/New_York',
            },
            'id': 'line_item_id',
            'lastModifiedByApp': None,
            'lastModifiedDateTime': {
                'date': {
                    'day': 23,
                    'month': 4,
                    'year': 2014,
                },
                'hour': 15,
                'minute': 50,
                'second': 0,
                'timeZoneID': 'America/New_York',
            },
            'lineItemType': 'STANDARD',
            'name': 'line_item_name',
            'orderId': 'campaign_id',
            'orderName': 'campaign_name',
            'primaryGoal': {
                'goalType': 'LIFETIME',
                'unitType': 'IMPRESSIONS',
                'units': u'1000000',
            },
            'startDateTime': {
                'date': {
                    'day': 23,
                    'month': 4,
                    'year': 2014,
                },
                'hour': 15,
                'minute': 50,
                'second': 0,
                'timeZoneID': 'America/New_York',
            },
            'stats': {
                'clicksDelivered': 0,
                'impressionsDelivered': 0,
                'videoCompletionsDelivered': 0,
                'videoStartsDelivered': 0,
            },
            'targetPlatform': 'ANY',
            'targeting': {
                'inventoryTargeting': {
                    'targetedAdUnits': [{
                        'adUnitId': 'adunit',
                        'includeDescendants': True,
                    }],
                },
            },
            'valueCostPerUnit': {
                'currencyCode': 'USD',
                'microAmount': '0',
            },
            'status': 'DRAFT',
        }

        # Check transform_line_item_to_dfp
        self.assertDictEqual(
            dfp_line_item,
            transform_line_item_to_dfp(TEST_LINE_ITEM),
        )

        # Check transform_line_item_from_dfp
        self.assertEqual(
            TEST_LINE_ITEM,
            transform_line_item_from_dfp(dfp_line_item),
        )

        # Check inversion of dfp line_item
        self.assertDictEqual(
            dfp_line_item,
            transform_line_item_to_dfp(transform_line_item_from_dfp(dfp_line_item)),
        )

        # Check inversion of native line_item
        self.assertEqual(
            TEST_LINE_ITEM,
            transform_line_item_from_dfp(transform_line_item_to_dfp(TEST_LINE_ITEM)),
        )

    def test_line_item_forecast_utils(self):
        dfp_no_start_no_id = {
            'costType': 'CPM',
            'creativePlaceholders': [{
                'creativeSizeType': 'PIXEL',
                'expectedCreativeCount': '1',
                'size': {
                    'height': '768',
                    'isAspectRatio': False,
                    'width': '1024',
                },
            }],
            'endDateTime': {
                'date': {
                    'day': 31,
                    'month': 5,
                    'year': 2014,
                },
                'hour': 23,
                'minute': 59,
                'second': 0,
                'timeZoneID': 'America/New_York',
            },
            'lineItemType': 'STANDARD',
            'primaryGoal': {
                'goalType': 'LIFETIME',
                'unitType': 'IMPRESSIONS',
                'units': 1000000,
            },
            'startDateTimeType': 'IMMEDIATELY',
            'targetPlatform': 'ANY',
            'targeting': {
                'inventoryTargeting': {
                    'targetedAdUnits': [{
                        'adUnitId': 'adunit',
                        'includeDescendants': True,
                    }],
                },
            },
        }
        # Check transform_forecast_line_item_to_dfp
        self.assertDictEqual(
            dfp_no_start_no_id,
            transform_forecast_line_item_to_dfp(TEST_LINE_ITEM, use_start=False, preserve_id=False),
        )

        dfp_start_no_id = {
            'costType': 'CPM',
            'creativePlaceholders': [{
                'creativeSizeType': 'PIXEL',
                'expectedCreativeCount': '1',
                'size': {
                    'height': '768',
                    'isAspectRatio': False,
                    'width': '1024',
                },
            }],
            'endDateTime': {
                'date': {
                    'day': 31,
                    'month': 5,
                    'year': 2014,
                },
                'hour': 23,
                'minute': 59,
                'second': 0,
                'timeZoneID': 'America/New_York',
            },
            'lineItemType': 'STANDARD',
            'primaryGoal': {
                'goalType': 'LIFETIME',
                'unitType': 'IMPRESSIONS',
                'units': 1000000,
            },
            'startDateTimeType': 'USE_START_DATE_TIME',
            'startDateTime': {
                'date': {
                    'day': 23,
                    'month': 4,
                    'year': 2014,
                },
                'hour': 15,
                'minute': 50,
                'second': 0,
                'timeZoneID': 'America/New_York',
            },
            'targetPlatform': 'ANY',
            'targeting': {
                'inventoryTargeting': {
                    'targetedAdUnits': [{
                        'adUnitId': 'adunit',
                        'includeDescendants': True,
                    }],
                },
            },
        }

        # Check transform_forecast_line_item_to_dfp
        self.assertDictEqual(
            dfp_start_no_id,
            transform_forecast_line_item_to_dfp(TEST_LINE_ITEM, use_start=True, preserve_id=False),
        )

        dfp_start_id = {
            'costType': 'CPM',
            'creativePlaceholders': [{
                'creativeSizeType': 'PIXEL',
                'expectedCreativeCount': '1',
                'size': {
                    'height': '768',
                    'isAspectRatio': False,
                    'width': '1024',
                },
            }],
            'endDateTime': {
                'date': {
                    'day': 31,
                    'month': 5,
                    'year': 2014,
                },
                'hour': 23,
                'minute': 59,
                'second': 0,
                'timeZoneID': 'America/New_York',
            },
            'lineItemType': 'STANDARD',
            'primaryGoal': {
                'goalType': 'LIFETIME',
                'unitType': 'IMPRESSIONS',
                'units': 1000000,
            },
            'startDateTimeType': 'USE_START_DATE_TIME',
            'startDateTime': {
                'date': {
                    'day': 23,
                    'month': 4,
                    'year': 2014,
                },
                'hour': 15,
                'minute': 50,
                'second': 0,
                'timeZoneID': 'America/New_York',
            },
            'targetPlatform': 'ANY',
            'targeting': {
                'inventoryTargeting': {
                    'targetedAdUnits': [{
                        'adUnitId': 'adunit',
                        'includeDescendants': True,
                    }],
                },
            },
            'id': 'line_item_id',
            'orderId': 'campaign_id',
        }

        # Check transform_forecast_line_item_to_dfp
        self.assertDictEqual(
            dfp_start_id,
            transform_forecast_line_item_to_dfp(TEST_LINE_ITEM, use_start=True, preserve_id=True),
        )

    def test_creative_utils(self):
        creative = Creative(
            advertiser_id='ad_id',
            id='creative_id',
            name='creative_name',
            size={
                'height': '250',
                'isAspectRatio': False,
                'width': '300',
            },
            preview_url='image.com',
            last_modified=datetime(
                2015, 3, 3, 15, 57, tzinfo=timezone('America/New_York')
            ),
        )

        dfp_creative = {
            'id': 'creative_id',
            'advertiserId': 'ad_id',
            'name': 'creative_name',
            'previewUrl': 'image.com',
            'size': {
                'height': '250',
                'isAspectRatio': False,
                'width': '300',
            },
            'lastModifiedDateTime': {
                'date': {
                    'day': 3,
                    'month': 3,
                    'year': 2015,
                },
                'hour': 15,
                'minute': 57,
                'second': 0,
                'timeZoneID': 'America/New_York',
            },
        }

        # Check transform_creative_to_dfp
        self.assertDictEqual(
            dfp_creative,
            transform_creative_to_dfp(creative),
        )

        # Check transform_creative_from_dfp
        self.assertEqual(
            creative,
            transform_creative_from_dfp(dfp_creative),
        )

        # Check inversion of dfp creative
        self.assertDictEqual(
            dfp_creative,
            transform_creative_to_dfp(transform_creative_from_dfp(dfp_creative)),
        )

        # Check inversion of native creative
        self.assertEqual(
            creative,
            transform_creative_from_dfp(transform_creative_to_dfp(creative)),
        )


if __name__ == "__main__":
    unittest.main()
