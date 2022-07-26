import re
import sys
import getopt
import scrapy
import sentry_sdk
from scrapy.linkextractors import LinkExtractor
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from items import FundaItem
from funda_helpers import transform_date_to_database_date_format


def main(argv):
    """
    @param argv: -p = place
    @return: starts spider with user input or returns error
    """
    argument_list = sys.argv[1:]
    options = "p:"
    long_options = ["Place"]

    try:
        arguments, values = getopt.getopt(argument_list, options, long_options)
        for currentArgument, currentValue in arguments:
            if currentArgument in ('-p', '--Place'):
                start_spider(currentValue)
    except getopt.error as err:
        print(str(err))


def start_spider(place: str):
    """
    Starts spider
    @param place: str
    @return: None
    """
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    process.crawl(FundaSpiderSold, place)
    if "twisted.internet.reactor" in sys.modules:
        del sys.modules["twisted.internet.reactor"]
    process.start()


class FundaSpiderSold(scrapy.Spider):
    name = 'funda_sold'
    allowed_domains = ["funda.nl"]

    def __init__(self, place, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = ["https://www.funda.nl/koop/verkocht/%s/p%s/" % (place, page_number) for page_number in
                           range(1, 50)]
        self.base_url = "https://www.funda.nl/koop/verkocht/%s/" % place
        self.le1 = LinkExtractor(allow=r'%s+(huis|appartement)-\d{8}' % self.base_url)
        self.le2 = LinkExtractor(allow=r'%s+(huis|appartement)-\d{8}.*/kenmerken/' % self.base_url)

    def parse(self, response, **kwargs):
        links = self.le1.extract_links(response)
        slash_count = self.base_url.count('/') + 1  # Controls the depth of the links to be scraped
        for link in links:
            if link.url.count('/') == slash_count and link.url.endswith('/'):
                item = FundaItem()
                item['url'] = link.url
                if re.search(r'/appartement-', link.url):
                    item['property_type'] = "apartment"
                elif re.search(r'/huis-', link.url):
                    item['property_type'] = "house"
                yield scrapy.Request(link.url, callback=self.parse_dir_contents, meta={'item': item})

    def parse_dir_contents(self, response):
        new_item = response.meta['item']
        title = response.xpath('//title/text()').extract()[0]
        address = re.findall(r'Verkocht: (.*) \d{4}', title)[0].replace(' ', '')
        street = re.search('[a-zA-Z]+', address).group(0)
        housenumber = re.search(r'\d+', address).group(0)
        housenumber_add = re.search(r'\d[a-zA-Z]+', address)
        if housenumber_add and len(housenumber_add.group(0)) > 15:
            housenumber_add = 'to long'
        try:
            postal_code = re.search(r'\d{4} [A-Z]{2}', title).group(0)
        except AttributeError as e:
            print(e, "\n Property has no postal code, probably newly built and has no postal code yed")
            pass
        city = re.search(r'\d{4} [A-Z]{2} \w+', title).group(0).split()[2]
        area_dd = response.xpath("//span[contains(@title, 'wonen')]/following-sibling::span[1]/text()").extract()[0]
        area = re.findall(r'\d+', area_dd)[0]
        try:
            plot_size_dd = response.xpath("//span[contains(@title, 'perceel')]/following-sibling::span[1]/text()").extract()[0]
            plot_size = re.search(r'\d+', plot_size_dd).group(0)
        except IndexError as e:
            plot_size = ''
            sentry_sdk.capture_exception(e)
            pass
        price_dd = response.xpath('.//strong[@class="object-header__price--historic"]/text()').extract()[0]
        price = ''.join(re.findall(r'\d+', price_dd)).replace('.', '')
        year_sold_dd = response.xpath("//dt[contains(.,'Verkoopdatum')]/following-sibling::dd[1]/text()").extract()[0]
        year_sold_clean = transform_date_to_database_date_format(year_sold_dd)
        new_item['street'] = street
        new_item['housenumber'] = housenumber
        if housenumber_add:
            new_item['housenumber_add'] = housenumber_add.group(0)
        new_item['postal_code'] = postal_code
        new_item['city'] = city
        new_item['area'] = area
        if plot_size:
            new_item['plot_size'] = plot_size
        if price:
            new_item['price'] = price
        else:
            new_item['price'] = 0
        new_item['year_sold'] = year_sold_clean
        new_item['status'] = 'Verkocht'
        yield new_item


if __name__ == '__main__':
    main(sys.argv[1:])
