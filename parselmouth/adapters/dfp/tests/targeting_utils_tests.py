import unittest

from parselmouth.utils.check import check_equal
from parselmouth.targeting import AdUnit
from parselmouth.targeting import Geography
from parselmouth.targeting import TargetingCriterion
from parselmouth.targeting import TargetingData

from parselmouth.adapters.dfp.targeting_utils import transform_inventory_targeting_from_dfp
from parselmouth.adapters.dfp.targeting_utils import transform_inventory_targeting_to_dfp
from parselmouth.adapters.dfp.targeting_utils import transform_geography_targeting_from_dfp
from parselmouth.adapters.dfp.targeting_utils import transform_geography_targeting_to_dfp


class TargetingUtilsTest(unittest.TestCase):

    def test_inventory_targeting_utils(self):
        adunit1_or_adunit2 = TargetingCriterion(
            [AdUnit(id='1'), AdUnit(id='2')],
            TargetingCriterion.OPERATOR.OR,
        )
        dfp_adunit1_or_adunit2 = {
            'targetedAdUnits': [
                {
                    'includeDescendants': True,
                    'adUnitId': '1',
                },
                {
                    'includeDescendants': True,
                    'adUnitId': '2',
                },
            ],
        }
        # Check transform_inventory_targeting_to_dfp
        self.assertTrue(check_equal(
            dfp_adunit1_or_adunit2,
            transform_inventory_targeting_to_dfp(adunit1_or_adunit2),
        ))
        # Check transform_inventory_targeting_from_dfp
        self.assertTrue(check_equal(
            adunit1_or_adunit2,
            transform_inventory_targeting_from_dfp(dfp_adunit1_or_adunit2),
        ))

        not_adunit3 = TargetingCriterion(
            [TargetingCriterion([AdUnit(id='3')], TargetingCriterion.OPERATOR.OR)],
            TargetingCriterion.OPERATOR.NOT,
        )
        dfp_not_adunit3 = {
            'excludedAdUnits': [
                {
                    'includeDescendants': True,
                    'adUnitId': '3',
                },
            ],
        }
        # Check transform_inventory_targeting_to_dfp
        self.assertTrue(check_equal(
            dfp_not_adunit3,
            transform_inventory_targeting_to_dfp(not_adunit3),
        ))
        # Check transform_inventory_targeting_from_dfp
        self.assertTrue(check_equal(
            not_adunit3,
            transform_inventory_targeting_from_dfp(dfp_not_adunit3),
        ))

        adunit1_or_adunit2_and_not_adunit3 = TargetingCriterion(
            [adunit1_or_adunit2, not_adunit3],
            TargetingCriterion.OPERATOR.AND,
        )
        dfp_adunit1_or_adunit2_and_not_adunit3 = {
            'targetedAdUnits': [
                {
                    'includeDescendants': True,
                    'adUnitId': '1',
                },
                {
                    'includeDescendants': True,
                    'adUnitId': '2',
                },
            ],
            'excludedAdUnits': [
                {
                    'includeDescendants': True,
                    'adUnitId': '3',
                },
            ],
        }
        # Check transform_inventory_targeting_to_dfp
        self.assertTrue(check_equal(
            dfp_adunit1_or_adunit2_and_not_adunit3,
            transform_inventory_targeting_to_dfp(adunit1_or_adunit2_and_not_adunit3),
        ))
        # Check transform_inventory_targeting_from_dfp
        self.assertTrue(check_equal(
            adunit1_or_adunit2_and_not_adunit3,
            transform_inventory_targeting_from_dfp(dfp_adunit1_or_adunit2_and_not_adunit3),
        ))

    def test_geography_targeting_utils(self):
        geo1 = Geography(
            id='1',
            type='country',
            name='France',
        )
        geo2 = Geography(
            id='2',
            type='country',
            name='Germany',
        )
        geo3 = Geography(
            id='3',
            type='country',
            name='Greece',
        )

        geo1_or_geo2 = TargetingCriterion(
            [geo1, geo2],
            TargetingCriterion.OPERATOR.OR,
        )
        dfp_geo1_or_geo2 = {
            'targetedLocations': [
                {
                    'type': 'country',
                    'displayName': 'France',
                    'id': '1',
                },
                {
                    'type': 'country',
                    'displayName': 'Germany',
                    'id': '2',
                },
            ],
        }

        # Check transform_inventory_targeting_to_dfp
        self.assertTrue(check_equal(
            dfp_geo1_or_geo2,
            transform_geography_targeting_to_dfp(geo1_or_geo2),
        ))
        # Check transform_inventory_targeting_from_dfp
        self.assertTrue(check_equal(
                geo1_or_geo2,
                transform_geography_targeting_from_dfp(dfp_geo1_or_geo2),
        ))

        not_geo3 = TargetingCriterion(
            [TargetingCriterion([geo3], TargetingCriterion.OPERATOR.OR)],
            TargetingCriterion.OPERATOR.NOT,
        )
        dfp_not_geo3 = {
            'excludedLocations': [
                {
                    'type': 'country',
                    'displayName': 'Greece',
                    'id': '3',
                },
            ],
        }
        # Check transform_inventory_targeting_to_dfp
        self.assertTrue(check_equal(
            dfp_not_geo3,
            transform_geography_targeting_to_dfp(not_geo3),
        ))
        # Check transform_inventory_targeting_from_dfp
        self.assertTrue(check_equal(
            not_geo3,
            transform_geography_targeting_from_dfp(dfp_not_geo3),
        ))

        geo1_or_geo2_and_not_geo3 = TargetingCriterion(
            [geo1_or_geo2, not_geo3],
            TargetingCriterion.OPERATOR.AND,
        )
        dfp_geo1_or_geo2_and_not_geo3 = {
            'targetedLocations': [
                {
                    'type': 'country',
                    'displayName': 'France',
                    'id': '1',
                },
                {
                    'type': 'country',
                    'displayName': 'Germany',
                    'id': '2',
                },
            ],
            'excludedLocations': [
                {
                    'type': 'country',
                    'displayName': 'Greece',
                    'id': '3',
                },
            ],
        }
        # Check transform_inventory_targeting_to_dfp
        self.assertTrue(check_equal(
            dfp_geo1_or_geo2_and_not_geo3,
            transform_geography_targeting_to_dfp(geo1_or_geo2_and_not_geo3),
        ))
        # Check transform_inventory_targeting_from_dfp
        self.assertTrue(check_equal(
            geo1_or_geo2_and_not_geo3,
            transform_geography_targeting_from_dfp(dfp_geo1_or_geo2_and_not_geo3),
        ))

if __name__ == "__main__":
    unittest.main()
