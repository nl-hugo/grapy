import logging
import os

from algoliasearch.search_client import SearchClient

logger = logging.getLogger()
logger.setLevel(os.environ.get("LOGGING", logging.DEBUG))


def is_in_aws():
    return os.getenv("AWS_EXECUTION_ENV") is not None


class VivinoSearch:
    def __init__(self):
        # In AWS, Algolia variables are available in the env; outside AWS these must be loaded from the .env file.
        if not is_in_aws():
            from dotenv import load_dotenv
            load_dotenv()
        self.client = SearchClient.create()
        self.index = self.client.init_index(os.environ.get("ALGOLIA_INDEX"))

    @staticmethod
    def _get_year(item):
        return item.get("year")

    @staticmethod
    def _get_vintage(wine, year):
        """
        Gets the correct vintage from the wine or UV if no matching vintage is found. Other vintages are discarded.

        :param wine: the wine dict
        :param year: the year
        :return: the vintage dict
        """
        # sort vintages by year and get the correct vintage
        vintage = sorted([v for v in wine.get("vintages") if v["year"] == str(year) or v["year"] == "U.V."],
                         key=VivinoSearch._get_year)
        return vintage[0]

    def _get_wine(self, keywords):
        """
        Search the wine that best matches the keywords and returns the first result

        :param keywords: the keywords to search on
        :return: the first search result
        """
        res = self.index.search(keywords, {
            "attributesToRetrieve": [
                "id",
                "name",
                "type_id",
                "style_id",
                "region.id",
                "grapes",
                "winery.id",
                "vintages.id",
                "vintages.year",
            ],
            "hitsPerPage": 1
        })
        hits = res.get("hits")

        if hits and len(hits) > 0:
            logging.info(f"{len(hits)} Results for keywords {keywords}")
            result = hits[0]
            del result["_highlightResult"]  # no need for highlights
            return result

    def search(self, keywords, year="U.V."):
        """
        Search for wine and vintage on Vivino

        :param keywords:
        :param year:
        :return:
        """
        logging.info(f"Searching for {keywords} and vintage {year}")
        wine = self._get_wine(keywords)
        wine["vintages"] = VivinoSearch._get_vintage(wine, year)
        logging.info(f"Found {wine}")
        return wine


if __name__ == "__main__":
    pass
