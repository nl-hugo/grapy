# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import logging
from datetime import date

import scrapy
from scrapy.exceptions import DropItem


class VendorWine(scrapy.Item):
    vendor = scrapy.Field()
    url = scrapy.Field()
    winery = scrapy.Field()
    name = scrapy.Field()
    price = scrapy.Field()
    volume = scrapy.Field()
    year = scrapy.Field()

    def validate(self, forbidden_names, accepted_volumes):
        logging.debug(f"Validate item {self}")

        # set vintage to "U.V." (unknown) if no year is specified
        if not self.get("year"):
            logging.warning("Vintage missing, set to U.V.")
            self["year"] = "U.V."

        # all fields must be present with a non-empty value
        for field in self.fields:
            data = self.get(field)
            if not data and not field == "winery":
                raise DropItem(f"Missing {field}")

        # year must be a valid number, "N.V." or "U.V."
        vintage = self.get("year")
        try:
            this_year = date.today().year
            if not 1700 < int(vintage) < this_year:
                raise DropItem(f"Vintage not between 1700 and {this_year}: {vintage}")
        except ValueError:
            if vintage not in ["U.V.", "N.V."]:
                raise DropItem(f"Vintage not \"U.V.\" or \"N.V.\": {vintage}")

        # price must be greater than one
        price = self.get("price")
        if price <= 1:
            logging.warning(f"Price too low {price}")
        #     raise DropItem(f"Price too low {price}")

        # acceptable volumes
        volume = self.get("volume")
        if volume not in accepted_volumes:
            raise DropItem(f"Volume {volume} not acceptable ({accepted_volumes})")

        # must not contain forbidden name
        for name in forbidden_names:
            if name in self.get("name").lower():
                raise DropItem(f"Forbidden name {name}")
