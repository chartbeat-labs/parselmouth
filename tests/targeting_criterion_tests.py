import unittest

from parseltongue.targeting import TargetingCriterion
from parseltongue.targeting import AdUnit
from parseltongue.exceptions import ParseltongueException


ADUNIT1 = AdUnit(
    id='1',
    name='home',
)

ADUNIT2 = AdUnit(
    id='2',
    name='page',
)

ADUNIT3 = AdUnit(
    id='3',
    name='hockey',
)

ADUNIT4 = AdUnit(
    id='4',
    name='baseball',
)

CRITERION1 = TargetingCriterion(
    [ADUNIT1], TargetingCriterion.OPERATOR.OR,
)

CRITERION2 = TargetingCriterion(
    [ADUNIT2], TargetingCriterion.OPERATOR.OR,
)

CRITERION3 = TargetingCriterion(
    [ADUNIT1, ADUNIT2], TargetingCriterion.OPERATOR.OR,
)

CRITERION4 = TargetingCriterion(
    [ADUNIT1, ADUNIT2], TargetingCriterion.OPERATOR.AND,
)

CRITERION5 = TargetingCriterion(
    [ADUNIT3, ADUNIT4], TargetingCriterion.OPERATOR.OR,
)


class TargetingCriterionTest(unittest.TestCase):

    def test_get_data(self):
        answer_targets = []
        answer_op = TargetingCriterion.OPERATOR.OR

        criterion = TargetingCriterion(
            answer_targets, answer_op,
        )
        test_op, test_targets = criterion.get_data()

        self.assertEqual(answer_targets, test_targets)
        self.assertEqual(answer_op, test_op)

        answer_targets = [ADUNIT1, ADUNIT2]
        answer_op = TargetingCriterion.OPERATOR.AND

        criterion = TargetingCriterion(
            answer_targets, answer_op,
        )
        test_op, test_targets = criterion.get_data()

        self.assertEqual(answer_targets, test_targets)
        self.assertEqual(answer_op, test_op)

    def test_flatten(self):
        answer_targets = []
        answer_op = TargetingCriterion.OPERATOR.OR

        criterion = TargetingCriterion(
            answer_targets, answer_op,
        )
        test_flatten = criterion.flatten()
        answer_flatten = []

        self.assertEqual(answer_flatten, test_flatten)

        criterion = TargetingCriterion(
            [CRITERION1, CRITERION2],
            TargetingCriterion.OPERATOR.NOT,
        )

        test_flatten = criterion.flatten()
        answer_flatten = [ADUNIT1, ADUNIT2]

        self.assertEqual(answer_flatten, test_flatten)

    def test_get_includes_and_excludes(self):
        criterion = CRITERION3 & (~CRITERION5)
        test_includes, test_excludes = criterion.get_includes_and_excludes()
        answer_includes = [ADUNIT1, ADUNIT2]
        answer_excludes = [ADUNIT3, ADUNIT4]

        self.assertEqual(sorted(test_includes), sorted(answer_includes))
        self.assertEqual(sorted(test_excludes), sorted(answer_excludes))

        criterion = CRITERION1 & CRITERION2 & CRITERION5
        test_includes, test_excludes = criterion.get_includes_and_excludes()
        answer_includes = [ADUNIT1, ADUNIT2, ADUNIT3, ADUNIT4]
        answer_excludes = []

        self.assertEqual(sorted(test_includes), sorted(answer_includes))
        self.assertEqual(sorted(test_excludes), sorted(answer_excludes))

        criterion = ~CRITERION1 & ~CRITERION2 & ~CRITERION5
        test_includes, test_excludes = criterion.get_includes_and_excludes()
        answer_includes = []
        answer_excludes = [ADUNIT1, ADUNIT2, ADUNIT3, ADUNIT4]

        self.assertEqual(sorted(test_includes), sorted(answer_includes))
        self.assertEqual(sorted(test_excludes), sorted(answer_excludes))

        criterion = ~CRITERION1 & ~CRITERION2 & CRITERION5
        test_includes, test_excludes = criterion.get_includes_and_excludes()
        answer_includes = [ADUNIT3, ADUNIT4]
        answer_excludes = [ADUNIT1, ADUNIT2]

        self.assertEqual(sorted(test_includes), sorted(answer_includes))
        self.assertEqual(sorted(test_excludes), sorted(answer_excludes))

    def test_operators(self):
        test_criterion = CRITERION1 & CRITERION2
        answer_criterion = CRITERION4
        self.assertEqual(test_criterion, answer_criterion)

        test_criterion = CRITERION1 | CRITERION2
        answer_criterion = CRITERION3
        self.assertEqual(test_criterion, answer_criterion)

        test_criterion = CRITERION1 | CRITERION3
        test_op, test_targets = test_criterion.get_data()
        answer_op = TargetingCriterion.OPERATOR.OR
        answer_targets = [ADUNIT1, ADUNIT1, ADUNIT2]
        self.assertEqual(test_op, answer_op)
        self.assertEqual(test_targets, answer_targets)

        test_criterion = CRITERION1 & CRITERION3
        test_op, test_targets = test_criterion.get_data()
        answer_op = TargetingCriterion.OPERATOR.AND
        answer_targets = [CRITERION1, CRITERION3]
        self.assertEqual(test_op, answer_op)
        self.assertEqual(test_targets, answer_targets)

        test_criterion = CRITERION1 & CRITERION4
        test_op, test_targets = test_criterion.get_data()
        answer_op = TargetingCriterion.OPERATOR.AND
        answer_targets = [ADUNIT1, ADUNIT1, ADUNIT2]
        self.assertEqual(test_op, answer_op)
        self.assertEqual(test_targets, answer_targets)

    def test_remove_target(self):
        test_criterion = CRITERION4.remove_target(CRITERION1)
        answer_criterion = CRITERION2
        self.assertEqual(test_criterion, answer_criterion)

        test_criterion = CRITERION4.remove_target(CRITERION2)
        answer_criterion = CRITERION1
        self.assertEqual(test_criterion, answer_criterion)

        test_criterion = (CRITERION1 & CRITERION5).remove_target(CRITERION1)
        answer_criterion = CRITERION5
        self.assertEqual(test_criterion, answer_criterion)

        test_criterion = CRITERION1.remove_target(CRITERION1)
        answer_criterion = None
        self.assertEqual(test_criterion, answer_criterion)

        test_criterion = CRITERION3.remove_target(CRITERION3)
        answer_criterion = None
        self.assertEqual(test_criterion, answer_criterion)

        self.assertRaises(ParseltongueException, CRITERION3.remove_target, CRITERION2)

        self.assertRaises(ParseltongueException, CRITERION5.remove_target, CRITERION4)

        self.assertRaises(ParseltongueException, (CRITERION1 & CRITERION5).remove_target, CRITERION5)

    def test_to_doc(self):
        # Test to doc
        test_doc = CRITERION1.to_doc()
        answer_doc = {
            '_metadata': {u'cls': 'TargetingCriterion'},
            'OR': [
                {
                    '_metadata': {u'cls': 'AdUnit'},
                    'chartbeat_id': None,
                    'external_id': None,
                    'id': '1',
                    'include_descendants': True,
                    'name': 'home',
                    'parent_id': None,
                }
            ],
        }
        self.assertEqual(test_doc, answer_doc)

        # test from doc
        self.assertEqual(
            CRITERION1,
            TargetingCriterion.from_doc(answer_doc),
        )

        # test to doc/from doc inversions
        self.assertEqual(
            CRITERION1,
            TargetingCriterion.from_doc(CRITERION1.to_doc()),
        )

        self.assertEqual(
            CRITERION2,
            TargetingCriterion.from_doc(CRITERION2.to_doc()),
        )

        self.assertEqual(
            CRITERION3,
            TargetingCriterion.from_doc(CRITERION3.to_doc()),
        )

        self.assertEqual(
            CRITERION4,
            TargetingCriterion.from_doc(CRITERION4.to_doc()),
        )

if __name__ == "__main__":
    unittest.main()
