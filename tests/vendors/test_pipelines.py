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


class TestWineVendorsPipeline(unittest.TestCase):

    def setUp(self):
        self.pipeline = pipelines.WineVendorsPipeline("http://www.example.com", "key", [], [.75])
        self.pipeline.open_spider(None)

        data = json.loads(fixture_wine())
        self.wine = items.VendorWine(data)

    def test_process_item(self):
        """ """
        response = self.pipeline.process_item(self.wine, None)
        self.assertEqual(self.wine, response)

    def test_process_invalid_item(self):
        """ """
        del self.wine["name"]
        with self.assertRaises(DropItem):
            self.pipeline.process_item(self.wine, None)


if __name__ == "__main__":
    unittest.main()
