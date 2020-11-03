import unittest

from grapy.vivino_search import VivinoSearch


class TestVivinoSearch(unittest.TestCase):
    """ env variables ALGOLIA_APP_ID, ALGOLIA_API_KEY and ALGOLIA_INDEX must be set in .env """
    def setUp(self):
        self.vivino = VivinoSearch()

    def test_search(self):
        res = self.vivino.search("Corette Viognier", "2018")
        self.assertEqual(2423268, res.get("id"))
        self.assertEqual("Viognier", res.get("name"))
        self.assertEqual("2018", res.get("vintages").get("year"))

    def test_no_vintage(self):
        res = self.vivino.search("Corette Viognier", )
        self.assertEqual(2423268, res.get("id"))
        self.assertEqual("U.V.", res.get("vintages").get("year"))

    def test_vintage_does_not_exist(self):
        res = self.vivino.search("Corette Viognier", "9999")
        self.assertEqual(2423268, res.get("id"))
        self.assertEqual("U.V.", res.get("vintages").get("year"))


if __name__ == "__main__":
    unittest.main()
