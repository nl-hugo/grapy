import logging
import os

import grapy.utils as utils
from grapy.grapy_db import GrapyDDB
from grapy.vivino_api import VivinoApi
from grapy.vivino_search import VivinoSearch

logger = logging.getLogger()
logger.setLevel(os.environ.get("LOGGING", logging.INFO))


class Grapy():
    def __init__(self):
        self.db = GrapyDDB()
        self.api = VivinoApi()
        self.search = VivinoSearch()
        self.batch_size = int(os.environ.get("BATCH_SIZE", 10))
        logging.debug(f"Initialized, BATCH_SIZE {self.batch_size}")

    @staticmethod
    def _get_last_seen(item):
        return item.get("last_updated_at", "")
        # return item.get("lastVivinofied", "")

    def vivinofy(self):
        """
        Searches the database for vendor wines without Vivino search result and searches Vivino for any matching
        vintages. Search results are added to the Grapy databases.
        :return:
        """
        # list all wines without vintage
        # TODO: maybe we want to update ratings for wines WITH vintage as well now and then...
        items = self.db.get_unknown_vintage().get("Items")
        logging.info(f"{len(items)} Vendor wine(s) ready to vivinofy")

        # sort by date last seen, oldest first
        sort_items = sorted(items, key=Grapy._get_last_seen)

        for item in sort_items[:self.batch_size]:
            # get keywords and search vivino
            keywords = f'{item.get("winery")} {item.get("name")}'
            year = item.get("year")

            logging.info(f"Searching vintage \"{year}\" for keywords \"{keywords}\"")
            search_result = self.search.search(keywords, year)

            # from the response, we should create a wine, vintage, winery object
            # search and store winery
            winery_id = utils.safe_get(search_result, ["winery", "id"])
            if winery_id:
                winery = self.api.get_winery(winery_id)
                self.db.add_winery(winery)

            # search and store vintage
            vintage_id = utils.safe_get(search_result, ["vintages", "id"])
            if vintage_id:
                vintage = self.api.get_vintage(vintage_id)
                self.db.add_vintage(vintage)

            # create wine object from the search result
            wine = self.api.get_wine(search_result)
            self.db.add_wine(wine)

            # set the vintage# for the vendor wine item
            self.db.set_vintage(item.get("pk"), vintage_id)

        return utils.num_updated(len(items), self.batch_size), utils.num_remaining(len(items), self.batch_size)
