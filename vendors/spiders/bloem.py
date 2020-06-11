# -*- coding: utf-8 -*-
import re

import scrapy

from vendors.items import VendorWine
from vendors.utils import float_or_none

pattern = re.compile(r'\(([0-9,]*)\)')


def find_property(response, label):
    return response.css('ul.wijn-informatie') \
        .xpath('//li[contains(text(), "{}")]/strong/text()'.format(label)).get().strip()


class BloemSpider(scrapy.Spider):
    name = 'bloem'
    allowed_domains = ['henribloem.nl']
    start_urls = [
        'https://www.henribloem.nl/rode-wijn/',
        'https://www.henribloem.nl/witte-wijn/',
        'https://www.henribloem.nl/rose/',
    ]

    def parse(self, response):
        """ Parse the response """
        urls = response.css('#product-list > ul > li.product > a::attr(href)').extract()
        for url in urls:
            yield scrapy.Request(url=response.urljoin(url), callback=self.parse_item)

        next_page_url = response.css('nav.pagination > ol > li.next > a::attr(href)').get()
        if next_page_url is not None:
            yield scrapy.Request(response.urljoin(next_page_url))

    def parse_item(self, response):
        """ Creates a VendorWine from the response """
        wine = VendorWine()
        wine['vendor'] = {'name': 'Henri Bloem', 'url': self.allowed_domains[0]}
        wine['url'] = response.url
        wine['winery'] = find_property(response, 'Producent')
        wine['name'] = response.css('#product-specs > h2::text').get()
        wine['price'] = float_or_none(response.css('meta[itemprop="price"]::attr(content)').get())
        wine['year'] = find_property(response, 'Oogstjaar')
        wine['volume'] = .75

        # update volume if specified in wine name
        m = re.search(pattern, wine['name'])
        if m is not None:
            wine['volume'] = float_or_none(m.group(1).replace(',', '.'))

        yield wine
