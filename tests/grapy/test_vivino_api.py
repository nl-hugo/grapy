import unittest
from decimal import Decimal

from grapy.vivino_api import VivinoApi


class TestVivinoApi(unittest.TestCase):

    def setUp(self):
        self.vivino = VivinoApi()

    def test_countries(self):
        res = self.vivino.get_countries()
        self.assertGreater(len(res), 250)  # at least 250 countries

        item = next((item for item in res if item["code"] == "nl"), None)
        expected = {"code": "nl", "name": "Netherlands"}
        self.assertEqual(expected, item)

    def test_regions(self):
        res = self.vivino.get_regions()
        self.assertGreater(len(res), 3600)  # at least 3600 regions

        item = next((item for item in res if item["id"] == 933), None)
        expected = {"id": 933, "name": "Valencia", "country": "es"}
        self.assertEqual(expected, item)

    def test_wine_types(self):
        res = self.vivino.get_wine_types()
        self.assertEqual(len(res), 7)  # currently 7 styles

        item = next((item for item in res if item["id"] == 1), None)
        expected = {"id": 1, "name": "Red Wine"}
        self.assertEqual(expected, item)

    def test_wine_styles(self):
        res = self.vivino.get_wine_styles()
        self.assertGreater(len(res), 300)  # at least 300 styles

        item = next((item for item in res if item["id"] == 1), None)
        expected = {"id": 1, "name": "Spanish Albariño", "regional_name": "Spanish", "varietal_name": "Albariño"}
        self.assertEqual(expected, item)

    def test_grapes(self):
        res = self.vivino.get_grapes()
        self.assertGreater(len(res), 1550)  # at least 1550 grapes

        item = next((item for item in res if item["id"] == 1), None)
        expected = {
            "id": 1, "name": "Shiraz/Syrah", "acidity": 2, "body": 5, "color": 5,
            "flavor_profile": "Black pepper, plum, dark chocolate, full color and tannins"
        }
        self.assertEqual(expected, item)

    def test_vintage(self):
        res = self.vivino.get_vintage(156109791)
        expected = {
            "id": 156109791,
            "name": "Corette Viognier 2018",
            "statistics.ratings_average": Decimal("3.8"),
            "statistics.ratings_count": 142,
            "wine.id": 2423268,
            "year": "2018"
        }
        self.assertEqual(156109791, res.get("id"))
        self.assertEqual("Corette Viognier 2018", res.get("name"))
        self.assertEqual(2423268, res.get("wine.id"))
        self.assertEqual("2018", res.get("year"))
        self.assertEqual(Decimal, type(res.get("statistics.ratings_average")))
        self.assertEqual(int, type(res.get("statistics.ratings_count")))

    def test_winery(self):
        res = self.vivino.get_winery(15597)
        expected = {
            "id": 15597,
            "location": {
                "latitude": Decimal("43.591236"),
                "longitude": Decimal("3.258363")
            },
            "name": "Corette",
            "region.id": 3003,
            "website": ""
        }
        self.assertEqual(expected, res)


if __name__ == "__main__":
    unittest.main()
