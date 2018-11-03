import scrapy


class OucModulesSpider(scrapy.Spider):
    name = "ouc"
    start_urls = [
        'https://www.ouc.ac.cy/web/guest/s2/programme/cos/modules',
    ]

    def parse(self, response):
        for q in response.xpath("//table[@id='course']/tbody/tr"):
            yield {
                'title': q.xpath("td[1]/a/text()").extract_first(),
                'link': q.xpath("td[1]/a/@href").extract_first(),
                'code': q.xpath("td[2]/text()").extract_first(),
                'ects': q.xpath("td[3]/text()").extract_first(),
            }
