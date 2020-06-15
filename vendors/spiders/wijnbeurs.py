# -*- coding: utf-8 -*-
import json
import re

import scrapy

from vendors.items import VendorWine
from vendors.utils import float_or_none

pattern = re.compile(r'productData = ({.+});')


class WijnbeursSpider(scrapy.Spider):
    name = 'wijnbeurs'
    allowed_domains = ['wijnbeurs.nl']
    start_urls = [
        'https://www.wijnbeurs.nl/rode-wijn',
        'https://www.wijnbeurs.nl/witte-wijn',
        'https://www.wijnbeurs.nl/rose',
    ]

    def parse(self, response):
        """ Parse the response """
        urls = response.css('ol.products > li.product-item > a::attr(href)').extract()
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_item)

        next_page_url = response.css('ul.pages-items > li.pages-item-next > a::attr(href)').get()
        if next_page_url is not None:
            yield scrapy.Request(next_page_url)

    def parse_item(self, response):
        """ Creates a VendorWine from the response """
        wine = VendorWine()
        wine['vendor'] = {'name': self.name.title(), 'url': self.allowed_domains[0]}
        wine['url'] = response.url

        data = response.xpath('//script[contains(text(), "productData")]/text()').get()
        m = re.search(pattern, data)
        if m is not None:
            d = json.loads(m.group(1))
            wine['winery'] = ''
            wine['name'] = d.get('name')
            wine['price'] = float_or_none(d.get('price'))

        wine['year'] = response.css('td[data-th="Jaargang"]::text').get()
        wine['volume'] = 1.5 if 'magnum' in wine['url'] else 0.75

        yield wine
