#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Parselmouth - Targeting Models

Base Interfaces for targeting items
"""

# Future-proof
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

# Standard Library Imports
from copy import deepcopy

# Parselmouth Imports
from parselmouth.exceptions import ParselmouthException
from parselmouth.model import ObjectModel
from parselmouth.utils.enum import Enum
from parselmouth.utils.check import check_equal


class AdUnit(ObjectModel):
    """
    Abstract Class for Ad Units

    An ad unit is a representation of one or more spaces where ads can
    be delivered.
    """
    def __init__(self,
                 id=None,
                 parent_id=None,
                 name=None,
                 include_descendants=True,
                 external_id=None,
                 external_name=None):
        self.id = id
        self.parent_id = parent_id
        self.name = name
        self.include_descendants = include_descendants
        self.external_id = external_id
        self.external_name = external_name


class Placement(ObjectModel):
    """
    Abstract Class for Placements

    A placement is an optional grouping of ad units that make them
    easier to target all at once.
    """
    def __init__(self,
                 id=None,
                 parent_id=None,
                 name=None,
                 adunits=None,
                 external_id=None,
                 external_name=None):
        self.id = id
        self.parent_id = parent_id
        self.name = name
        self.adunits = adunits
        self.external_id = external_id
        self.external_name = external_name


class Geography(ObjectModel):
    """
    Abstract Class for geography targets
    """
    def __init__(self,
                 id=None,
                 parent_id=None,
                 type=None,
                 name=None,
                 external_id=None,
                 external_name=None):
        self.id = id
        self.parent_id = parent_id
        self.type = type
        self.name = name
        self.external_id = external_id
        self.external_name = external_name


class Technology(ObjectModel):
    """
    Abstract Class for technology targets
    """
    def __init__(self,
                 id=None,
                 parent_id=None,
                 name=None,
                 external_id=None,
                 external_name=None,
                 type=None,
                 version=None):
        self.id = id
        self.parent_id = parent_id
        self.name = name
        self.external_id = external_id
        self.external_name = external_name
        self.type = type
        self.version = version


class DayPart(ObjectModel):
    """
    Abstract Class for day part targets
    """
    def __init__(self,
                 day_of_week,
                 start,
                 end):
        self.day_of_week = day_of_week
        self.start = start
        self.end = end


class UserDomain(ObjectModel):
    """
    Abstract Class for user domain targets
    """
    def __init__(self,
                 domain):
        self.domain = domain


class Custom(ObjectModel):
    """
    Abstract Class for custom targets
    """
    def __init__(self,
                 id=None,
                 id_key=None,
                 parent_id=None,
                 name=None,
                 type=None,
                 external_id=None,
                 external_name=None,
                 descriptive_name=None,
                 node_key=None):
        self.id = id
        self.id_key = id_key
        self.parent_id = parent_id
        self.name = name
        self.type = type
        self.external_id = external_id
        self.external_name = external_name
        self.descriptive_name = descriptive_name
        self.node_key = node_key


class VideoContent(ObjectModel):
    """
    Abstract Class for video content targets
    """
    def __init__(self,
                 id=None,
                 parent_id=None,
                 name=None,
                 external_id=None,
                 external_name=None):
        self.id = id
        self.parent_id = parent_id
        self.name = name
        self.external_id = external_id
        self.external_name = external_name


class VideoPosition(ObjectModel):
    """
    Abstract Class for video position targets
    """
    def __init__(self,
                 id=None,
                 parent_id=None,
                 name=None,
                 external_id=None,
                 external_name=None):
        self.id = id
        self.parent_id = parent_id
        self.name = name
        self.external_id = external_id
        self.external_name = external_name


class TargetingCriterion(object):
    """
    Class for creating boolean combinations of target models
    """

    OPERATOR = Enum(['OR', 'AND', 'NOT'])
    """
    Enum, list of allowed operators
    """

    def __init__(self, target_list, operator=None):
        """
        @param target_list: list(ObjectModel)|list(TargetingCriterion)|ObjectModel
        @param operator: self.OPERATOR
        """
        if isinstance(target_list, ObjectModel):
            # Cast to list in case a single ObjectModel is inputed
            target_list = [target_list]
            operator = self.OPERATOR.OR

        if not operator in self.OPERATOR:
            raise ParselmouthException("Invalid operator")
        if not isinstance(target_list, list):
            raise ParselmouthException("Invalid target list")

        self._data = {operator: target_list}

    def __str__(self):
        return "{class_name}({data})".format(
            class_name=self.__class__.__name__,
            data=str(self._data),
        )

    def __repr__(self):
        return str(self)

    @classmethod
    def _add_criterion(cls, first, second, operator):
        """
        Add two criterion with & or |. If there would be
        a nested AND: { AND: { present in new criterion,
        squash the result into AND: [].

        @param first: TargetingCriterion
        @param second: TargetingCriterion
        @param operator: TargetingCriterion.OPERATOR
        @return: TargetingCriterion
        """
        assert isinstance(first, TargetingCriterion)
        assert isinstance(second, TargetingCriterion)
        assert operator in cls.OPERATOR

        op1, targets1 = first.get_data()
        op2, targets2 = second.get_data()

        first_is_extendable = op1 == operator or len(targets1) <= 1
        second_is_extendable = op2 == operator or len(targets2) <= 1
        # Are the targets of the same python type?
        same_types = type(targets1[0]) == type(targets2[0])

        if op1 == cls.OPERATOR.NOT or op2 == cls.OPERATOR.NOT:
            # If either operator is a not, do not
            # attempt to simplify the response
            new_target_list = [first, second]
        elif first_is_extendable and second_is_extendable and same_types:
            # If both summands are in agreement with new operator,
            # and their types match, then concatenate their targets
            new_target_list = targets1 + targets2
        else:
            new_target_list = [first, second]

        return TargetingCriterion(
            new_target_list,
            operator,
        )

    def remove_target(self, target):
        """
        Remove the specified target from the current criterion.
        We assume that the criterion has a AND [] construction, and
        furthermore that the target lies within the top-level AND.

        @param criterion: TargetingCriterion
        @param target: TargetingCriterion

        @return: TargetingCriterion|None
        """
        assert isinstance(target, TargetingCriterion)

        if self == target:
            return None

        op1, targets1 = self.get_data()
        op2, targets2 = target.get_data()

        if not op1 == self.OPERATOR.AND:
            raise ParselmouthException(
                "TargetingCriterion has wrong structure. Top-level operator not an AND."
            )

        if not len(targets2) == 1 or isinstance(targets2[0], TargetingCriterion):
            raise ParselmouthException(
                "Target should be a simple TargetingCriterion with a single ObjectModel."
            )

        target_object_model = targets2[0]

        target_index = None
        if target_object_model in targets1:
            target_index = targets1.index(target_object_model)

        if target in targets1:
            target_index = targets1.index(target)

        if target_index is None:
            raise ParselmouthException(
                "Target not found in top-level structure."
            )

        targets1 = deepcopy(targets1)
        targets1.pop(target_index)

        # Handle the following case which creates an extraneous AND:
        # AND: [TargetingCriterion] ---> TargetingCriterion
        if len(targets1) == 1 and isinstance(targets1[0], TargetingCriterion):
            return targets1[0]

        # Default to OR operator for single target:
        # AND: [ObjectModel] ---> OR: [ObjectModel]
        if len(targets1) == 1:
            op1 = self.OPERATOR.OR

        return TargetingCriterion(
            targets1,
            op1,
        )

    def __and__(self, other):
        return self._add_criterion(
            self, other, self.OPERATOR.AND,
        )

    def __or__(self, other):
        return self._add_criterion(
            self, other, self.OPERATOR.OR,
        )

    def __invert__(self):
        return TargetingCriterion(
            [self],
            self.OPERATOR.NOT,
        )

    def __ne__(self, other):
        return not(self == other)

    def __eq__(self, other):
        if not isinstance(other, TargetingCriterion):
            return False
        return check_equal(self._data, other._data)

    def get_data(self):
        """
        @return: operation, target_list
        """
        return self._data.items()[0]

    def to_doc(self):
        """
        Serialize this object into a dictionary

        @return: dict
        """
        doc = {}
        if not self._data:
            return doc

        for operator, _values in self._data.items():
            doc[operator] = [d.to_doc() for d in _values]

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
        tmp_doc = deepcopy(doc)
        del tmp_doc['_metadata']
        operator, doc_list = tmp_doc.items()[0]

        target_list = []
        for _doc in doc_list:
            if _doc['_metadata']['cls'] == 'TargetingCriterion':
                target_list.append(TargetingCriterion.from_doc(_doc))
            else:
                target_list.append(ObjectModel.from_doc(_doc))

        return cls(target_list, operator)

    def flatten(self):
        """
        Return flattened list of all targeting
        objects in self.  By default all targeting objects are
        returned.  Only one of includes_only or excludes_only
        may be True.

        @param includes_only: bool, only give ObjectModels that
            do not live under a NOT operator
        @param excludes_only: bool, only give ObjectModels that
            live under a NOT operator
        @return: list(ObjectModel)
        """
        models = []
        _, targets = self.get_data()
        for t in targets:
            if isinstance(t, ObjectModel):
                models += [t]
            elif isinstance(t, TargetingCriterion):
                models += t.flatten()

        return models

    def _get_includes(self):
        """
        Recursive function to get all targeting objects
        that do not live under a NOT operator

        @return: list(ObjectModel)
        """
        models = []
        op, targets = self.get_data()
        if op == self.OPERATOR.NOT:
            return models

        for t in targets:
            if isinstance(t, ObjectModel):
                models += [t]
            elif isinstance(t, TargetingCriterion):
                if op != self.OPERATOR.NOT:
                    models += t._get_includes()

        return models

    def get_includes_and_excludes(self):
        """
        Get a list of all targeting objects that
        are included in the target (do not live under a NOT),
        and a list of excluded targets(live under a NOT).

        WARNING: This functionality only works for simple
        targeting criterion that do not have very complex
        boolean construction. This only works for targeting
        criterion that have a scheme like:
            (OR: [1,2,3]) & (NOT: OR: [4,5,6])
        In more complex targeting setups, you cannot guarantee that
        this function will output what you actually want.

        @return: list(ObjectModel), list(ObjectModel)
        """
        # Get set of all targeting objects
        all_targets = set(self.flatten())
        # Get set of all included objects
        includes = set(self._get_includes())
        # Get the items from all_targets which are not in includes
        excludes = all_targets - includes
        return list(includes), list(excludes)


class TargetingData(ObjectModel):
    """
    Abstract Class for line item targeting information
    Targeting indicates which kinds of users get served
    and ad impression or which part of a hosts site to
    serve an ad to
    """

    def __init__(self,
                 inventory=None,
                 geography=None,
                 day_part=None,
                 user_domain=None,
                 technology=None,
                 video_content=None,
                 video_position=None,
                 custom=None):
        self.inventory = inventory
        self.geography = geography
        self.day_part = day_part
        self.user_domain = user_domain
        self.technology = technology
        self.video_content = video_content
        self.video_position = video_position
        self.custom = custom

    def to_doc(self):
        """
        Serialize this object into a dictionary

        @return: dict
        """
        doc = {}
        for _key, _value in vars(self).items():
            if isinstance(_value, TargetingCriterion):
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
        params = {}
        for _key, _value in doc.items():
            if _key == '_metadata':
                continue
            elif _value:
                params[_key] = TargetingCriterion.from_doc(_value)

        return cls(**params)
