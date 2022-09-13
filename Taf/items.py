import scrapy


class TafItem(scrapy.Item):
    retailer_sku = scrapy.Field()
    lang = scrapy.Field()
    market = scrapy.Field()
    gender = scrapy.Field()
    image_urls = scrapy.Field()
    price = scrapy.Field()
    currency = scrapy.Field()
    color = scrapy.Field()
    url = scrapy.Field()
    brand = scrapy.Field()
    category = scrapy.Field()
    name = scrapy.Field()
    description = scrapy.Field()
    skus = scrapy.Field()
