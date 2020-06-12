# -*- coding: utf-8 -*-
import scrapy

from vendors.items import VendorWine
from vendors.utils import float_or_none

volumes = {
    '75 cl': .75,
    '75cl': .75,
    '150 cl': 1.5,
    '150cl': 1.5,
    '300 cl': 3,
}


class HvdwSpider(scrapy.Spider):
    name = 'hvdw'
    allowed_domains = ['heerenvandewijn.nl']
    start_urls = [
        'https://www.heerenvandewijn.nl/wijn/rode-wijn/',
        'https://www.heerenvandewijn.nl/wijn/witte-wijn/',
        'https://www.heerenvandewijn.nl/wijn/rose-wijn/',
    ]

    def parse(self, response):
        """ Parse the response """
        urls = response.css('#products .prod a.title::attr(href)').extract()
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_item)

        next_page_url = response \
            .xpath('//p[contains(@class, "list-pages")]/a[contains(text(), "Volgende")]/@href').get()
        if next_page_url is not None:
            yield scrapy.Request(response.urljoin(next_page_url))

    def parse_item(self, response):
        """ Creates a WineVendorsItem from the response """
        wine = VendorWine()
        wine['vendor'] = {'name': 'Heeren van de Wijn', 'url': self.allowed_domains[0]}
        wine['url'] = response.url

        wine['winery'] = response.css('#product-info > .details') \
            .xpath('//strong[contains(text(), "Merk:")]/following-sibling::a[1]/text()').get()
        wine['name'] = response.css('strong[itemprop="name"]::text').get()
        wine['price'] = float_or_none(response.css('span[itemprop="price"]::text').get().replace(',', '.'))
        wine['year'] = None  # TODO: year is not advertised
        volume = response.css('#product-info > .details') \
            .xpath('//strong[contains(text(), "Inhoud:")]/following-sibling::text()').get().strip()
        wine['volume'] = volumes.get(volume, -1)

        yield wine
