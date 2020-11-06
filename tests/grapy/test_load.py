import unittest

import grapy.load as utils


class TestGrapyDdb(unittest.TestCase):

    def setUp(self):
        self.row = {
            "id": 3778,
            "name": "Gevrey-Chambertin 1er Cru \"La Bossière\"",
            "country": "fr",
            "class": {
                "id": 37,
                "country_code": "fr",
                "abbreviation": "Premier Cru",
                "description": "Burgundy Premier Cru"
            }
        }

    def test_safe_build_composite_sort_key(self):
        res = utils.build_composite_sort_key(self.row, "regions#id")
        self.assertEqual("regions#3778", res)

    def test_safe_build_node_list(self):
        res = utils.build_node_list([self.row], "id", "REGIONS", "name")
        item = res[0]["PutRequest"]["Item"]
        self.assertEqual("regions#3778", item["pk"])
        self.assertEqual(self.row["name"], item["data"])
        self.assertFalse("id" in item)

    # def test_safe_build_node_list_keep(self):
    #     res = utils.build_node_list([self.row], "id", "REGIONS", "name", keep=["country", "class.id", "fail"])
    #     item = res[0]["PutRequest"]["Item"]
    #     self.assertTrue("country" in item)
    #     self.assertTrue("class.id" in item)
    #     self.assertEqual(None, item["fail"])

    def test_build_node_missing_fields(self):
        item = {
            "id": 3899667,
            "winery.id": None
        }
        res = utils.build_node(item, "id", "WINES", "wineries#winery.id")
        self.assertEqual("wines#3899667", res["pk"])
        self.assertEqual("wineries#", res["data"])


if __name__ == "__main__":
    unittest.main()
