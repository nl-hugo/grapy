# -*- coding: utf-8 -*-
import json
import re
from urllib.parse import urljoin

import scrapy

from vendors.items import VendorWine
from vendors.utils import float_or_none

year_pattern = re.compile(r'\s(\d+)$')


class VicampoSpider(scrapy.Spider):
    name = 'vicampo'
    allowed_domains = ['vicampo.nl']
    start_urls = [
        'https://api.vicampo.nl/v1/category_search?pagination_limit=500&type=Enkele+flessen&wine_type=Rode+wijn',
        'https://api.vicampo.nl/v1/category_search?pagination_limit=500&type=Enkele+flessen&wine_type=Witte+wijn',
        'https://api.vicampo.nl/v1/category_search?pagination_limit=500&type=Enkele+flessen&wine_type=Rosé',
    ]

    def parse(self, response):
        """ Parse the response """
        results = json.loads(response.text).get('results')
        for res in results:
            url = res.get('url')
            if res.get('entity_type') == 'product' and url:
                yield scrapy.Request(url=urljoin('https://' + self.allowed_domains[0], url), callback=self.parse_item)

    def parse_item(self, response):
        """ Creates a VendorWine from the response """
        wine = VendorWine()
        wine['vendor'] = {'name': self.name.title(), 'url': self.allowed_domains[0]}
        wine['url'] = response.url
        wine['winery'] = response.css('article::attr(data-ec-brand)').get()
        wine['name'] = response.css('article::attr(data-ec-name)').get()
        wine['price'] = float_or_none(response.css('article::attr(data-ec-price)').get())
        wine['volume'] = 1.5 if 'magnum' in wine['url'] else 0.75
        wine['year'] = 'U.V.'

        m = re.search(year_pattern, wine.get('name'))
        if m is not None:
            wine['year'] = m.group(1)

        yield wine
