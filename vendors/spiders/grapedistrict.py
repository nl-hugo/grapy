# -*- coding: utf-8 -*-
import json

import scrapy

from vendors.items import VendorWine
from vendors.utils import float_or_none


class GrapedistrictSpider(scrapy.Spider):
    name = 'grapedistrict'
    allowed_domains = ['grapedistrict.nl']
    start_urls = [
        'https://www.grapedistrict.nl/tegels/rode-wijnen.html',
        'https://www.grapedistrict.nl/tegels/witte-wijnen.html',
        'https://www.grapedistrict.nl/smaak/rosy.html',
    ]

    def parse(self, response):
        """ Parse the response """
        urls = response.css('ul.products-grid > li.item > a::attr(href)').extract()
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_item)

    def parse_item(self, response):
        """ Creates a VendorWine from the response """
        wine = VendorWine()
        wine['vendor'] = {'name': self.name.title(), 'url': self.allowed_domains[0]}
        wine['url'] = response.url

        data = response.xpath('//script[@type="application/ld+json" and contains(text(), "Product")]/text()').get()
        d = json.loads(data)

        wine['winery'] = d.get('brand')
        wine['name'] = d.get('name')

        offers = d.get('offers', {})
        wine['price'] = float_or_none(offers.get('price'))
        wine['volume'] = 0.75
        wine['year'] = response.xpath(
            '//span[@class="item-details-title" and contains(text(), "Jaar")]/following-sibling::node()/text()').get()

        yield wine
