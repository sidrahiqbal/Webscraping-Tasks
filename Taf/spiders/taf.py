import json
import urllib

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from Taf.items import TafItem


class TafParseSpider(scrapy.Spider):
    name = "taf_parse"
    BASE_URL = 'https://www.taf.com.mx/api/catalog_system/pub/products/search'
    item = TafItem()

    def retailer_sku(self, response):
        return self.raw_data_extractor(response)['productId']

    def market(self, response):
        return response.css('meta[name="country"]::attr(content)').get()

    def lang(self, response):
        return response.css('html::attr(lang)').get().split('-')[0]

    def gender(self, response):
        return response['Género']

    def color(self, response):
        return response['Color']

    def brand(self, response):
        return response['brand']

    def category(self, response):
        return response['categories']

    def name(self, response):
        return response['productName']

    def url(self, response):
        return self.raw_data_extractor(response)['pageUrl']

    def description(self, response):
        return response['description']

    def price(self, response):
        return response['items'][0]['sellers'][0]['commertialOffer']['Price']

    def currency(self, response):
        local_info = json.loads(response.css('script:contains(Currency)::text').get().split('=')[-1].replace(';', ''))
        return local_info['CurrencyLocale']['CurrencyEnglishName']

    def sku(self, response):
        skus = []

        for each_sku in response['items']:
            skus.append({'sku_id': each_sku['itemId'],
                         'name': each_sku['name'],
                         'price': each_sku['sellers'][0]['commertialOffer']['Price'],
                         'available': each_sku['sellers'][0]['commertialOffer']['IsAvailable'],
                         'currency': self.currency(page_response),
                         'size': each_sku['name'].split(':')[1]})

        return skus

    def raw_data_extractor(self,response):
        return json.loads(response.css('script:contains(sku)::text').getall()[1].replace('\nvtex.events.addData(', '').replace(');\n', ''))

    def image_url(self, response):
        return [image['imageUrl'] for image in response['items'][0]['images']]

    def product_search(self, response):
        product_info = json.loads(response.text)[0]
        self.item['image_urls'] = self.image_url(product_info)
        self.item['name'] = self.name(product_info)
        self.item['brand'] = self.brand(product_info)
        self.item['description'] = self.description(product_info)
        self.item['gender'] = self.gender(product_info)
        self.item['category'] = self.category(product_info)
        self.item['price'] = self.price(product_info)
        self.item['skus'] = self.sku(product_info)

        yield self.item

    def parse(self, response):
        global page_response
        page_response = response
        pid = int(self.retailer_sku(response))
        params = {'fq': f'productId:{pid}'}
        url = f'{self.BASE_URL}?{urllib.parse.urlencode(params)}'

        self.item['retailer_sku'] = self.retailer_sku(response)
        self.item['lang'] = self.lang(response)
        self.item['url'] = self.url(response)
        self.item['market'] = self.market(response)
        self.item['currency'] = self.currency(response)

        yield scrapy.Request(url=url, method='GET', callback=self.product_search)


class Taf(CrawlSpider):
    name = "taf_crawl"
    start_urls = ['https://www.taf.com.mx/']
    parse_spider = TafParseSpider()
    allowed_domains = ['taf.com.mx']
    rules = (
        Rule(LinkExtractor(allow=(r'/p$',)), callback=parse_spider.parse),
        Rule(LinkExtractor(restrict_css=('.nav-item--level-1', '.product-list__wrapper'))),
    )
