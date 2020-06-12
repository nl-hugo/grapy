# -*- coding: utf-8 -*-
import scrapy

from vendors.items import VendorWine
from vendors.utils import float_or_none


def find_property(response, label):
    result = response.css('#product-attribute-specs-table') \
        .xpath('//th[contains(text(), "{}")]/following-sibling::td/text()'.format(label)).get()
    if result is not None:
        result = result.strip()
    return result


class GoudentonSpider(scrapy.Spider):
    name = 'goudenton'
    allowed_domains = ['degoudenton.nl']
    start_urls = [
        'https://www.degoudenton.nl/rode-wijn',
        'https://www.degoudenton.nl/witte-wijn',
        'https://www.degoudenton.nl/rose-wijn',
    ]

    def parse(self, response):
        """ Parse the response """
        urls = response.css('.product-image::attr(href)').extract()
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_item)

        next_page_url = response.css('li.next-page > a::attr(href)').get()
        if next_page_url is not None:
            yield scrapy.Request(next_page_url)

    def parse_item(self, response):
        """ Creates a WineVendorsItem from the response """
        wine = VendorWine()
        wine['vendor'] = {'name': 'Wijnkoperij De Gouden Ton', 'url': self.allowed_domains[0]}
        wine['url'] = response.url
        wine['winery'] = find_property(response, 'Producent')
        wine['name'] = response.css('.product-name > h1::text').get()
        wine['price'] = float_or_none(response.css('meta[itemprop="price"]::attr(content)').get())
        wine['year'] = find_property(response, 'Oogst')
        wine['volume'] = float_or_none(find_property(response, 'inhoud').replace(',', '.'))

        yield wine
