import json
from urllib.parse import urljoin
from urllib.request import urlopen

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from Taf.items import TafItem


class TafParseSpider(scrapy.Spider):
    name = "taf"

    def product_id(self, response):
        return self.raw_data_extractor(response)['productId']

    def gender(self, response):
        return response.css('td[class="value-field Genero"]::text').get()

    def color(self, response):
        return response.css('td[class="value-field Color"]::text').get()

    def brand(self, response):
        return self.raw_data_extractor(response)['productBrandName']

    def category(self, response):
        return self.raw_data_extractor(response)['productDepartmentName']

    def subcategory(self, response):
        return self.raw_data_extractor(response)['productCategoryName']

    def product_name(self, response):
        return self.raw_data_extractor(response)['productName']

    def url(self, response):
        return self.raw_data_extractor(response)['pageUrl']

    def description(self, response):
        return response.css('.productDescription ::text').get()

    def sku(self, response):
        skus = []
        for each_sku in self.skus_data_extractor(response)['skus']:
            skus.append({'sku_id': each_sku['sku'],
                         'sku_name': each_sku['skuname'],
                         'price': each_sku['bestPrice'],
                         'seller': each_sku['seller'],
                         'available': each_sku['available'],
                         'available_quantity': each_sku['availablequantity'],
                         'size': each_sku['dimensions']})
        return skus

    def raw_data_extractor(self,response):
        return json.loads(response.css('script:contains(sku)::text').getall()[1].replace('\nvtex.events.addData(', '').replace(');\n', ''))

    def skus_data_extractor(self, response):
        return json.loads(response.css('script:contains(sku)::text').getall()[-1].replace("var skuJson_0 = ", '').replace(";CATALOG_SDK.setProductWithVariationsCache(skuJson_0.productId, skuJson_0); var skuJson = skuJson_0;", ''))

    def image_urls(self, response):
        sku_id = list(self.raw_data_extractor(response)['skuStocks'].keys())[0]
        result = urlopen(urljoin('https://www.taf.com.mx/produto/sku/', sku_id))
        result = json.loads(result.read())
        image_urls = []

        for each in result[0]['Images']:
            image_urls.append((each[0]['Path']))

        return image_urls

    def parse(self, response):
        item = TafItem()
        item['product_id'] = self.product_id(response)
        item['url'] = self.url(response)
        item['image_urls'] = self.image_urls(response)
        item['gender'] = self.gender(response)
        item['color'] = self.color(response)
        item['brand'] = self.brand(response)
        item['category'] = self.category(response)
        item['subcategory'] = self.subcategory(response)
        item['name'] = self.product_name(response)
        item['description'] = self.description(response)
        item['skus'] = self.sku(response)

        yield item


class Taf(CrawlSpider):
    name = "taf_spider"
    start_urls = ['https://www.taf.com.mx/']
    parse_spider = TafParseSpider()
    allowed_domains = ['taf.com.mx']
    rules = (
        Rule(LinkExtractor(allow=(r'/p$',)), callback=parse_spider.parse),
        Rule(LinkExtractor(restrict_css=('.nav-item--level-1', '.product-list__wrapper'))),
    )
