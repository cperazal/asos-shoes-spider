import scrapy
from scrapy import Request
import json

class AsoShoesSpider(scrapy.Spider):
    name = 'asos_shoes'
    allowed_domains = ['asos.com']
    start_urls = ['https://www.asos.com/men/shoes-boots-trainers/boots/cat/?cid=5774&nlid=mw%7Cshoes%7Cshop%20by%20product%7Cboots&page=1']

    def parse(self, response):
        products = response.xpath('//article/a/@href').extract()
        for product in products:
            yield Request(product,
                          callback=self.parse_product)

        next_page_url = response.xpath('//a[text()="Load more"]/@href').extract_first()
        if next_page_url:
            yield Request(next_page_url,
                          callback=self.parse)

    def parse_product(self, response):
        product_name = response.xpath('//h1/text()').extract_first()
        product_id = response.url.split('/prd/')[1].split('?')[0]
        price_api_url = f'https://www.asos.com/api/product/catalogue/v3/stockprice?productIds={product_id}&store=ROW&currency=USD'
        yield Request(price_api_url,
                      meta={'product_name': product_name},
                      callback=self.parse_product_price)

    def parse_product_price(self, response):
        json_response = json.loads(response.body.decode('utf-8'))
        product_price = json_response[0]['productPrice']['current']['text']

        yield {
            'product_name': response.meta['product_name'],
            'product_price': product_price
        }

