# -*- coding: utf-8 -*-
import scrapy

from vendors.items import VendorWine
from vendors.utils import float_or_none


def find_property(response, label):
    # TODO: niet ==, maar contains (ignore case)
    return response.css('#product_tabs_kenmerken_contents') \
        .xpath('//td[text()="{}:"]/following-sibling::node()/text()'.format(label)).get().strip()


class GrandcruwijnenSpider(scrapy.Spider):
    name = 'grandcruwijnen'
    allowed_domains = ['grandcruwijnen.nl']
    start_urls = [
        'https://www.grandcruwijnen.nl/alle-wijnen/rood',
        'https://www.grandcruwijnen.nl/alle-wijnen/wit',
        'https://www.grandcruwijnen.nl/alle-wijnen/rose',
    ]

    def parse(self, response):
        """ Parse the response """
        urls = response.css('.products-list .product-name > a::attr(href)').extract()
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_item)

        next_page_url = response.css('.pages a.next::attr(href)').get()
        if next_page_url is not None:
            yield scrapy.Request(next_page_url)

    def parse_item(self, response):
        """ Creates a WineVendorsItem from the response """
        wine = VendorWine()
        wine['vendor'] = {'name': 'Grandcruwijnen', 'url': self.allowed_domains[0]}
        wine['url'] = response.url
        wine['winery'] = find_property(response, 'Wijnhuis')
        wine['name'] = response.css('h1.product-name::text').get()
        wine['price'] = float_or_none(response.css('span[itemprop="price"]::text').get())
        wine['volume'] = float_or_none(find_property(response, 'Inhoud fles').split(' ')[0])
        wine['year'] = find_property(response, 'Jaar')

        yield wine
