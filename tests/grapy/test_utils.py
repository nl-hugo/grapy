import unittest

from grapy import utils


class TestUtils(unittest.TestCase):
    dct = {"parent": {"child": "ok"}}

    def test_safe_get_self(self):
        """
        :return:
        """
        res = utils.safe_get(self.dct, [])
        self.assertEqual(self.dct, res)

    def test_safe_get_no_key(self):
        """
        :return:
        """
        res = utils.safe_get(self.dct, ['fail'])
        self.assertEqual(None, res)

    def test_safe_get_parent(self):
        """
        :return:
        """
        res = utils.safe_get(self.dct, ['parent'])
        self.assertEqual({"child": "ok"}, res)

    def test_safe_get_child(self):
        """
        :return:
        """
        res = utils.safe_get(self.dct, ['parent', 'child'])
        self.assertEqual("ok", res)

    def test_safe_get_child_only(self):
        """
        :return:
        """
        res = utils.safe_get(self.dct, ['child'])
        self.assertEqual(None, res)

    def test_num_remaining(self):
        self.assertEqual(90, utils.num_remaining(100, 10))
        self.assertEqual(5, utils.num_remaining(15, 10))
        self.assertEqual(0, utils.num_remaining(5, 10))

    def test_num_updated(self):
        self.assertEqual(10, utils.num_updated(100, 10))
        self.assertEqual(10, utils.num_updated(15, 10))
        self.assertEqual(5, utils.num_updated(5, 10))


if __name__ == '__main__':
    unittest.main()
