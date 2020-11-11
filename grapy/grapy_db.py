import logging
import os
from time import localtime, strftime

from grapy import dynamo_db, load

logger = logging.getLogger()
logger.setLevel(os.environ.get("LOGGING", logging.INFO))


class GrapyDDB(dynamo_db.DynamoDB):
    def __init__(self):
        super().__init__()

    def populate(self):
        countries, regions, wine_types, wine_styles, grapes = load.load_data()
        table_data = load.build_adjacency_lists(countries, regions, wine_types, wine_styles, grapes)
        self.load_dynamo_data(table_data)

    def set_vintage(self, url, vintage_id):
        """
        Sets the vintage id for the vendor wine with the given url
        :param url:
        :param vintage_id:
        :return:
        """
        logger.debug(f"Set vintage id {vintage_id} for {url}")
        key = dynamo_db.DynamoDB._build_key("pk", url, "sk", "VENDORWINES")

        return self.table.update_item(
            Key=key,
            UpdateExpression="set #data=:v, #ts=:ts",
            ExpressionAttributeValues={
                ":v": f"vintages#{vintage_id}", ":ts": strftime("%Y-%m-%d %H:%M:%S %z", localtime())
            },
            ExpressionAttributeNames={"#data": "data", "#ts": "last_vivinofied_at"}
        )

    def add_vendor_wine(self, item):
        """
        Adds a scraped vendor wine item
        :param item:
        :return:
        """
        logger.info(f"Add vendor wine {item}")

        # adding the item updates existing items, if it already exists; note that all vintages are reset to `vintage#`
        # which forces a re-scrape on vivino
        row = load.build_node(item, "url", "VENDORWINES", "vintages#")
        result = self.add_item(row, "ALL_OLD")
        attrs = result.get("Attributes")

        # a vintage will be reused if it existed before the update and remains valid
        if attrs:
            # the vintage before the update
            vintage = attrs.get("data")

            # vintage remains valid if neither name, winery nor year has changed
            is_vintage_valid = attrs.get("name") == item.get("name") and attrs.get("winery") == item.get(
                "winery") and attrs.get("year") == item.get("year")
            logging.debug(f"Vintage id {vintage} already exist and remains valid: {is_vintage_valid}")

            # vintage# is always reset to vintage# by default
            # only if a vintage was known previously, then update
            if is_vintage_valid and vintage != "vintages#":
                row = load.build_node(item, "url", "VENDORWINES", vintage)
                result = self.add_item(row)

        return result

    def add_wine(self, item):
        """
        Adds a Vivino wine item
        :param item:
        :return:
        """
        logger.debug(f"Add wine {item}")
        row = load.build_node(item, "id", "WINES", "wineries#winery.id")
        return self.add_item(row)

    def add_winery(self, item):
        """
        Adds a Vivino winery item
        :param item:
        :return:
        """
        logger.debug(f"Add winery {item}")
        row = load.build_node(item, "id", "WINERIES", "regions#region.id")
        return self.add_item(row)

    def add_vintage(self, item):
        """
        Adds a Vivino vintage item
        :param item:
        :return:
        """
        logger.debug(f"Add vintage {item}")
        row = load.build_node(item, "id", "VINTAGES", "wines#wine.id")
        return self.add_item(row)

    def get_unknown_vintage(self):
        """
        Lists all vendorwines with an unknown vintage
        :return:
        """
        logger.debug("Get all vendor wines without vintage")
        return self.query_index("gsi_1", "sk", "VENDORWINES", "data", "vintages#")

    def get_all(self, table_name, last_key, limit=1000):
        """
        Lists all items from table
        :param table_name:
        :param last_key:
        :param limit:
        :return:
        """
        logger.debug(f"Get all {table_name} paginated from {last_key} limit {limit}")
        return self.query_index(index_name="gsi_1", pk_name="sk", pk_value=table_name.upper(), start_key=last_key,
                                limit=limit)

    def delete_all(self, table_name):
        """
        Deletes all items from table
        :param table_name:
        :return:
        """
        logger.debug(f"Delete all {table_name}")
        items = self.get_all(table_name, None, 1000).get("Items")
        for item in items:
            logging.debug(f"Deleting {item}")
            self.delete_item("pk", item.get("pk"), "sk", table_name.upper())

        return len(items)
