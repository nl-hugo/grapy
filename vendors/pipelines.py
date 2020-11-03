# -*- coding: utf-8 -*-
import json
import logging
import os

import requests

logger = logging.getLogger()
logger.setLevel(os.environ.get("LOGGING", logging.DEBUG))


class WineVendorsPipeline(object):
    def __init__(self):
        self.api_endpoint = os.environ.get("DYNAMODB_ENDPOINT")
        self.api_key = os.environ.get("DYNAMODB_API_KEY")

    def process_item(self, item, spider):
        logging.info(f"Processing item {item}")
        item.validate()

        # make a request to put the item
        data = json.dumps(dict(item))
        headers = {"x-api-key": self.api_key}

        logging.debug(f"PUT {self.api_endpoint} - {data}")
        try:
            r = requests.put(url=self.api_endpoint, headers=headers, data=data)
            logging.debug(f"Response: {r.headers}")
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            logging.error(err)

        return item
