import re
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from items import FundaItem


def start_spider(place):
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    process.crawl(FundaSpider, place)
    process.start()


class FundaSpider(scrapy.Spider):
    name = "funda_spider"
    allowed_domains = ["funda.nl"]

    def __init__(self, place, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = ["https://www.funda.nl/koop/%s/p%s/" % (place, page_number) for page_number in range(1, 2)]
        self.base_url = "https://www.funda.nl/koop/%s/" % place
        self.le1 = LinkExtractor(allow=r'%s+(huis|appartement)-\d{8}' % self.base_url)

    def parse(self, response, **kwargs):
        links = self.le1.extract_links(response)
        for link in links:
            if link.url.count('/') == 6 and link.url.endswith('/'):
                item = FundaItem()
                item['url'] = link.url
                if re.search(r'/appartement-', link.url):
                    item['property_type'] = "apartment"
                elif re.search(r'/huis-', link.url):
                    item['property_type'] = "house"
                yield scrapy.Request(link.url, callback=self.parse_dir_contents, meta={'item': item})

    def parse_dir_contents(self, response):
        """
        @param response:
        @return: processed item for pipeline
        """
        new_item = response.request.meta['item']
        title = response.xpath('//title/text()').extract()[0]
        postal_code = re.search(r'\d{4} [A-Z]{2}', title).group(0)
        city = re.search(r'\d{4} [A-Z]{2} \w+', title).group(0).split()[2]
        address = re.findall(r'te koop: (.*) \d{4}', title)[0].replace(' ', '')
        street_extracted = re.search('[-a-zA-Z]+', address).group(0)
        price_dd = response.xpath('.//strong[@class="object-header__price"]/text()').extract()[0]
        price = ''.join(re.findall(r'\d+', price_dd)).replace('.', '')
        housenumber = re.search('[0-9]+', address).group(0)
        housenumber_add = re.search(r'\d[a-zA-Z]+', address)
        # TODO Extract also the housenumber add
        area_dd = response.xpath("//span[contains(@title,'wonen')]/following-sibling::span[1]/text()").extract()[0]
        area = re.findall(r'\d+', area_dd)[0]

        new_item['street'] = street_extracted
        new_item['housenumber'] = housenumber
        if housenumber_add:
            new_item['housenumber_add'] = housenumber_add.group(0)
        new_item['city'] = city
        new_item['postal_code'] = postal_code.replace(' ', '')
        new_item['address'] = address
        new_item['price'] = price
        new_item['status'] = "Te koop"
        new_item['area'] = area

        # TODO Expand datapoints
        # new_item['year_built'] = year_built
        # year_built_dd = response.xpath("//dt[contains(.,'Bouwjaar')]/following-sibling::dd[1]/text()").extract()[0]
        # year_built = self.construction_year(response)
        # rooms_dd = response.xpath("//dt[contains(.,'Aantal kamers')]/following-sibling::dd[1]/text()").extract()[0]
        # rooms = re.findall('\d+ kamer', rooms_dd)[0].replace(' kamer', '')
        # bedrooms = response.xpath("//span[contains(@title,'slaapkamer')]/following-sibling::span[1]/text()").extract()[0]
        # new_item['rooms'] = rooms
        # new_item['bedrooms'] = bedrooms
        yield new_item

    def construction_year(self, response):
        try:
            # Some have a single bouwjaar
            singleYear = response.xpath("//dt[text()='Bouwjaar']/following-sibling::dd/span/text()").extract()
            # Some have a period
            period = response.xpath("//dt[text()='Bouwperiode']/following-sibling::dd/span/text()").extract()
            if len(singleYear) > 0:
                # Some are built before 1906 (earliest date that Funda will let you specify)
                return re.findall(r'\d{4}', singleYear[0])[0]
            elif len(period) > 0:
                return re.findall(r'$\d{4}', period[0])[0]
            else:
                return 'unknown'
        except:
            return "Failed to parse"


if __name__ == '__main__':
    start_spider('zwolle')
