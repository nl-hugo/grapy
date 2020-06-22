import json
import unittest
from time import sleep

from scrapy.exceptions import DropItem

from vendors import pipelines, items


class TestWineVendorsPipeline(unittest.TestCase):

    def setUp(self):
        self.pipeline = pipelines.WineVendorsPipeline()

        with open('data/wine.json', 'r') as f:
            data = json.load(f)
            self.wine = items.VendorWine(data)
            self.pipeline.create_item(self.wine)

    def tearDown(self):
        self.pipeline.delete_item(self.wine)

    def test_get_item(self):
        """ get an item """
        response = self.pipeline.get_item(self.wine)
        self.assertEqual(self.wine.get('url'), response.get('pk'))
        self.assertEqual('VENDORWINE', response.get('sk'))

    def test_delete_item(self):
        """ delete an item """
        response = self.pipeline.delete_item(self.wine)
        self.assertEqual(self.wine.get('url'), response.get('pk'))
        self.assertEqual('VENDORWINE', response.get('sk'))
        self.assertIsNone(self.pipeline.get_item(self.wine))

    def test_update_item(self):
        """ create an item that does not exist """
        # update the item
        self.wine['vendor'] = 'new vendor'
        self.wine['price'] = 5.95
        self.wine['volume'] = 1.5
        self.wine['winery'] = 'do not change me!'
        self.wine['name'] = 'do not change me!'
        self.wine['year'] = 'do not change me!'

        # wait for a bit to check timestamps
        sleep(3)
        response = self.pipeline.update_item(self.wine)

        # vendor, price and volume must updated
        self.assertEqual(self.wine.get('vendor'), response.get('vendor'))
        self.assertEqual(self.wine.get('price'), float(response.get('price')))
        self.assertEqual(self.wine.get('volume'), float(response.get('volume')))

        # winery, name and year must not be updated
        self.assertNotEqual(self.wine.get('winery'), response.get('winery'))
        self.assertNotEqual(self.wine.get('name'), response.get('name'))
        self.assertNotEqual(self.wine.get('year'), response.get('pk'))

        # lastSeen must be updated
        self.assertLess(response.get('firstSeen'), response.get('lastSeen'))

    def test_process_new_item(self):
        """ """
        wine = self.wine.copy()
        wine['url'] = 'test url'

        response = self.pipeline.process_item(wine, None)
        self.assertEqual(wine.get('url'), response.get('pk'))
        self.pipeline.delete_item(wine)

    def test_process_invalid_item(self):
        """ """
        self.pipeline.delete_item(self.wine)
        wine = self.wine.copy()
        del wine['name']
        with self.assertRaises(DropItem):
            self.pipeline.process_item(wine, None)
        self.assertIsNone(self.pipeline.get_item(wine))

    def test_process_item_price(self):
        """ """
        # wait for a bit to check timestamps
        sleep(3)
        self.wine['price'] = 3.95

        response = self.pipeline.process_item(self.wine, None)
        self.assertEqual(self.wine.get('url'), response.get('pk'))
        self.assertEqual(self.wine.get('price'), float(response.get('price')))
        self.assertLess(response.get('firstSeen'), response.get('lastSeen'))

    def test_process_item_name(self):
        """ """
        # delete the original item and replace it with modified one
        self.pipeline.delete_item(self.wine)
        with open('data/wine_ddb.json', 'r') as f:
            data = json.load(f)
            self.pipeline.table.put_item(Item=data)

        response = self.pipeline.get_item(self.wine)
        self.assertEqual(data.get('data'), response.get('data'))
        self.wine['name'] = 'new name'

        response = self.pipeline.process_item(self.wine, None)
        self.assertEqual(self.wine.get('url'), response.get('pk'))
        self.assertEqual(self.wine.get('name'), response.get('name'))
        self.assertEqual('vintages#', response.get('data'))
        self.assertLess(response.get('firstSeen'), response.get('lastSeen'))


if __name__ == '__main__':
    unittest.main()
