#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Parselmouth - Ad Server Object Models

Base Interfaces for ad server items
"""

# Future-proof
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

# Standard Library Imports
from abc import ABCMeta
from pprint import pformat
import logging

# Global Variable Definitions
_class_name_map = None
"""
dict, global variable used to contain mappings of the string name for an
      object to its class
"""


def _initialize_class_name_map():
    """
    Create a dictionary mapping each ObjectModel
    child to its name.  This is used for cerealizing
    dictionary objects back to ObjectModels
    """
    global _class_name_map

    from parselmouth.delivery import Cost
    from parselmouth.delivery import Goal
    from parselmouth.delivery import Stats
    from parselmouth.delivery import DeliveryMeta
    from parselmouth.delivery import Creative
    from parselmouth.delivery import LineItem
    from parselmouth.delivery import Campaign
    from parselmouth.targeting import TargetingData
    from parselmouth.targeting import AdUnit
    from parselmouth.targeting import Placement
    from parselmouth.targeting import Geography
    from parselmouth.targeting import Technology
    from parselmouth.targeting import DayPart
    from parselmouth.targeting import UserDomain
    from parselmouth.targeting import Custom
    from parselmouth.targeting import VideoContent
    from parselmouth.targeting import VideoPosition
    from parselmouth.targeting import TargetingCriterion

    _class_name_map = {
        'Cost': Cost,
        'Goal': Goal,
        'Stats': Stats,
        'DeliveryMeta': DeliveryMeta,
        'Creative': Creative,
        'LineItem': LineItem,
        'Campaign': Campaign,
        'TargetingData': TargetingData,
        'AdUnit': AdUnit,
        'Placement': Placement,
        'Geography': Geography,
        'Technology': Technology,
        'DayPart': DayPart,
        'UserDomain': UserDomain,
        'Custom': Custom,
        'VideoContent': VideoContent,
        'VideoPosition': VideoPosition,
        'TargetingCriterion': TargetingCriterion,
    }


class ObjectModel(object):
    """
    Abstract Base for all parselmouth object models
    """

    __metaclass__ = ABCMeta
    """
    Ensure that this abstract class is extended
    """

    ignored_comparable_keys = [
        'last_modified',
        'last_modified_by',
        'preview_url',
    ]
    """
    list(str), list of keys that will be ignored when comparing objects

    NOTES:
        * Unfortunately, google DFP appears to encode a hash into the
        preview url response of a creative. This is likely part of some
        measure to enforce a TTL on an asset or prevent it from being
        scraped continuously. This means that we can't really check
        that the urls are the same :(
            One thing we could do to get around this is to store the
            base64 encoding of the image in the object we test against
            and download the asset from the preview url given by DFP.
            Then all we need to do is compare the base64 encoded assets.

    """

    def __str__(self):
        """
        Human readable representation of this object
        @return: str
        """
        pretty = False
        return "{class_name}({vars})".format(
            class_name=self.__class__.__name__,
            vars=pformat(vars(self)) if pretty else str(vars(self))
        )

    def __repr__(self):
        return str(self)

    def __ne__(self, other):
        return not(self == other)

    def __getitem__(self, key):
        return vars(self)[key]

    def __eq__(self, other):
        if isinstance(other, ObjectModel):
            self_dict = vars(self)
            other_dict = vars(other)
            for _key, _value in self_dict.items():

                # Skip comparison of keys like "last_modified" that
                # don't really communicate anything useful
                if _key in self.ignored_comparable_keys:
                    continue

                if _key not in other_dict:
                    logging.warning(
                        "{0} key is not in the other object".format(_key)
                    )
                    return False
                elif other_dict.get(_key) != _value:
                    logging.debug(
                        "Other value ({0}) does not equal this value ({1})".format(
                            other_dict.get(_key),
                            _value
                        )
                    )
                    return False
            return True
        return NotImplemented

    def to_doc(self):
        """
        Serialize this object into a dictionary

        @return: dict
        """
        doc = {}
        for _key, _value in vars(self).items():
            if isinstance(_value, ObjectModel):
                doc[_key] = _value.to_doc()
            else:
                doc[_key] = _value

        # Save metadata for use when re-cerealizing data
        doc['_metadata'] = {
            'cls': self.__class__.__name__,
        }
        return doc

    @classmethod
    def from_doc(cls, doc):
        """
        Convert a dictionary (from to_doc) back to its
        native ObjectModel type

        @param doc: dict
        """
        if not _class_name_map:
            _initialize_class_name_map()

        params = {}
        for _key, _value in doc.items():
            if _key == '_metadata':
                continue
            elif isinstance(_value, dict):
                cls_name = _value['_metadata']['cls']
                params[_key] = _class_name_map[cls_name].from_doc(_value)
            else:
                params[_key] = _value

        # In the case when ObjectModel.from_doc is called
        # outside of the child class, read the class name
        # from metadata and call that classes init function
        _doc_cls_name = doc['_metadata']['cls']
        if _class_name_map.get(_doc_cls_name):
            _doc_cls = _class_name_map[_doc_cls_name]
        else:
            _doc_cls = cls

        return _doc_cls(**params)

    def __hash__(self):
        return hash(frozenset(vars(self)))
