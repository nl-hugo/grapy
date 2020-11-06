import json
import logging
import os
from decimal import Decimal

import requests

from grapy.utils import safe_get

logger = logging.getLogger()
logger.setLevel(os.environ.get("LOGGING", logging.DEBUG))


class VivinoApi:
    def __init__(self):
        self.base_url = "http://api.vivino.com/"

    def _query_api(self, entity, key=None):
        key_str = "/" + str(key) if key else ""
        url = f"{self.base_url}{entity}{key_str}"
        logging.debug(f"Querying {url}")

        response = requests.get(url)
        if response.status_code == requests.codes.ok:
            return json.loads(response.text, parse_float=Decimal)
        else:
            response.raise_for_status()

    @staticmethod
    def _keep_selected_fields(response, keep):
        result = {}
        for k in keep:
            result[k] = safe_get(response, k.split("."))
        return result

    def _process_query(self, entity, key=None, keep=None):
        logging.info(f"Query {entity}/{key}, keeping fields {keep}")

        response = self._query_api(entity, key)
        if keep is None:
            keep = []

        if key is not None:
            result = VivinoApi._keep_selected_fields(response, keep)
        else:
            result = []
            # check if detailed info is available (e.g. for grapes)
            for item in response:
                if item.get("has_detailed_info") is True:
                    detailed_item = self._query_api(entity, key=item.get("id"))
                    result.append(VivinoApi._keep_selected_fields(detailed_item, keep))
                else:
                    result.append(VivinoApi._keep_selected_fields(item, keep))
        return result

    def get_countries(self):
        """ Queries all countries and keeps selected fields """
        keep = ["code", "name"]
        return self._process_query(entity="countries", keep=keep)

    def get_regions(self):
        """ Queries all regions and keeps selected fields """
        keep = ["id", "name", "country"]
        return self._process_query(entity="regions", keep=keep)

    def get_wine_types(self):
        """ Queries all wine types and keeps selected fields """
        keep = ["id", "name"]
        return self._process_query(entity="wine-types", keep=keep)

    def get_wine_styles(self):
        """ Queries all wine styles and keeps selected fields """
        keep = ["id", "name", "regional_name", "varietal_name"]
        return self._process_query(entity="wine-styles", keep=keep)

    def get_grapes(self):
        """ Queries all grapes and keeps selected fields """
        keep = ["id", "name", "flavor_profile", "color", "acidity", "body"]
        return self._process_query(entity="grapes", keep=keep)

    # def get_wine(event, context):
    #     key = event.get("id")
    #     keep = [
    #         "id",
    #         "name",
    #         "winery.id"
    #     ]
    #     return handler({"entity": "wines", "id": key, "keep": keep}, context)

    def get_wine(self, search_result):
        """ Returns a wine dict for the specified search result """
        # create wine object; this is a bit different from the other entities, because the fields that we need are
        # part of the search result
        keep = ["id", "name", "winery.id", "type_id", "style_id", "grapes"]
        return VivinoApi._keep_selected_fields(search_result, keep)

    def get_winery(self, key):
        """ Queries the winery specified by the key and keeps selected fields
        :param key: the winery id
        """
        keep = ["id", "name", "region.id", "website", "location"]
        return self._process_query(entity="wineries", key=key, keep=keep)

    def get_vintage(self, key):
        """ Queries the vintage specified by the key and keeps selected fields
        :param key: the vintage id
        """
        keep = ["id", "name", "wine.id", "year", "statistics.ratings_count", "statistics.ratings_average"]
        return self._process_query(entity="vintages", key=key, keep=keep)


if __name__ == "__main__":
    pass
