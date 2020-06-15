# -*- coding: utf-8 -*-
import json
import re

import scrapy

from vendors.items import VendorWine
from vendors.utils import float_or_none

volume_pattern = re.compile(r'-(\d+)cl/$')


class BartsSpider(scrapy.Spider):
    name = 'barts'
    allowed_domains = ['bartswijnkoperij.nl']
    start_urls = [
        'https://bartswijnkoperij.nl/product-categorie/rode-wijn/',
        'https://bartswijnkoperij.nl/product-categorie/witte-wijn/',
        'https://bartswijnkoperij.nl/product-categorie/rose-wijn/',
    ]

    def parse(self, response):
        """ Parse the response """
        urls = response.css('ul.products > li.product > div > a::attr(href)').extract()
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_item)

        next_page_url = response.css('a.page-numbers.next::attr(href)').get()
        if next_page_url is not None:
            yield scrapy.Request(next_page_url)

    def parse_item(self, response):
        """ Creates a VendorWine from the response """
        wine = VendorWine()
        wine['vendor'] = {'name': 'Barts Wijnkoperij', 'url': self.allowed_domains[0]}

        data = response.xpath('//script[@type="application/ld+json" and contains(text(), "Product")]/text()').get()
        d = json.loads(data)

        wine['url'] = d.get('url')
        wine['winery'] = ''
        wine['name'] = d.get('name')
        offers = d.get('offers', [])
        if len(offers) > 0:
            wine['price'] = float_or_none(offers[0]['price'])
        wine['year'] = ''
        wine['volume'] = 0.75

        m = re.search(volume_pattern, d.get('url'))
        if m is not None:
            wine['volume'] = float_or_none(m.group(1)) / 100

        yield wine
