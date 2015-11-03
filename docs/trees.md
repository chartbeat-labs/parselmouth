#Parselmouth NodeTree
## Summary

DFP also supports ad unit hierarchies governed by complex tree
structures.  For example a site might have an ad unit (or zone)
called Sports with child ad units called Sports/Hockey and
Sports/Baseball.  Both of these ad units share a parent ad unit
called Sports and are sibblings in this tree structure.
Parselmouth also supports functions which help in working with
these tree structures using objects called NodeTrees.

```python
>>> from parselmouth.constants import ParselmouthTargetTypes
>>> adunit_tree = client.construct_tree(ParselmouthTargetTypes.adunit)
>>> sports_tree = adunit_tree.get_subtree('name', 'Sports')
```


## NodeTree Attributes

Each NodeTree object stores information about the given node
which is of type AdUnit in this case, because we build of tree
of that type.

```python
>>> sports_tree.node
AdUnit({'external_name': None, 'name': 'Sports', 'include_descendants': True, 'parent_id': 'SITE_ID', 'external_id': None, 'id': 'SPORTS_ID'})
```

The depth of this item is also stored.  This is an integer that
indicates how far this AdUnit is from the site parent node.

```python
>>> site_tree = adunit_tree.get_subtree('id', 'SITE_ID')
>>> site_tree.depth
0
>>> sports_tree.depth
1
```

You can also access all children of the sports ad unit,
which are stored as a list of NodeTree objects.

```python
>>> for sub_unit in sports_tree.children:
...     print sub_unit.node.depth
...
2
2
```


##NodeTree Functions

The NodeTree class comes equiped with a number of useful functions.
get_subtree allows you to grab the tree whose parent is given by
the inputs.

```
>>> sports_tree = adunit_tree.get_subtree('name', 'Sports')
>>> sports_tree = adunit_tree.get_subtree('id', 'SPORTS_ID')
>>> hockey_tree = adunit_tree.get_subtree('name', 'Sports/Hockey')
>>> hockey_tree = sports_tree.get_subtree('name', 'Sports/Hockey')
```

flatten allows you to get an entire list of all objects stored within
a given tree.  Note that this function returns a list of AdUnit objects
and includes the parent AdUnit in the list.

```python
>>> sports_adunits = sports_tree.flatten()
>>> for sub_adunit in sports_adunits:
...    print sub_adunit.name
...
'Sports'
'Sports/Hockey'
'Sports/Baseball'
```

get_max_depth gives you the maximum depth value that appears in
the given tree.

```python
>>> sports_tree.get_max_depth()
2
```
