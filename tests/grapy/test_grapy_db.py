import json
import os
import unittest
from decimal import Decimal
from unittest.mock import patch

from grapy.grapy_db import GrapyDDB
from grapy.load import build_adjacency_lists


def fixture_vendorwine():
    return json.dumps({
        "vendor": {
            "name": "TestVendor",
            "url": "www.vivino.com"
        },
        "url": "https://www.vivino.com/catena-alta-malbec/w/1870",
        "winery": "Catena Alta",
        "name": "Malbec",
        "year": "U.V.",
        "price": 31.95,
        "volume": 0.75
    })


def fixture_vintage():
    return json.dumps({
        "id": 1469245,
        "name": "Catena Alta Malbec",
        "wine.id": 1870,
        "year": "",
        "statistics.ratings_count": 23080,
        "statistics.ratings_average": 4.2
    })


def fixture_winery():
    return json.dumps({
        "id": 243350,
        "name": "Catena Alta",
        "region.id": 454,
        "website": "http://www.catenawines.com/catena-alta-wines.php",
        "location": None
    })


def fixture_countries():
    return json.dumps([
        {"code": "x1", "name": "country1"}, {"code": "x2", "name": "country2"}, {"code": "x3", "name": "country3"}]
    )


class TestGrapyDdb(unittest.TestCase):

    @patch.dict(os.environ, {"DYNAMODB_TABLE": "grapy-dev"})
    def setUp(self):
        self.db = GrapyDDB()

    def test_build_row(self):
        pass

    def test_set_vintage(self):
        data = json.loads(fixture_vendorwine(), parse_float=Decimal)
        self.db.add_vendor_wine(data)

        self.db.set_vintage(f"vendorwines#{data.get('url')}", 1469245)
        res = self.db.get_item("pk", f"vendorwines#{data.get('url')}", "sk", "VENDORWINES").get("Item")
        self.assertEqual("vintages#1469245", res.get("data"))
        self.db.delete_item("pk", f"vendorwines#{data.get('url')}", "sk", "VENDORWINES")

    def test_add_vendor_wine(self):
        data = json.loads(fixture_vendorwine(), parse_float=Decimal)
        self.db.add_vendor_wine(data)

        res = self.db.get_item("pk", f"vendorwines#{data.get('url')}", "sk", "VENDORWINES").get("Item")
        self.assertEqual("U.V.", res.get("year"))
        self.assertEqual("vintages#", res.get("data"))
        self.assertIsNotNone(res.get("last_updated_at"))
        self.db.delete_item("pk", f"vendorwines#{data.get('url')}", "sk", "VENDORWINES")

    def test_add_wine(self):
        item = {"id": 1, "name": "test", "winery.id": 1}
        self.db.add_wine(item)

        res = self.db.get_item("pk", "wines#1", "sk", "WINES").get("Item")
        self.assertEqual("wineries#1", res.get("data"))
        self.assertEqual("test", res.get("name"))
        self.assertIsNotNone(res.get("last_updated_at"))
        self.db.delete_item("pk", "wines#1", "sk", "WINES")

    def test_add_winery(self):
        data = json.loads(fixture_winery(), parse_float=Decimal)
        self.db.add_winery(data)

        res = self.db.get_item("pk", "wineries#243350", "sk", "WINERIES").get("Item")
        self.assertEqual("Catena Alta", res.get("name"))
        self.assertEqual("regions#454", res.get("data"))
        self.assertIsNone(res.get("location"))
        self.assertIsNotNone(res.get("last_updated_at"))
        self.db.delete_item("pk", "wineries#243350", "sk", "WINERIES")

    def test_add_vintage(self):
        data = json.loads(fixture_vintage(), parse_float=Decimal)
        self.db.add_vintage(data)

        res = self.db.get_item("pk", "vintages#1469245", "sk", "VINTAGES").get("Item")
        self.assertEqual(Decimal("4.2"), res.get("statistics.ratings_average"))
        self.assertEqual("Catena Alta Malbec", res.get("name"))
        self.assertEqual("wines#1870", res.get("data"))
        self.assertEqual("", res.get("year"))
        self.assertIsNotNone(res.get("last_updated_at"))
        self.db.delete_item("pk", "vintages#1469245", "sk", "VINTAGES")

    def test_get_unknown_vintage(self):
        pass

    def test_get_all(self):
        data = json.loads(fixture_countries())
        table_data = build_adjacency_lists(data, [], [], [], [])
        self.db.load_dynamo_data(table_data)

        res = self.db.get_all("countries", None, 1)
        items = res.get("Items")
        self.assertEqual(1, len(items))
        self.assertEqual(1, res.get("Count"))

        # get next page
        next_key = res.get("LastEvaluatedKey")
        self.assertEqual(items[0].get("pk"), next_key.get("pk"))

        res2 = self.db.get_all("countries", next_key, 2)
        self.assertEqual(2, len(res2.get("Items")))
        self.assertEqual(2, res2.get("Count"))

    def test_update_price(self):
        data = json.loads(fixture_vendorwine(), parse_float=Decimal)
        self.db.add_vendor_wine(data)
        self.db.set_vintage(f"vendorwines#{data.get('url')}", 1469245)

        # update price, vintage should be unchanged
        data["price"] = 10
        self.db.add_vendor_wine(data)
        res = self.db.get_item("pk", f"vendorwines#{data.get('url')}", "sk", "VENDORWINES").get("Item")
        self.assertEqual(Decimal("10"), res.get("price"))
        self.assertEqual("vintages#1469245", res.get("data"))
        self.db.delete_item("pk", f"vendorwines#{data.get('url')}", "sk", "VENDORWINES")

    def test_update_volume(self):
        data = json.loads(fixture_vendorwine(), parse_float=Decimal)
        self.db.add_vendor_wine(data)
        self.db.set_vintage(f"vendorwines#{data.get('url')}", 1469245)

        # update volume, vintage should be unchanged
        data["volume"] = Decimal("1.5")
        self.db.add_vendor_wine(data)
        res = self.db.get_item("pk", f"vendorwines#{data.get('url')}", "sk", "VENDORWINES").get("Item")
        self.assertEqual(Decimal("1.5"), res.get("volume"))
        self.assertEqual("vintages#1469245", res.get("data"))
        self.db.delete_item("pk", f"vendorwines#{data.get('url')}", "sk", "VENDORWINES")

    def test_update_name(self):
        data = json.loads(fixture_vendorwine(), parse_float=Decimal)
        self.db.add_vendor_wine(data)
        self.db.set_vintage(data.get("url"), 1469245)

        # update name, vintage should be reset to vintage#
        data["name"] = "new name"
        self.db.add_vendor_wine(data)
        res = self.db.get_item("pk", f"vendorwines#{data.get('url')}", "sk", "VENDORWINES").get("Item")
        self.assertEqual("new name", res.get("name"))
        self.assertEqual("vintages#", res.get("data"))
        self.db.delete_item("pk", f"vendorwines#{data.get('url')}", "sk", "VENDORWINES")

    def test_update_winery(self):
        data = json.loads(fixture_vendorwine(), parse_float=Decimal)
        self.db.add_vendor_wine(data)
        self.db.set_vintage(data.get("url"), 1469245)

        # update winery, vintage should be reset to vintage#
        data["winery"] = "new name"
        self.db.add_vendor_wine(data)
        res = self.db.get_item("pk", f"vendorwines#{data.get('url')}", "sk", "VENDORWINES").get("Item")
        self.assertEqual("new name", res.get("winery"))
        self.assertEqual("vintages#", res.get("data"))
        self.db.delete_item("pk", f"vendorwines#{data.get('url')}", "sk", "VENDORWINES")

    def test_update_year(self):
        data = json.loads(fixture_vendorwine(), parse_float=Decimal)
        self.db.add_vendor_wine(data)
        self.db.set_vintage(f"vendorwines#{data.get('url')}", 1469245)

        # update year, vintage should be reset to vintage#
        data["year"] = "2019"
        self.db.add_vendor_wine(data)
        res = self.db.get_item("pk", f"vendorwines#{data.get('url')}", "sk", "VENDORWINES").get("Item")
        self.assertEqual("2019", res.get("year"))
        self.assertEqual("vintages#", res.get("data"))
        self.db.delete_item("pk", f"vendorwines#{data.get('url')}", "sk", "VENDORWINES")


if __name__ == "__main__":
    unittest.main()
