import json
import urllib

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from Taf.items import TafItem


class Mixin:
    BASE_URL = 'https://www.taf.com.mx/api/catalog_system/pub/products/search'
    start_urls = ['https://www.taf.com.mx/']
    allowed_domains = ['taf.com.mx']
    lang = 'es'
    market = 'MEX'
    currency = 'Mexican Peso'


class TafParseSpider(Mixin, scrapy.Spider):
    name = "taf_parse"
    BASE_URL = Mixin.BASE_URL

    def parse(self, response):
        pid = int(self.retailer_sku(response))
        params = {'fq': f'productId:{pid}'}
        url = f'{self.BASE_URL}?{urllib.parse.urlencode(params)}'

        yield scrapy.Request(url=url, method='GET', callback=self.product_search, meta={'first_response': response})

    def product_search(self, response):
        product_info = json.loads(response.text)[0]
        item = TafItem()
        item['retailer_sku'] = self.retailer_sku(response.meta.get('first_response'))
        item['lang'] = Mixin.lang
        item['url'] = self.url(response.meta.get('first_response'))
        item['market'] = Mixin.market
        item['currency'] = Mixin.currency
        item['image_urls'] = self.image_url(product_info)
        item['name'] = self.name(product_info)
        item['brand'] = self.brand(product_info)
        item['description'] = self.description(product_info)
        item['gender'] = self.gender(product_info)
        item['category'] = self.category(product_info)
        item['price'] = self.price(product_info)
        item['skus'] = self.sku(product_info)

        yield item

    def retailer_sku(self, response):
        return self.raw_data_extractor(response)['productId']

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

    def sku(self, response):
        skus = []

        for each_sku in response['items']:
            skus.append({'sku_id': each_sku['itemId'],
                         'name': each_sku['name'],
                         'price': each_sku['sellers'][0]['commertialOffer']['Price'],
                         'out_of_stock': False if each_sku['sellers'][0]['commertialOffer']['IsAvailable'] else True,
                         'currency': Mixin.currency,
                         'size': each_sku['name'].split(':')[1]})

        return skus

    def raw_data_extractor(self, response):
        sku_script = response.css('script:contains(sku)::text').getall()[1]
        return json.loads(sku_script.replace('\nvtex.events.addData(', '').replace(');\n', ''))

    def image_url(self, response):
        return [image['imageUrl'] for image in response['items'][0]['images']]


class Taf(Mixin, CrawlSpider):
    name = "taf_crawl"
    start_urls = Mixin.start_urls
    parse_spider = TafParseSpider()
    allowed_domains = Mixin.allowed_domains
    rules = (
        Rule(LinkExtractor(allow=(r'/p$',)), callback=parse_spider.parse),
        Rule(LinkExtractor(restrict_css=('.nav-item--level-1', '.product-list__wrapper'))),
    )
