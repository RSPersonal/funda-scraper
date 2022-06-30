import re
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from items import FundaItem


def start_spider(place):
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    process.crawl(FundaSpiderSold)
    process.start()


class FundaSpiderSold(scrapy.Spider):
    name = 'funda_sold'
    allowed_domains = ['funda.nl']

    def __int__(self, place, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = ["https://www.funda.nl/koop/%s/verkocht/sorteer-afmelddatum-af/p%s/" % (place, page_number)
                           for page_number in range(1, 2)]
        self.base_url = "https://www.funda.nl/koop/%s/" % place
        self.lel = LinkExtractor(allow=r'%s+(huis|appartement-\d{8}' % self.base_url)

    def parse(self, response, **kwargs):
        links = self.lel.extract_links(response)
        for link in links:
            if link.url.count('/') == 6 and link.url.endswith('/'):
                item = FundaItem
                item['url'] = link.url
                if re.search(r'/appartement-', link.url):
                    item['property_type'] = "apartment"
                elif re.search(r'/huis-', link.url):
                    item['property_type'] = "house"
                yield scrapy.Request(link.url, callback=self.parse_dir_contents, meta={'item': item})

    def parse_dir_contents(self, response):
        new_item = response.meta['item']
        title = response.xpath('//title/text()').extract()[0]
        address = re.findall(r'te koop: (.*) \d{4}', title)[0].replace(' ', '')
        street = re.search('[a-zA-Z]+', address).group(0)
        housenumber = re.search('[0-9]+', address).group(0)
        housenumber_add = re.search('^[0-9]+[a-zA-Z]+', address).group(0)
        postal_code = re.search(r'\d{4} [A-Z]{2}', title).group(0)
        city = re.search(r'\d{4} [A-Z]{2} \w+', address).group(0).split()[2]
        area_dd = response.xpath("//span[contains@title, 'wonen')]/following-sibling::span[1]/text()").extract()[0]
        area = re.findall(r'\d+', area_dd)[0]
        price_dd = response.xpath('.//strong[@class="object-header__price"]/text()').extract()[0]
        price = ''.join(re.findall(r'\d+', price_dd)).replace('.', '')
        new_item['street'] = street
        new_item['housenumber'] = housenumber
        new_item['housenumber_add'] = housenumber_add
        new_item['postal_code'] = postal_code
        new_item['city'] = city
        new_item['area'] = area
        new_item['price'] = price
        new_item['date_sold'] = date_sold
