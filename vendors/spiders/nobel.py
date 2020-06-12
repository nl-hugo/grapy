# -*- coding: utf-8 -*-
import scrapy

from vendors.items import VendorWine
from vendors.utils import float_or_none


class NobelSpider(scrapy.Spider):
    name = 'nobel'
    allowed_domains = ['nobelwijnen.nl']
    start_urls = [
        'http://www.nobelwijnen.nl/rode-wijnen/',
        'http://www.nobelwijnen.nl/witte-wijnen/',
        'http://www.nobelwijnen.nl/rose-wijnen/',
    ]

    def parse(self, response):
        """ Parse the response """
        urls = response.css('.product-hover > a::attr(href)').extract()
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_item)

        next_page_url = response.css('.pages-item-next > a::attr(href)').get()
        if next_page_url is not None:
            yield scrapy.Request(response.urljoin(next_page_url))

    def parse_item(self, response):
        """ Creates a WineVendorsItem from the response """
        wine = VendorWine()
        wine['vendor'] = {'name': 'Nobel wijnkoperij', 'url': self.allowed_domains[0]}
        wine['url'] = response.url
        wine['winery'] = ''
        wine['name'] = response.css('meta[property="og:title"]::attr(content)').get()
        wine['price'] = float_or_none(response.css('meta[property="product:price:amount"]::attr(content)').get())

        volume_label = response.css('#product-attribute-specs-table td[data-th="Inhoud"]::text').get()
        if volume_label:
            wine['volume'] = float_or_none(volume_label.replace(',', '.').split(' ')[0])

        wine['year'] = response.css('#product-attribute-specs-table td[data-th="Oogstjaar"]::text').get()

        yield wine
