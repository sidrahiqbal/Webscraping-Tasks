import scrapy


class TafItem(scrapy.Item):
    product_id = scrapy.Field()
    gender = scrapy.Field()
    image_urls = scrapy.Field()
    color = scrapy.Field()
    url = scrapy.Field()
    brand = scrapy.Field()
    category = scrapy.Field()
    subcategory = scrapy.Field()
    name = scrapy.Field()
    description = scrapy.Field()
    skus = scrapy.Field()
