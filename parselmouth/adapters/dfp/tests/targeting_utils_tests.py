import unittest

from parselmouth.utils.check import check_equal
from parselmouth.constants import TechnologyTargetTypes
from parselmouth.targeting import AdUnit
from parselmouth.targeting import Geography
from parselmouth.targeting import Technology
from parselmouth.targeting import Custom
from parselmouth.targeting import TargetingCriterion

from parselmouth.adapters.dfp.targeting_utils import transform_inventory_targeting_from_dfp
from parselmouth.adapters.dfp.targeting_utils import transform_inventory_targeting_to_dfp
from parselmouth.adapters.dfp.targeting_utils import transform_geography_targeting_from_dfp
from parselmouth.adapters.dfp.targeting_utils import transform_geography_targeting_to_dfp
from parselmouth.adapters.dfp.targeting_utils import transform_technology_targeting_from_dfp
from parselmouth.adapters.dfp.targeting_utils import transform_technology_targeting_to_dfp
from parselmouth.adapters.dfp.targeting_utils import transform_custom_targeting_from_dfp
from parselmouth.adapters.dfp.targeting_utils import transform_custom_targeting_to_dfp


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

    def test_technology_targeting_utils(self):
        tech1 = Technology(
            id='1',
            type=TechnologyTargetTypes.browser,
            name='chrome',
        )
        tech2 = Technology(
            id='2',
            type=TechnologyTargetTypes.device_category,
            name='mobile',
        )
        tech3 = Technology(
            id='3',
            type=TechnologyTargetTypes.device_category,
            name='desktop',
        )

        tech1_target = TargetingCriterion(tech1)
        dfp_tech1 = {
            'browserTargeting': {
                'browsers': [
                    {
                        'id': '1',
                    },
                ],
                'isTargeted': True,
            },
        }
        self.assertTrue(check_equal(
            dfp_tech1,
            transform_technology_targeting_to_dfp(tech1_target),
        ))

        not_tech1 = ~tech1_target
        dfp_not_tech1 = {
            'browserTargeting': {
                'browsers': [
                    {
                        'id': '1',
                    },
                ],
                'isTargeted': False,
            },
        }
        self.assertTrue(check_equal(
            dfp_not_tech1,
            transform_technology_targeting_to_dfp(not_tech1),
        ))

        tech2_or_tech3 = TargetingCriterion(
            [tech2, tech3],
            TargetingCriterion.OPERATOR.OR,
        )
        dfp_tech1_or_tech2 = {
            'deviceCategoryTargeting': {
                'targetedDeviceCategories': [
                    {
                        'id': '2',
                    },
                    {
                        'id': '3',
                    },
                ],
            },
        }
        self.assertTrue(check_equal(
            dfp_tech1_or_tech2,
            transform_technology_targeting_to_dfp(tech2_or_tech3),
        ))

        tech2_and_not_tech3 = TargetingCriterion(tech2) & ~TargetingCriterion(tech3)
        dfp_tech2_and_not_tech3 = {
            'deviceCategoryTargeting': {
                'targetedDeviceCategories': [
                    {
                        'id': '2',
                    },
                ],
                'excludedDeviceCategories': [
                    {
                        'id': '3',
                    },
                ],
            },
        }
        self.assertTrue(check_equal(
            dfp_tech2_and_not_tech3,
            transform_technology_targeting_to_dfp(tech2_and_not_tech3),
        ))

        tech1_and_tech2_and_not_tech3 = TargetingCriterion(tech1) & tech2_and_not_tech3
        dfp_tech1_and_tech2_and_not_tech3 = {
            'deviceCategoryTargeting': {
                'targetedDeviceCategories': [
                    {
                        'id': '2',
                    },
                ],
                'excludedDeviceCategories': [
                    {
                        'id': '3',
                    },
                ],
            },
            'browserTargeting': {
                'browsers': [
                    {
                        'id': '1',
                    },
                ],
                'isTargeted': True,
            },
        }
        self.assertTrue(check_equal(
            dfp_tech1_and_tech2_and_not_tech3,
            transform_technology_targeting_to_dfp(tech1_and_tech2_and_not_tech3),
        ))

        # Test reflexivity
        self.assertTrue(check_equal(
            dfp_tech1_and_tech2_and_not_tech3,
            transform_technology_targeting_to_dfp(
                transform_technology_targeting_from_dfp(
                    dfp_tech1_and_tech2_and_not_tech3,
                ),
            ),
        ))

    def test_custom_targeting_utils(self):
        custom1 = Custom(
            id='1',
            name='rich',
            id_key='audienceSegmentIds',
            node_key='AudienceSegmentCriteria',
        )
        custom2 = Custom(
            id='2',
            parent_id='gender',
            name='female',
            id_key='valueIds',
            node_key='CustomCriteria',
        )
        custom3 = Custom(
            id='3',
            parent_id='gender',
            name='male',
            id_key='valueIds',
            node_key='CustomCriteria',
        )

        custom1_target = TargetingCriterion(custom1)
        dfp_custom1 = {
            'logicalOperator': 'OR',
            'xsi_type': 'CustomCriteriaSet',
            'children': [
                {
                    'audienceSegmentIds': ['1'],
                    'operator': 'IS',
                    'xsi_type': 'AudienceSegmentCriteria',
                },
            ],

        }

        self.assertTrue(check_equal(
            dfp_custom1,
            transform_custom_targeting_to_dfp(custom1_target),
        ))

        # Test reflexivity
        self.assertTrue(check_equal(
            dfp_custom1,
            transform_custom_targeting_to_dfp(
                transform_custom_targeting_from_dfp(
                    dfp_custom1,
                ),
            ),
        ))

        custom2_or_custom3 = TargetingCriterion(
            [custom2, custom3],
            TargetingCriterion.OPERATOR.OR,
        )
        dfp_custom2_or_custom3 = {
            'logicalOperator': 'OR',
            'xsi_type': 'CustomCriteriaSet',
            'children': [
                {
                    'valueIds': ['2', '3'],
                    'keyId': 'gender',
                    'operator': 'IS',
                    'xsi_type': 'CustomCriteria',
                },
            ],

        }
        self.assertTrue(check_equal(
            dfp_custom2_or_custom3,
            transform_custom_targeting_to_dfp(custom2_or_custom3),
        ))

        custom2_and_not_custom3 = TargetingCriterion(custom2) & ~TargetingCriterion(custom3)
        dfp_custom2_and_not_custom3 = {
            'logicalOperator': 'AND',
            'xsi_type': 'CustomCriteriaSet',
            'children': [
                {
                    'logicalOperator': 'OR',
                    'xsi_type': 'CustomCriteriaSet',
                    'children': [
                        {
                            'valueIds': ['2'],
                            'keyId': 'gender',
                            'operator': 'IS',
                            'xsi_type': 'CustomCriteria',
                        },
                    ],
                },
                {
                    'logicalOperator': 'OR',
                    'xsi_type': 'CustomCriteriaSet',
                    'children': [
                        {
                            'valueIds': ['3'],
                            'keyId': 'gender',
                            'operator': 'IS_NOT',
                            'xsi_type': 'CustomCriteria',
                        },
                    ],
                },
            ],

        }
        self.assertTrue(check_equal(
            dfp_custom2_and_not_custom3,
            transform_custom_targeting_to_dfp(custom2_and_not_custom3),
        ))

        custom1_and_custom2_and_not_custom3 = custom1_target & custom2_and_not_custom3
        dfp_custom1_and_custom2_and_not_custom3 = {
            'logicalOperator': 'AND',
            'xsi_type': 'CustomCriteriaSet',
            'children': [
                {
                    'logicalOperator': 'OR',
                    'xsi_type': 'CustomCriteriaSet',
                    'children': [
                        {
                            'audienceSegmentIds': ['1'],
                            'operator': 'IS',
                            'xsi_type': 'AudienceSegmentCriteria',
                        },
                    ],
                },
                {
                    'logicalOperator': 'AND',
                    'xsi_type': 'CustomCriteriaSet',
                    'children': [
                        {
                            'logicalOperator': 'OR',
                            'xsi_type': 'CustomCriteriaSet',
                            'children': [
                                {
                                    'valueIds': ['2'],
                                    'keyId': 'gender',
                                    'operator': 'IS',
                                    'xsi_type': 'CustomCriteria',
                                },
                            ],
                        },
                        {
                            'logicalOperator': 'OR',
                            'xsi_type': 'CustomCriteriaSet',
                            'children': [
                                {
                                    'valueIds': ['3'],
                                    'keyId': 'gender',
                                    'operator': 'IS_NOT',
                                    'xsi_type': 'CustomCriteria',
                                },
                            ],
                        },
                    ],

                }
            ],

        }
        self.assertTrue(check_equal(
            dfp_custom1_and_custom2_and_not_custom3,
            transform_custom_targeting_to_dfp(custom1_and_custom2_and_not_custom3),
        ))

        custom1_or_custom2_and_not_custom3 = custom1_target | custom2_and_not_custom3
        dfp_custom1_or_custom2_and_not_custom3 = {
            'logicalOperator': 'OR',
            'xsi_type': 'CustomCriteriaSet',
            'children': [
                {
                    'logicalOperator': 'OR',
                    'xsi_type': 'CustomCriteriaSet',
                    'children': [
                        {
                            'audienceSegmentIds': ['1'],
                            'operator': 'IS',
                            'xsi_type': 'AudienceSegmentCriteria',
                        },
                    ],
                },
                {
                    'logicalOperator': 'AND',
                    'xsi_type': 'CustomCriteriaSet',
                    'children': [
                        {
                            'logicalOperator': 'OR',
                            'xsi_type': 'CustomCriteriaSet',
                            'children': [
                                {
                                    'valueIds': ['2'],
                                    'keyId': 'gender',
                                    'operator': 'IS',
                                    'xsi_type': 'CustomCriteria',
                                },
                            ],
                        },
                        {
                            'logicalOperator': 'OR',
                            'xsi_type': 'CustomCriteriaSet',
                            'children': [
                                {
                                    'valueIds': ['3'],
                                    'keyId': 'gender',
                                    'operator': 'IS_NOT',
                                    'xsi_type': 'CustomCriteria',
                                },
                            ],
                        },
                    ],

                }
            ],

        }
        self.assertTrue(check_equal(
            dfp_custom1_or_custom2_and_not_custom3,
            transform_custom_targeting_to_dfp(custom1_or_custom2_and_not_custom3),
        ))

        custom1_or_custom2_or_custom3 = custom1_target | custom2_or_custom3
        dfp_custom1_or_custom2_or_custom3 = {
            'logicalOperator': 'OR',
            'xsi_type': 'CustomCriteriaSet',
            'children': [
                {
                    'audienceSegmentIds': ['1'],
                    'operator': 'IS',
                    'xsi_type': 'AudienceSegmentCriteria',
                },
                {
                    'valueIds': ['2', '3'],
                    'keyId': 'gender',
                    'operator': 'IS',
                    'xsi_type': 'CustomCriteria',
                }
            ],

        }
        self.assertTrue(check_equal(
            dfp_custom1_or_custom2_or_custom3,
            transform_custom_targeting_to_dfp(custom1_or_custom2_or_custom3),
        ))


if __name__ == "__main__":
    unittest.main()
