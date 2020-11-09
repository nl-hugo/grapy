# Inspired by: https://stackoverflow.com/questions/33290876/how-to-create-custom-scrapy-item-exporter
import logging

import requests
from scrapy.exporters import BaseItemExporter
from scrapy.utils.serialize import ScrapyJSONEncoder

logger = logging.getLogger(__name__)


class RestApiExporter(BaseItemExporter):

    def __init__(self, api_url, api_key, **kwargs):
        super().__init__(dont_fail=True, **kwargs)
        self.api_url = api_url
        self.headers = {"x-api-key": api_key}
        self._kwargs.setdefault("ensure_ascii", not self.encoding)
        self.encoder = ScrapyJSONEncoder(**self._kwargs)

    def start_exporting(self):
        logger.debug(f"Start exporting to {self.api_url}")

    def finish_exporting(self):
        logger.debug(f"Done exporting")

    def export_item(self, item):
        item_dict = dict(self._get_serialized_fields(item))
        data = self.encoder.encode(item_dict) + "\n"
        logger.debug(f"PUT {self.api_url} - {data}")
        try:
            r = requests.put(url=self.api_url, headers=self.headers, data=data)
            logger.debug(f"Response: {r.headers}")
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            logger.error(err)
