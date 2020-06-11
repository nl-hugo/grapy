# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class VendorWine(scrapy.Item):
    vendor = scrapy.Field()
    url = scrapy.Field()
    winery = scrapy.Field()
    name = scrapy.Field()
    price = scrapy.Field()
    volume = scrapy.Field()
    year = scrapy.Field()
