# -*- coding: utf-8 -*-
import logging

from vendors.exporters import RestApiExporter

logger = logging.getLogger(__name__)


class WineVendorsPipeline(object):

    def __init__(self, api_url, api_key, forbidden_names, accepted_volumes):
        # set api properties
        self.api_url = api_url
        self.api_key = api_key

        # set item validation properties
        self.forbidden_names = forbidden_names
        self.accepted_volumes = accepted_volumes

    @classmethod
    def from_crawler(cls, crawler):
        # get api settings from settings.py
        api_url = crawler.settings.get("DYNAMODB_ENDPOINT")
        api_key = crawler.settings.get("DYNAMODB_API_KEY")

        # get item validation settings from settings.py
        forbidden_names = crawler.settings.getlist("FORBIDDEN_NAMES")
        accepted_volumes = crawler.settings.getlist("ACCEPTED_VOLUMES")

        return cls(api_url, api_key, forbidden_names, accepted_volumes)

    def open_spider(self, spider):
        logger.info("Spider opened, open exporter")
        self.exporter = RestApiExporter(self.api_url, self.api_key)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        logger.info("Spider closed, close exporter")
        self.exporter.finish_exporting()

    def process_item(self, item, spider):
        logger.info(f"Processing item {item}")
        item.validate(self.forbidden_names, self.accepted_volumes)
        self.exporter.export_item(item)
        return item
