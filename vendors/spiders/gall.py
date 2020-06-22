# -*- coding: utf-8 -*-
import json
import re

import scrapy

from vendors.items import VendorWine

pattern = re.compile(r'dataLayer.push\((.*)\)')
volumes = {
    '37.5CL': .375,
    '50CL': .5,
    '75CL': .75,
    '150CL': 1.5,
    '225CL': 2.25,
    '600CL': 6,
}


class GallSpider(scrapy.Spider):
    name = 'gall'
    allowed_domains = ['gall.nl']
    start_urls = [
        'https://www.gall.nl/wijn/rode-wijn/',
        'https://www.gall.nl/wijn/witte-wijn/',
        'https://www.gall.nl/wijn/rose-wijn/',
    ]

    def parse(self, response):
        """ Parse the response """
        urls = response.css('.c-product-tile > a::attr(href)').extract()
        for url in urls:
            yield scrapy.Request(url=response.urljoin(url), callback=self.parse_item)

        next_page_url = response.css('.pagination__load-more > a::attr(href)').get()
        if next_page_url is not None:
            yield scrapy.Request(response.urljoin(next_page_url))

    def parse_item(self, response):
        """ Creates a VendorWine from the response """
        wine = VendorWine()
        wine['vendor'] = {'name': 'Gall&Gall', 'url': self.allowed_domains[0]}
        wine['url'] = response.url

        data = response.xpath('//script[contains(text(), "productDetail")]/text()').get()
        m = re.search(pattern, data)
        if m is not None:
            d = json.loads(m.group(1))
            product = d['ecommerce']['detail']['products'][0]
            wine['name'] = product['name']
            wine['winery'] = product['brand']
            wine['price'] = product['price']
            wine['volume'] = volumes.get(product['variant'], -1)

        wine['year'] = response.xpath(
            '//dd[@class="product-attributes__title" and contains(text(), "Oogstjaar")]/following-sibling::node()/text()').get()

        yield wine
