import os
import unittest
from unittest.mock import patch

from grapy.dynamo_db import DynamoDB


class TestDynamodb(unittest.TestCase):

    @patch.dict(os.environ, {"DYNAMODB_TABLE": "grapy-dev"})
    def setUp(self):
        self.db = DynamoDB()
        self.entity = "TEST"
        self.item = {
            "pk": "some-unique-id",
            "sk": self.entity,
            "data": "TEST#",
            "price": "foo"
        }
        self.db.add_item(self.item)

    def tearDown(self):
        # delete item
        self.db.delete_item("pk", self.item.get("pk"), "sk", self.entity)
        res = self.db.query_table("pk", self.item.get("pk")).get("Items")
        self.assertEqual(0, len(res))

    def test_add_item(self):
        """
        Test if an item is added correctly
        :return:
        """
        res = self.db.get_item("pk", self.item.get("pk"), "sk", self.entity).get("Item")
        self.assertEqual(self.item, res)

    def test_update_data(self):
        """
        Test if a global index attribute is updated correctly
        :return:
        """
        self.item["data"] = "TEST#123"
        self.db.add_item(self.item)
        res = self.db.get_item("pk", self.item.get("pk"), "sk", self.entity).get("Item")
        self.assertEqual(self.item, res)

    def test_update_attr(self):
        """
        Test if a non-key attribute is updated correctly
        :return:
        """
        self.item["price"] = "bar"
        self.db.add_item(self.item)
        res = self.db.get_item("pk", self.item.get("pk"), "sk", self.entity).get("Item")
        self.assertEqual(self.item, res)

    def test_query_table(self):
        """
        Test if the table is queried correctly
        :return:
        """
        res = self.db.query_table("pk", self.item.get("pk")).get("Items")
        self.assertEqual(1, len(res))
        self.assertEqual(self.item, res[0])

    def test_query_index(self):
        """
        Test if the index is queried correctly
        :return:
        """
        item2 = self.item.copy()
        item2["pk"] = "another-unique-url"
        self.db.add_item(item2)
        res = self.db.query_index("gsi_1", "sk", self.item.get("sk")).get("Items")
        self.assertEqual(2, len(res))

        self.db.delete_item("pk", item2.get("pk"), "sk", self.entity)
        res = self.db.query_index("gsi_1", "sk", self.item.get("sk")).get("Items")
        self.assertEqual(1, len(res))

    def test_metadata(self):
        """
        Test table metadata structure
        :return:
        """
        md = self.db.get_table_metadata()

        pk = md.get("primary_key_name").get("AttributeName")
        self.assertEqual("pk", pk)

        gsi = md.get("global_secondary_indices")
        self.assertEqual(1, len(gsi))
        self.assertEqual("gsi_1", gsi[0].get("IndexName"))

        keys = gsi[0].get("KeySchema")
        self.assertEqual(2, len(keys))
        self.assertEqual("sk", keys[0].get("AttributeName"))
        self.assertEqual("data", keys[1].get("AttributeName"))


if __name__ == "__main__":
    unittest.main()
