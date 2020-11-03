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

    accepted_volumes = [.375, .5, .75, 1, 1.5, 2.25, 3, 6]

    forbidden_names = [
        "proefdoos",
        "pakket",
        "giftbox",
        "cadeau"
    ]

    def validate(self):
        logging.debug("Validate item {}".format(self))

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
                raise DropItem("Vintage not between 1700 and {}: {}".format(this_year, vintage))
        except ValueError:
            if vintage not in ["U.V.", "N.V."]:
                raise DropItem("Vintage not \"U.V.\" or \"N.V.\": {}".format(vintage))

        # price must be greater than one
        price = self.get("price")
        if price <= 1:
            raise DropItem("Price too low {}".format(price))

        # acceptable volumes
        volume = self.get("volume")
        if volume not in self.accepted_volumes:
            raise DropItem("Volume {} not acceptable ({})".format(volume, self.accepted_volumes))

        # must not contain forbidden name
        for name in self.forbidden_names:
            if name in self.get("name").lower():
                raise DropItem("Forbidden name {}".format(name))
