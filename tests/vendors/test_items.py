import json
import unittest

from scrapy.exceptions import DropItem

from vendors import pipelines, items


def fixture_wine():
    return json.dumps({
        "vendor": {
            "name": "TestVendor",
            "url": "www.vivino.com"
        },
        "url": "https://www.degoudenton.nl/corette-viognier",
        "winery": "Corette",
        "name": "Viognier",
        "year": "2018",
        "price": 8.95,
        "volume": 0.75
    })


class TestVendorWine(unittest.TestCase):

    def setUp(self):
        self.pipeline = pipelines.WineVendorsPipeline()
        data = json.loads(fixture_wine())
        self.wine = items.VendorWine(data)

    def test_item(self):
        """ validated items should be unmodified """
        item = self.wine.copy()
        self.wine.validate()
        self.assertEqual(item, self.wine)

    def test_item_unknown_field(self):
        """ items with an unknown field should raise a KeyError """
        with self.assertRaises(KeyError):
            self.wine["fail"] = "fails!"

    def test_item_missing_field(self):
        """ items with a missing field should be dropped """
        del self.wine["name"]
        with self.assertRaises(DropItem):
            self.wine.validate()

    def test_item_missing_winery(self):
        """ items with a winery missing field should NOT be dropped """
        self.wine["winery"] = ""
        self.wine.validate()
        self.assertEqual("", self.wine.get("winery"))

    def test_item_invalid_price(self):
        """ items with an invalid price should be dropped """
        self.wine["price"] = -1
        with self.assertRaises(DropItem):
            self.wine.validate()

    def test_item_invalid_vintage(self):
        """ items with an invalid vintage should be dropped """
        self.wine["year"] = "fail"
        with self.assertRaises(DropItem):
            self.wine.validate()

        self.wine["year"] = "9999"
        with self.assertRaises(DropItem):
            self.wine.validate()

    def test_item_invalid_volume(self):
        """ items with an invalid volume should be dropped """
        self.wine["volume"] = 0.69
        with self.assertRaises(DropItem):
            self.wine.validate()

    def test_item_forbidden_word(self):
        """ items with an forbidden word in their name should be dropped """
        self.wine["name"] = "Corette proefpakket"
        with self.assertRaises(DropItem):
            self.wine.validate()

    def test_item_no_vintage(self):
        """ items without a vintage should be modified to "U.V." """
        self.wine["year"] = ""
        self.wine.validate()
        self.assertEqual("U.V.", self.wine.get("year"))


if __name__ == "__main__":
    unittest.main()
