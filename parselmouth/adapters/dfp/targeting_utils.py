#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Parselmouth - DFP Targeting Utilities
"""

# Future-proof
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

# Standard Library Imports
from collections import defaultdict

# Parselmouth Imports
from parselmouth.constants import TechnologyTargetTypes
from parselmouth.exceptions import ParselmouthException
from parselmouth.targeting import AdUnit
from parselmouth.targeting import Custom
from parselmouth.targeting import Geography
from parselmouth.targeting import Placement
from parselmouth.targeting import TargetingCriterion
from parselmouth.targeting import TargetingData
from parselmouth.targeting import Technology


def clean_target_dict(data):
    """
    There are many unimplemented fields throughout parselmouth,
    for example some types of targeting are not yet implemented.
    In these cases, we must clean the dictionary before we pass
    it back to DFP. Fields like X.Type exist in many places, and these
    must be replaced with 'xsi_type' for exaample. Also, unneeded fields
    sometimes raise errors when passed back to DFP.

    @param data: dict
    @return: dict
    """
    if not isinstance(data, dict):
        return data

    # Track whether this is at bottom level of a nested dictionary
    at_bottom = True
    cln_dict = {}
    for _key, _val in data.items():
        if isinstance(_val, dict):
            at_bottom = False
            cln_dict[_key] = clean_target_dict(_val)
        elif isinstance(_val, list):
            at_bottom = False
            cln_dict[_key] = [
                clean_target_dict(d) for d in _val
            ]
        elif _key.find('_Type') >= 0:
            cln_dict['xsi_type'] = _val
        else:
            cln_dict[_key] = _val

    if at_bottom:
        # If you are at lowest level dictionary, only include
        # id and type fields
        clean_dict = {}
        for _key, _val in cln_dict.items():
            if _key.find('id') >= 0 or _key.find('Id') >= 0:
                clean_dict[_key] = _val
            elif _key == 'xsi_type':
                clean_dict[_key] = _val
    else:
        clean_dict = cln_dict

    return clean_dict


def _make_criterion_from_lists(includes, excludes):
    """
    Give a list of items to include and exclude,
    construct the corresponding TargetingCriterion

    @param includes: list
    @param excludes: list
    @return: TargetingCriterion|None
    """
    incl = TargetingCriterion(includes, TargetingCriterion.OPERATOR.OR)
    excl = TargetingCriterion(excludes, TargetingCriterion.OPERATOR.OR)
    if includes and excludes:
        return incl & (~excl)
    elif includes:
        return incl
    elif excludes:
        return ~excl
    else:
        return None


def _adunit_from_dfp(adunit):
    """
    Convert dfp dictionary to AdUnit targeting model

    @param adunit: dict
    @return: AdUnit
    """
    include_descendants = adunit.get('includeDescendants', False)

    return AdUnit(
        id=adunit['adUnitId'],
        include_descendants=include_descendants,
    )


def _adunit_to_dfp(adunit):
    """
    Convert AdUnit targeting model to dfp dictionary

    @param adunit: AdUnit
    @return: dict
    """
    return {
        'adUnitId': adunit.id,
        'includeDescendants': adunit.include_descendants,
    }


def transform_inventory_targeting_from_dfp(targeting):
    """
    Convert dfp dictionary to inventory targeting model

    @param targeting: dict
    @return: TargetingCriterion
    """
    if not targeting:
        return None

    include_list = []

    placement_ids = targeting.get('targetedPlacementIds', [])
    for pl_id in placement_ids:
        place = Placement(id=pl_id)
        include_list.append(place)

    ad_units = targeting.get('targetedAdUnits', [])
    for au in ad_units:
        include_list.append(_adunit_from_dfp(au))

    exclude_list = []
    ad_units = targeting.get('excludedAdUnits', [])
    for au in ad_units:
        exclude_list.append(_adunit_from_dfp(au))

    return _make_criterion_from_lists(include_list, exclude_list)


def transform_inventory_targeting_to_dfp(targeting):
    """
    Convert inventory targeting model to dfp dictionary

    @param adunit: TargetingCriterion
    @return: dict
    """
    targeted_placements = []
    targeted_adunits = []
    excluded_adunits = []

    includes, excludes = targeting.get_includes_and_excludes()

    for i in includes:
        if isinstance(i, AdUnit):
            targeted_adunits.append(_adunit_to_dfp(i))
        elif isinstance(i, Placement):
            targeted_placements.append(i.id)

    for e in excludes:
        if isinstance(e, AdUnit):
            excluded_adunits.append(_adunit_to_dfp(e))

    target_dict = {}
    if targeted_placements:
        target_dict['targetedPlacementIds'] = targeted_placements

    if targeted_adunits:
        target_dict['targetedAdUnits'] = targeted_adunits

    if excluded_adunits:
        target_dict['excludedAdUnits'] = excluded_adunits

    return target_dict


def _geo_from_dfp(geo):
    """
    Convert dfp dictionary to Geography targeting model

    @param adunit: dict
    @return: Geography
    """
    return Geography(
        id=geo['id'],
        type=geo['type'],
        name=geo['displayName'],
    )


def _geo_to_dfp(geo):
    """
    Convert Geography targeting model to dfp dictionary

    @param adunit: Geography
    @return: dict
    """
    return {
        'type': geo.type,
        'displayName': geo.name,
        'id': geo.id
    }


def transform_geography_targeting_from_dfp(targeting):
    """
    Convert dfp dictionary to geography targeting model

    @param targeting: dict
    @return: TargetingCriterion
    """
    if not targeting:
        return None

    exclude_list = []
    excluded = targeting.get('excludedLocations', [])
    for g in excluded:
        exclude_list.append(_geo_from_dfp(g))

    include_list = []
    included = targeting.get('targetedLocations', [])
    for g in included:
        include_list.append(_geo_from_dfp(g))

    return _make_criterion_from_lists(include_list, exclude_list)


def transform_geography_targeting_to_dfp(targeting):
    """
    Convert geography targeting model to dfp dictionary

    @param adunit: TargetingCriterion
    @return: dict
    """
    included_locations = []
    excluded_locations = []

    includes, excludes = targeting.get_includes_and_excludes()

    for i in includes:
        if isinstance(i, Geography):
            included_locations.append(_geo_to_dfp(i))

    for e in excludes:
        if isinstance(e, Geography):
            excluded_locations.append(_geo_to_dfp(e))

    target_dict = {}
    if included_locations:
        target_dict['targetedLocations'] = included_locations

    if excluded_locations:
        target_dict['excludedLocations'] = excluded_locations

    return target_dict


TECHNOLOGY_KEY_MAP = {
    TechnologyTargetTypes.bandwidth_group: {
        'target_name': 'BandwidthGroupTargeting',
        'type': 'list',
        'list_name': 'bandwidthGroups',
    },
    TechnologyTargetTypes.browser: {
        'target_name': 'browserTargeting',
        'type': 'list',
        'list_name': 'browsers',
    },
    TechnologyTargetTypes.browser_language: {
        'target_name': 'browserLanguageTargeting',
        'type': 'list',
        'list_name': 'browserLanguages',
    },
    TechnologyTargetTypes.device_manufacturer: {
        'target_name': 'DeviceManufacturerTargeting',
        'type': 'list',
        'list_name': 'deviceManufacturers',
    },
    TechnologyTargetTypes.mobile_carrier: {
        'target_name': 'MobileCarrierTargeting',
        'type': 'list',
        'list_name': 'mobileCarriers',
    },
    TechnologyTargetTypes.operating_system: {
        'target_name': 'OperatingSystemTargeting',
        'type': 'list',
        'list_name': 'operatingSystems',
    },
    TechnologyTargetTypes.device_capability: {
        'target_name': 'DeviceCapabilityTargeting',
        'type': 'categorical',
        'include': 'targetedDeviceCapabilities',
        'exclude': 'excludedDeviceCapabilities',
    },
    TechnologyTargetTypes.device_category: {
        'target_name': 'deviceCategoryTargeting',
        'type': 'categorical',
        'include': 'targetedDeviceCategories',
        'exclude': 'excludedDeviceCategories',
    },
    TechnologyTargetTypes.mobile_device: {
        'target_name': 'MobileDeviceTargeting',
        'type': 'categorical',
        'include': 'targetedMobileDevices',
        'exclude': 'excludedMobileDevices',
    },
    TechnologyTargetTypes.mobile_device_submodel: {
        'target_name': 'MobileDeviceSubmodelTargeting',
        'type': 'categorical',
        'include': 'targetedMobileDeviceSubmodels',
        'exclude': 'excludedMobileDeviceSubmodels',
    },
    TechnologyTargetTypes.operating_system_version: {
        'target_name': 'OperatingSystemVersionTargeting',
        'type': 'categorical',
        'include': 'targetedOperatingSystemVersions',
        'exclude': 'excludedOperatingSystemVersions',
    },
}
"""
dict, The way DFP handles technology targeting information
    is completely insane. This dictionary tells us how technology
    data must be handled for DFP to understand it properly.
    There are two different format types:
        1) list: A single list of ids is given, and a field
            isTargeted: True|False determines whether this list
            is targeted or not.
        2) categorical: Two lists of included/excluded ids
            are given.

    This dictionary also contains all the key names needed by DFP.
    For some reason they like to pluralize words in proper English
    in a way that cannot be easily automated.

    See: https://developers.google.com/doubleclick-publishers/docs/reference/v201408/ProposalLineItemService.TechnologyTargeting
"""


def transform_technology_targeting_from_dfp(targeting):
    """
    Convert DFP technology targeting data to TargetingCriterion

    @param targeting: dict
    @return: TargetingCriterion
    """
    if not targeting:
        return None

    target_data = {
        'include': [],
        'exclude': [],
    }

    for tech_type, _map in TECHNOLOGY_KEY_MAP.items():
        target = targeting.get(_map['target_name'])
        if not target:
            continue

        _map_type = _map['type']
        if _map_type == 'list':
            _list_name = _map['list_name']
            browser_list = []
            for item in target[_list_name]:
                tech_target = Technology(
                    id=item['id'],
                    name=item.get('name'),
                    type=tech_type,
                )
                browser_list.append(tech_target)
            # The isTargeted key determines whether
            # to target this entire list or not
            if target['isTargeted']:
                target_data['include'] += browser_list
            else:
                target_data['exclude'] += browser_list

        elif _map_type == 'categorical':
            # Get lists of items to be included and excluded
            for _cat_key in ['include', 'exclude']:
                dfp_key = _map[_cat_key]
                raw_data = target.get(dfp_key, [])
                for item in raw_data:
                    tech_target = Technology(
                        id=item['id'],
                        name=item.get('name'),
                        type=tech_type,
                    )
                    target_data[_cat_key].append(tech_target)

    # Build TargetingCriterion from list of includes and excludes
    includes = target_data['include']
    inc = TargetingCriterion(includes, TargetingCriterion.OPERATOR.OR)
    excludes = target_data['exclude']
    exl = TargetingCriterion(excludes, TargetingCriterion.OPERATOR.OR)
    if includes and excludes:
        return inc & (~exl)
    elif includes:
        return inc
    elif excludes:
        return ~exl
    else:
        return None


def transform_technology_targeting_to_dfp(targeting):
    """
    Convert TargetingCriterion to DFP technology targeting data
    in dictionary form.

    @param targeting: TargetingCriterion
    @return: dict
    """
    includes, excludes = targeting.get_includes_and_excludes()
    targeting_data = {
        'include': includes,
        'exclude': excludes,
    }

    dict_info = defaultdict(lambda: defaultdict(list))
    for criterion_type, criterion in targeting_data.iteritems():
        for item in criterion:
            tech_type = item.type

            _map = TECHNOLOGY_KEY_MAP[tech_type]
            _map_type = _map['type']
            _target_name = _map['target_name']

            # Only output the id of the technology target
            dfp_doc = {'id': item.id}
            if _map_type == 'list':
                _list_name = _map['list_name']
                dict_info[_target_name][_list_name].append(dfp_doc)
                dict_info[_target_name]['isTargeted'] = (criterion_type == 'include')
            elif _map_type == 'categorical':
                _category_name = _map[criterion_type]
                dict_info[_target_name][_category_name].append(dfp_doc)

    # Convert defaultdict to dictionary
    dfp_dict = {}
    for _key, _val in dict_info.items():
        dfp_dict[_key] = dict(_val)

    return dfp_dict


"""
The following targeting utils are unimplemented at this time.
If any of these fields need to be used within python,
these methods will need to be implemented.  For now, dictionaries
of native DFP structure will be stored into these targeting
fields to ensure that the data is not lost.
"""


def transform_user_domain_targeting_from_dfp(targeting):
    return clean_target_dict(targeting)


def transform_user_domain_targeting_to_dfp(targeting):
    return targeting or None


def transform_day_part_targeting_from_dfp(targeting):
    return clean_target_dict(targeting)


def transform_day_part_targeting_to_dfp(targeting):
    return targeting or None


def transform_video_content_targeting_from_dfp(targeting):
    return clean_target_dict(targeting)


def transform_video_content_targeting_to_dfp(targeting):
    return targeting or None


def transform_video_position_targeting_from_dfp(targeting):
    return clean_target_dict(targeting)


def transform_video_position_targeting_to_dfp(targeting):
    return targeting or None


def _recursive_custom_from_dfp(data):
    """
    Convert dfp dictionary to custom targeting model

    @param targeting: dict
    @return: TargetingCriterion
    """
    children = data.get('children', [])
    if children:
        operator = data['logicalOperator']
        target_list = [_recursive_custom_from_dfp(c) for c in children]
        return TargetingCriterion(target_list, operator)
    else:
        # Base case
        values = []

        if data.get('audienceSegmentIds'):
            node_key = 'AudienceSegmentCriteria'
            _id_key = 'audienceSegmentIds'
            value_ids = data[_id_key]
            for vid in value_ids:
                values.append(
                    Custom(
                        id=vid,
                        id_key=_id_key,
                        node_key=node_key,
                    )
                )
        else:
            node_key = 'CustomCriteria'
            _id_key = 'valueIds'
            value_ids = data[_id_key]
            key_id = data['keyId']
            for vid in value_ids:
                values.append(Custom(
                    id=vid,
                    id_key=_id_key,
                    parent_id=key_id,
                    node_key=node_key,
                ))

        targeting = TargetingCriterion(values, TargetingCriterion.OPERATOR.OR)
        if data['operator'] == 'IS':
            return targeting
        else:
            return ~targeting


def transform_custom_targeting_from_dfp(targeting):
    """
    Convert dfp dictionary to custom targeting model

    @param targeting: dict
    @return: TargetingCriterion
    """
    if not targeting:
        return None

    return _recursive_custom_from_dfp(targeting)


def _custom_target_list_to_child_list(custom_targets, is_operator):
    """
    Convert a list of custom targets to a list of dictionaries
    formatted for use in DFP

    @param custom_targets: list(Custom)
    @param is_operator: str, 'IS' or 'IS_NOT'
    @return: list(dict)
    """
    _children = defaultdict(lambda: defaultdict(list))
    for value in custom_targets:
        _children[value.parent_id][is_operator].append(value)

    dfp_children = []
    for _parent_id, _operations in _children.iteritems():
        for _operator, _values in _operations.iteritems():
            _value_target_ids = []
            _node_type = None
            _node_value_type = None

            for _custom_value in _values:
                _this_node_type = _custom_value.node_key
                _this_node_value_type = _custom_value.id_key

                if not _node_type and not _node_value_type:
                    _node_type = _this_node_type
                    _node_value_type = _this_node_value_type

                if (_this_node_type != _custom_value.node_key or
                        _this_node_value_type != _custom_value.id_key):
                    raise ParselmouthException(
                        "Could not serialize Custom Target: %s" % _custom_value
                    )
                _value_target_ids.append(_custom_value.id)

            _doc = {
                'operator': _operator,
                'xsi_type': _node_type,
                _node_value_type: _value_target_ids,
            }
            if _parent_id:
                _doc['keyId'] = _parent_id

            dfp_children.append(_doc)

    return dfp_children


def _recursive_custom_to_dfp(targeting):
    """
    Convert custom targeting model to dfp dictionary

    @param targeting: TargetingCriterion
    @return: dict
    """
    operator, targets = targeting.get_data()

    if operator == TargetingCriterion.OPERATOR.NOT:
        # In this case targets is of the form [TargetingCriterion]
        # NOTE: NOT operators are always a list of size 1
        # In this case we redefine operator and targets
        operator, targets = targets[0].get_data()
        is_operator = 'IS_NOT'
    else:
        is_operator = 'IS'

    if isinstance(targets[0], Custom):
        # In this case, we are in the deepest level of the targeting
        # targets is of type list(Custom)
        children = _custom_target_list_to_child_list(targets, is_operator)
    elif len(targets) == 1:
        # targets is a list of exactly one TargetingCriterion
        # To avoid redundant nesting, we return the output of this
        # individual result
        return _recursive_custom_to_dfp(targets[0])
    else:
        # In this case there are further depths to the targeting
        # targets is of type list(TargetingCriterion)
        children = [_recursive_custom_to_dfp(c) for c in targets]

    return {
        'xsi_type': 'CustomCriteriaSet',
        'children': children,
        'logicalOperator': operator
    }


def transform_custom_targeting_to_dfp(targeting):
    """
    Convert custom targeting model to dfp dictionary

    @param targeting: TargetingCriterion
    @return: dict
    """
    if not targeting:
        return None

    return _recursive_custom_to_dfp(targeting)


def transform_targeting_data_from_dfp(targeting):
    """
    Convert dictionary-representation for a SUDS creative object into a
    Parselmouth representation of a Creative

    @param targeting: dict, dictionary-representation of a DFP SUDS response
        for a single creative
    @return: parselmouth.delivery.TargetingData
    """

    return TargetingData(
        inventory=transform_inventory_targeting_from_dfp(targeting.get('inventoryTargeting')),
        geography=transform_geography_targeting_from_dfp(targeting.get('geoTargeting')),
        day_part=transform_day_part_targeting_from_dfp(targeting.get('dayPartTargeting')),
        user_domain=transform_user_domain_targeting_from_dfp(targeting.get('userDomainTargeting')),
        technology=transform_technology_targeting_from_dfp(targeting.get('technologyTargeting')),
        video_content=transform_video_content_targeting_from_dfp(targeting.get('contentTargeting')),
        video_position=transform_video_position_targeting_from_dfp(targeting.get('videoPositionTargeting')),
        custom=transform_custom_targeting_from_dfp(targeting.get('customTargeting')),
    )


def transform_targeting_data_to_dfp(targeting):
    """
    Convert dictionary-representation for a SUDS creative object into a
    Parselmouth representation of a Creative

    @param targeting: dict, dictionary-representation of a DFP SUDS response
        for a single creative
    @return: parselmouth.delivery.TargetingData
    """
    dfp_targeting = {}

    if targeting.inventory:
        dfp_targeting['inventoryTargeting'] = transform_inventory_targeting_to_dfp(targeting.inventory)

    if targeting.geography:
        dfp_targeting['geoTargeting'] = transform_geography_targeting_to_dfp(targeting.geography)

    if targeting.day_part:
        dfp_targeting['dayPartTargeting'] = transform_day_part_targeting_to_dfp(targeting.day_part)

    if targeting.technology:
        dfp_targeting['technologyTargeting'] = transform_technology_targeting_to_dfp(targeting.technology)

    if targeting.video_content:
        dfp_targeting['contentTargeting'] = transform_video_content_targeting_to_dfp(targeting.video_content)

    if targeting.video_position:
        dfp_targeting['videoPositionTargeting'] = transform_video_position_targeting_to_dfp(targeting.video_position)

    if targeting.custom:
        dfp_targeting['customTargeting'] = transform_custom_targeting_to_dfp(targeting.custom)

    return dfp_targeting

