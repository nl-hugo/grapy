# -*- coding: utf-8 -*-
import json
import logging
import os

import requests

logger = logging.getLogger()
logger.setLevel(os.environ.get("LOGGING", logging.DEBUG))


class WineVendorsPipeline(object):
    API_ENDPOINT = os.environ.get("DYNAMODB_ENDPOINT")
    API_KEY = os.environ.get("DYNAMODB_API_KEY")

    def __init__(self, forbidden_names, accepted_volumes):
        self.FORBIDDEN_NAMES = forbidden_names
        self.ACCEPTED_VOLUMES = accepted_volumes

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        return cls(settings.getlist("FORBIDDEN_NAMES"), settings.getlist("ACCEPTED_VOLUMES"))

    def process_item(self, item, spider):
        logging.info(f"Processing item {item}")
        # item.validate()
        item.validate(self.FORBIDDEN_NAMES, self.ACCEPTED_VOLUMES)

        # make a request to put the item
        data = json.dumps(dict(item))
        headers = {"x-api-key": self.API_KEY}

        logging.debug(f"PUT {self.API_ENDPOINT} - {data}")
        try:
            r = requests.put(url=self.API_ENDPOINT, headers=headers, data=data)
            logging.debug(f"Response: {r.headers}")
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            logging.error(err)

        return item
