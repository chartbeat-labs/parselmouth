import unittest

from parseltongue.utils.check import check_equal


class UtilsTest(unittest.TestCase):

    def test_check_equal_null(self):
        self.assertTrue(
           check_equal(0, 0),
        )

        self.assertFalse(
           check_equal(0, None),
        )

        self.assertFalse(
           check_equal(None, False),
        )

        self.assertTrue(
           check_equal(None, None),
        )

    def test_check_equal_dict(self):
        self.assertTrue(
           check_equal({'a': 0, 'b': 1}, {'b': 1, 'a': 0}),
        )

        self.assertFalse(
           check_equal({'a': 0, 'b': 1}, {'b': 0, 'a': 1}),
        )

    def test_check_equal_list(self):
        self.assertTrue(
           check_equal(['a', 'b', 0, 1, 2], [1, 2, 0, 'b', 'a']),
        )

        self.assertFalse(
           check_equal(['a', 'b', 0, 1, 2], [1, 2, 0, 'b']),
        )

        self.assertFalse(
           check_equal(['a', 'b', 0, 1, 2], [1, 2, 0, 'b', 'c']),
        )

        self.assertFalse(
           check_equal(['a', 'b', 0, 1, 2], [1, 4, 0, 'a', 'b']),
        )

    def test_check_equal_nested(self):
        self.assertTrue(
           check_equal(
                {'a': [None, 1, 2, {}], 'b': 1},
                {'b': 1, 'a': [1, 2, None, {}]},
            ),
        )

        self.assertFalse(
           check_equal(
                {'a': [None, 1, 2, {}], 'b': 1},
                {'b': 1, 'a': [1, 2, {}, {}]},
            ),
        )

        self.assertTrue(
           check_equal(
                [{'a': 1, 'b': True, 'c': ['a', 1]}, 1, 2],
                [2, 1, {'c': [1, 'a'], 'a': 1, 'b': True}],
            ),
        )

        self.assertFalse(
           check_equal(
                [{'a': 1, 'b': True, 'c': ['a', 1]}, 1, 2],
                [2, 1, {'c': [1, 'a'], 'a': 1, 'b': 1}],
            ),
        )


if __name__ == "__main__":
    unittest.main()
