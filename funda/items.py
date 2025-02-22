import scrapy


class FundaItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    address = scrapy.Field()
    street = scrapy.Field()
    housenumber = scrapy.Field()
    housenumber_add = scrapy.Field()
    postal_code = scrapy.Field()
    price = scrapy.Field()  # Listing price ("Vraagprijs")
    year_sold = scrapy.Field()
    year_built = scrapy.Field()  # Year built ("Bouwjaar")
    area = scrapy.Field()  # Built area ("Woonoppervlakte")
    plot_size = scrapy.Field()
    rooms = scrapy.Field()  # Number of rooms
    bedrooms = scrapy.Field()  # Number of bedrooms
    property_type = scrapy.Field()  # House or apartment
    city = scrapy.Field()
    posting_date = scrapy.Field()
    sale_date = scrapy.Field()
    status = scrapy.Field()
