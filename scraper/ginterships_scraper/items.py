import scrapy

class OfferItem(scrapy.Item):
    title = scrapy.Field()
    company = scrapy.Field()
    location = scrapy.Field()
    url = scrapy.Field()
    source = scrapy.Field()
    category = scrapy.Field()      # "stage" ou "emploi"
