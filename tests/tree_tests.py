import unittest

from parseltongue.constants import ParseltongueTargetTypes
from parseltongue.targeting import AdUnit
from parseltongue.tree_builder import NodeTree
from parseltongue.tree_builder import TreeBuilder


# Empty Node Tree
EMPTY_TREE = NodeTree(None, [])

# Make a nested sequence of adunits
HOMEPAGE = AdUnit(
    id='1',
    chartbeat_id='1',
    parent_id='',
    name='home',
)

HOMEPAGE_US = AdUnit(
    id='2',
    chartbeat_id='2',
    parent_id='1',
    name='home/us',
)

HOMEPAGE_US_MI = AdUnit(
    id='3',
    chartbeat_id='3',
    parent_id='2',
    name='home/us/mi',
)

NESTED_NODES = [
    HOMEPAGE,
    HOMEPAGE_US,
    HOMEPAGE_US_MI,
]

NESTED_TREE = NodeTree(
    None,
    [
        NodeTree(
            HOMEPAGE,
            [
                NodeTree(
                    HOMEPAGE_US,
                    [
                        NodeTree(
                        HOMEPAGE_US_MI,
                        [],
                        depth=2
                        ),
                    ],
                    depth=1,
                ),
            ],
            depth=0,
        ),
    ],
    None,
)


# Make parallel sequence of adunits
ENTERTAINMENT = AdUnit(
    id='1',
    chartbeat_id='1',
    parent_id='-1',
    name='entertainment',
)

SPORTS = AdUnit(
    id='2',
    chartbeat_id='2',
    parent_id='-2',
    name='sports',
)

NEWS = AdUnit(
    id='3',
    chartbeat_id='3',
    parent_id='-3',
    name='news',
)

DISJOINT_NODES = [
    ENTERTAINMENT,
    SPORTS,
    NEWS,
]

DISJOINT_TREE = NodeTree(
    None,
    [
        NodeTree(
            ENTERTAINMENT,
            [],
            depth=0,
        ),
        NodeTree(
            SPORTS,
            [],
            depth=0,
        ),
        NodeTree(
            NEWS,
            [],
            depth=0,
        ),
    ],
    None,
)


# Make another tree shape
HOMEPAGE_UK = AdUnit(
    id='3',
    chartbeat_id='3',
    parent_id='1',
    name='home/uk',
)

ANCESTOR_NODES = [
    HOMEPAGE,
    HOMEPAGE_US,
    HOMEPAGE_UK,
]

ANCESTOR_TREE = NodeTree(
    None,
    [
        NodeTree(
            HOMEPAGE,
            [
                NodeTree(
                    HOMEPAGE_US,
                    [],
                    depth=1,
                ),
                NodeTree(
                    HOMEPAGE_UK,
                    [],
                    depth=1,
                ),
            ],
            depth=0,
        ),
    ],
    None,
)


class TreeBuilderTest(unittest.TestCase):

    def setUp(self):
        self.tree_builder = TreeBuilder(None, None)

    def test_build_tree(self):
        # Test empty tree
        nodes1 = []
        test1 = self.tree_builder.build_tree(nodes1)

        self.assertEqual(test1, EMPTY_TREE)

        # Test basic nesting
        test2 = self.tree_builder.build_tree(NESTED_NODES)
        self.assertEqual(test2, NESTED_TREE)

        # Test disjoint branches
        test3 = self.tree_builder.build_tree(DISJOINT_NODES)
        self.assertEqual(test3, DISJOINT_TREE)

        # Test shared ancestor
        test3 = self.tree_builder.build_tree(ANCESTOR_NODES)
        self.assertEqual(test3, ANCESTOR_TREE)

    def test_doc_conversion(self):

        doc1 = self.tree_builder._convert_node_tree_to_doc(NESTED_TREE)
        test1 = self.tree_builder._convert_doc_to_node_tree(
            doc1, ParseltongueTargetTypes.adunit,
        )

        self.assertEqual(test1, NESTED_TREE)

        doc2 = self.tree_builder._convert_node_tree_to_doc(DISJOINT_TREE)
        test2 = self.tree_builder._convert_doc_to_node_tree(
            doc2, ParseltongueTargetTypes.adunit,
        )

        self.assertEqual(test2, DISJOINT_TREE)

        doc3 = self.tree_builder._convert_node_tree_to_doc(ANCESTOR_TREE)
        test3 = self.tree_builder._convert_doc_to_node_tree(
            doc3, ParseltongueTargetTypes.adunit,
        )

        self.assertEqual(test3, ANCESTOR_TREE)


class NodeTreeTest(unittest.TestCase):

    def test_get_subtree(self):
        # Test empty tree
        answer1 = None

        test1 = EMPTY_TREE.get_subtree(
            field_name='id',
            field_value='1',
        )

        self.assertEqual(test1, answer1)

        # Test missing id
        answer2 = None

        test2 = NESTED_TREE.get_subtree(
            field_name='id',
            field_value='1234',
        )

        self.assertEqual(test2, answer2)

        # Get middle tree
        answer3 = NodeTree(
            HOMEPAGE_US,
            [
                NodeTree(
                HOMEPAGE_US_MI,
                [],
                depth=2
                ),
            ],
            depth=1,
        )

        test3 = NESTED_TREE.get_subtree(
            field_name='id',
            field_value='2',
        )

        self.assertEqual(test3, answer3)

    def test_flatten(self):
        # Test empty tree
        answer1 = []
        test1 = EMPTY_TREE.flatten()
        self.assertEqual(test1, answer1)

        # Test nested tree
        answer2 = NESTED_NODES
        test2 = NESTED_TREE.flatten()
        self.assertEqual(test2, answer2)

        # Test disjoint tree
        answer3 = DISJOINT_NODES
        test3 = DISJOINT_TREE.flatten()
        self.assertEqual(test3, answer3)

        # Test ancestor tree
        answer4 = ANCESTOR_NODES
        test4 = ANCESTOR_TREE.flatten()
        self.assertEqual(test4, answer4)

        # Test depth = 0
        answer5 = [
            HOMEPAGE,
        ]
        test5 = NESTED_TREE.flatten(depth=0)
        self.assertEqual(test5, answer5)

        # Test depth = 1
        answer6 = [
            HOMEPAGE_US,
        ]
        test6 = NESTED_TREE.flatten(depth=1)
        self.assertEqual(test6, answer6)

        # Test depth = 2
        answer6 = [
            HOMEPAGE_US_MI,
        ]
        test6 = NESTED_TREE.flatten(depth=2)
        self.assertEqual(test6, answer6)

        # Test only_leaves = True
        answer7 = [
            HOMEPAGE_US_MI,
        ]
        test7 = NESTED_TREE.flatten(only_leaves=True)
        self.assertEqual(test7, answer7)

        # Test only_leave = True and depth=n
        with self.assertRaises(AssertionError):
            test8 = NESTED_TREE.flatten(depth=1, only_leaves=True)
            self.assertRaises(test8, AssertionError)

    def test_get_max_depth(self):
        # Test empty tree
        answer1 = None
        test1 = EMPTY_TREE.get_max_depth()
        self.assertEqual(test1, answer1)

        # Test nested tree
        answer2 = 2
        test2 = NESTED_TREE.get_max_depth()
        self.assertEqual(test2, answer2)

        # Test disjoint tree
        answer3 = 0
        test3 = DISJOINT_TREE.get_max_depth()
        self.assertEqual(test3, answer3)

        # Test ancestor tree
        answer4 = 1
        test4 = ANCESTOR_TREE.get_max_depth()
        self.assertEqual(test4, answer4)

    def test_filter_tree(self):

        answer1 = NESTED_TREE
        test1 = NESTED_TREE.filter_tree(
            set(["3"]),
        )
        self.assertEqual(test1, answer1)

        answer2 = NodeTree(
            None,
            [
                NodeTree(
                    HOMEPAGE,
                    [],
                    depth=0,
                ),
            ],
            None,
        )
        test2 = NESTED_TREE.filter_tree(
            set(["1"]),
        )
        self.assertEqual(test2, answer2)

        answer3 = NodeTree(
            None,
            [
                NodeTree(
                    ENTERTAINMENT,
                    [],
                    depth=0,
                ),
            ],
            None,
        )
        test3 = DISJOINT_TREE.filter_tree(
            set(["1"]),
        )
        self.assertEqual(test3, answer3)

        answer4 = NodeTree(
            None,
            [
                NodeTree(
                    HOMEPAGE,
                    [
                        NodeTree(
                            HOMEPAGE_US,
                            [],
                            depth=1,
                        ),
                    ],
                    depth=0,
                ),
            ],
            None,
        )
        test4 = ANCESTOR_TREE.filter_tree(
            set(["2"]),
        )
        self.assertEqual(test4, answer4)


if __name__ == "__main__":
    unittest.main()
