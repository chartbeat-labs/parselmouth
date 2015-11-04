#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Parselmouth - Tree Builder

Ad providers such as DFP employ complex tree structures to organize
zones or adunits within their system.  The TreeBuilder class helps
build and manipulate collections of objects with these tree structures.
"""

# Future-proof
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

# Standard Library Imports
from collections import defaultdict

# Parselmouth Imports
from parselmouth.constants import ParselmouthTargetTypes
from parselmouth.targeting import AdUnit
from parselmouth.targeting import Custom
from parselmouth.targeting import Geography


class NodeTree(object):
    """
    Class which represents a tree of ObjectModels
    """
    def __init__(self, node, children, depth=None):
        self.node = node
        self.children = children
        self.depth = depth

    def __ne__(self, other):
        return not(self == other)

    def __eq__(self, other):
        if self.node != other.node or self.depth != other.depth:
            return False

        if len(self.children) != len(other.children):
            return False

        for child in self.children:
            matching_child = [c for c in other.children if c == child]
            if not matching_child:
                return False

        return True

    def to_doc(self):
        return {
            'node': self.node.to_doc() if self.node else None,
            'children': [c.to_doc() for c in self.children],
            'depth': self.depth,
        }

    def get_subtree(self, field_name, field_value):
        """
        Find a subtree within a list of NodeTrees with the field value given

        @param field_name: ParselmouthFields
        @param field_value: str
        @return: NodeTree
        """
        subtree = None
        if self.children:
            for branch in self.children:
                _node = branch.node
                if _node and vars(_node).get(field_name) == field_value:
                    subtree = branch
                elif branch.children:
                    subtree = branch.get_subtree(
                        field_name,
                        field_value,
                    )

                if subtree:
                    return subtree

        return subtree

    def get_subtree_parents(self, field_name, field_value):
        """
        Get the node associated to the given field_name/field_value,
        then return a list of all parent nodes for this node
        =
        @param field_name: ParselmouthFields
        @param field_values: str
        @return: list(ObjectModel)
        """
        parent_nodes = []
        if self.node and self.get_subtree(field_name, field_value):
            parent_nodes.append(self.node)

        if self.children:
            for branch in self.children:
                parent_nodes += branch.get_subtree_parents(field_name, field_value)

        return parent_nodes

    def get_max_depth(self):
        """
        Get the maximum depth of any node within the tree

        @return: int|None
        """
        max_depth = self.depth

        if self.children:
            for branch in self.children:
                max_depth = max([max_depth, branch.get_max_depth()])

        return max_depth

    def flatten(self, depth=None, only_leaves=False):
        """
        Get a flat list of all descendants from a subtree.
        If depth is given, give only nodes at the given depth

        @param depth: int|None
        @param only_leaves: bool, only return maximal depth nodes
        @return: list(ObjectModel)
        """
        if only_leaves:
            assert depth is None

        descendants = []
        if self.node and \
            (depth is None or self.depth == depth) and \
            (only_leaves is False or len(self.children) == 0):
            descendants.append(self.node)

        if self.children:
            for branch in self.children:
                if branch.children:
                    descendants += branch.flatten(
                        depth=depth,
                        only_leaves=only_leaves,
                    )
                elif branch.node and (depth is None or branch.depth == depth):
                    descendants.append(branch.node)

        return descendants

    def filter_tree_by_key(self, key, filter_ids):
        """
        Filter a given tree to include branches that are either
        included in the set of filter_ids or at least of of its
        children are in the set of filter_ids

        @param key: ParselmouthField, key to filter on
        @param filter_ids: set(str)
        @return: NodeTree
        """
        if isinstance(filter_ids, list):
            filter_set = set(filter_ids)
        else:
            filter_set = filter_ids

        assert isinstance(filter_set, set)

        filtered_children = []
        for branch in self.children:
            _descendants = branch.flatten()
            _descendant_ids = set([vars(d)[key] for d in _descendants])

            # if some descendant of this branch is in filter_ids
            # keep this branch and update its children
            if filter_set.intersection(_descendant_ids):
                new_branch = branch.filter_tree_by_key(
                    key, filter_set,
                )
                if new_branch:
                    filtered_children.append(new_branch)

        return NodeTree(self.node, filtered_children, self.depth)

    def filter_tree(self, filter_ids):
        """
        Filter a given tree to include branches that are either
        included in the set of filter_ids or at least of of its
        children are in the set of filter_ids

        @param tree: list(dict)
        @param filter_ids: set(str)
        @return: NodeTree
        """
        return self.filter_tree_by_key('external_name', filter_ids)

    def update_external_names(self, id_map):
        """
        Set external names of nodes in given tree to new values
        given by the dictionary id_map: id field --> external_name field.
        NOTE: This edits the nodes of this tree in place

        @param id_map: dict
        """
        current_node = self.node
        if current_node:
            _external_name = id_map.get(current_node.id)
            if _external_name:
                current_node.external_name = _external_name

        for branch in self.children:
            branch.update_external_names(id_map)


class TreeBuilder(object):
    """
    Interface from building ad provider data into trees

    Subject include:
        * Demographic data
        * Geographic data
        * Ad Placement data
    """

    TARGET_CLASS_MAP = {
        ParselmouthTargetTypes.adunit: AdUnit,
        ParselmouthTargetTypes.geography: Geography,
        ParselmouthTargetTypes.demographics: Custom,
        ParselmouthTargetTypes.ad_position: Custom,
        ParselmouthTargetTypes.custom: Custom,
    }
    """
    dict, associate to each target_type the appropriate targeting class
    """

    INTERFACE_FUNCTION_MAP = {
        ParselmouthTargetTypes.adunit: lambda i: i.get_adunit_targets(),
        ParselmouthTargetTypes.geography: lambda i: i.get_geography_targets(),
        ParselmouthTargetTypes.demographics: lambda i: i.get_custom_targets(),
        ParselmouthTargetTypes.ad_position: lambda i: i.get_custom_targets(),
        ParselmouthTargetTypes.custom: lambda i: i.get_custom_targets(),
    }
    """
    dict, associate to each target_type the interface target getter function
    """

    def __init__(self, provider_name, interface=None):
        """
        Constructor

        @param domain: str
        @param provider_name: ParselmouthProviders
        @param interface: Interface for provider
        """
        self.provider_name = provider_name
        self.interface = interface

    def _recursive_make_tree(self, pid, parents, node_map, depth=0):
        """
        Recursively construct tree by creating a nested dictionary
        based off of data from parents that gives a parent child
        relationship

        @param pid: parent id
        @param parents: dict, the keys are parent ids, and values
            are all of the children of that id
        @param node_map: dict, node documents associated with each id
        @param depth: int, recursive handle on node depth in a tree
        @return: list(dict)
        """

        trees = []
        for child in parents.get(pid, []):
            _id = child.id
            node = node_map.get(_id)
            tree = NodeTree(
                node,
                children=self._recursive_make_tree(
                    _id, parents, node_map, depth + 1
                ),
                depth=depth,
            )
            trees.append(tree)

        return trees

    def build_tree(self, nodes):
        """
        Interface for translating a flat data structure into a native
        hierarchical type.

        @param nodes: list(TargetingModel) with id and parent_id fields
        @return: NodeTree
        """
        node_map = {}
        # Create flat list of all parents and their immediate children
        parents = defaultdict(list)
        for node in nodes:
            parents[node.parent_id].append(node)
            node_map[node.id] = node

        # Construct tree by building trees at each maximal parent
        maximal_trees = []
        for pid in parents.keys():
            # Determine if pid is a maximal parent
            # By checking to see if pid is a child of any other id
            maximal = True
            for children in parents.values():
                children_ids = [c.id for c in children]
                # If pid is a child of another id, then flag as not maximal
                if pid in children_ids:
                    maximal = False
                    break
            # Create tree starting at this maximal parent
            if maximal:
                max_node = node_map.get(pid)
                children = self._recursive_make_tree(
                    pid, parents, node_map,
                )

                if max_node:
                    tree = NodeTree(max_node, children)
                    maximal_trees.append(tree)
                else:
                    maximal_trees.extend(children)

        return NodeTree(
            node=None,
            children=maximal_trees,
        )

    def construct_tree(self, target_type):
        """
        Get all data of type target_type from ad provider,
        and build a tree

        @param taget_type: ParselmouthTargetTypes
        @return: NodeTree
        """
        assert target_type in ParselmouthTargetTypes
        assert self.interface
        nodes = self.INTERFACE_FUNCTION_MAP[target_type](self.interface)
        return self.build_tree(nodes)

    def _convert_node_tree_to_doc(self, tree):
        """
        Convert NodeTree into a dict that can be written to mongo

        @param tree: NodeTree
        @return: dict
        """
        return tree.to_doc()

    def _convert_doc_to_node_tree(self, doc, target_type):
        """
        Convert a mongo tree doc into a NodeTree Object

        @param doc: dict
        @param target_type: ParselmouthTargetTypes
        @return: NodeTree
        """
        _target_class = self.TARGET_CLASS_MAP[target_type]
        if doc['node']:
            node = _target_class.from_doc(doc['node'])
        else:
            node = None

        children = doc.get('children', [])
        depth = doc.get('depth')

        return NodeTree(
            node=node,
            children=[self._convert_doc_to_node_tree(c, target_type) for c in children],
            depth=depth,
        )
