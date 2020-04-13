# -*- coding: utf-8 -*-
import scrapy
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from scrapy_selenium import SeleniumRequest


class AmazonproductsbycategorySpider(scrapy.Spider):
    name = 'AmazonProductsByCategory'
    amazon_base_url = 'https://www.amazon.com'
    allowed_domains = ['www.amazon.com']
    start_urls = ['https://www.amazon.com/s?k=Baby+Foods&rh=n%3A16323111&ref=nb_sb_noss']

    def start_requests(self):
        # self.start_urls = self.__get_start_urls()
        for url in self.start_urls:
            yield SeleniumRequest(
                url=url,
                callback=self.scrape_product,
                errback=self.failure,
                dont_filter=True,
                wait_time=0.0001,
                wait_until=EC.element_to_be_clickable((By.CLASS_NAME, 's-search-results'))
            )

    def scrape_product(self, response):
        """
        scrape product information
        :param response:
        :return:
        """

        for href in response.css('ul.a-pagination li.a-last ::attr(href)').getall():
            self.logger.info('following to next page: %s', href)
            print('{}/{}'.format(self.amazon_base_url, href))
            # yield response.follow(href, self.scrape_product)
            yield SeleniumRequest(
                url='{}/{}'.format(self.amazon_base_url, href),
                callback=self.scrape_product,
                errback=self.failure,
                dont_filter=True,
                wait_time=0.0001,
                wait_until=EC.element_to_be_clickable((By.CLASS_NAME, 's-search-results'))
            )

        result_xpath = '//div[@id="search"]//span[@data-component-type="s-search-results"]//div[@data-asin]'
        for product in response.xpath(result_xpath):
            asin = product.xpath('./@data-asin').get()
            product_info = {
                'asin': asin,
                'product_url': '{}/dp/{}'.format(self.amazon_base_url, asin),
                'product_name': product.xpath(
                    './/span[@class="a-size-base-plus a-color-base a-text-normal"]/text()').get(),
                'lowest_price': product.xpath('.//span[@class="a-price"]/span/text()').get(),
                'prime': product.xpath('.//i[@aria-label="Amazon Prime"]/@aria-label').get(),
                'start_rating': product.xpath('.//span[@class="a-icon-alt"]/text()').get(),
            }
            yield SeleniumRequest(
                url=product_info['product_url'],
                callback=self.scrape_product_details,
                meta=dict(product_info=product_info),
                errback=self.failure,
                dont_filter=True,
                wait_time=0.0001,
                wait_until=EC.element_to_be_clickable((By.ID, 'productTitle'))
            )
            # print(product_info)
            # products.append(product_info)
            # yield product_info

    def scrape_product_details(self, response):
        """
        scrape product information
        :param response:
        :return:
        """
        product_info = response.meta['product_info']
        request_url = response.request.url
        #print('Scraping: {}'.format(request_url))
        # asin and product name
        asin = [url for url in str(request_url).split('/') if url][-1]
        product_name = response.xpath('//span[@id="productTitle"]/text()').get()

        if response.xpath('//span[@id="unqualified-buybox-olp"]'):
            price = response.xpath('//span[@id="unqualified-buybox-olp"]//span[@class="a-color-price"]/text()').get()
        elif response.xpath('//*[@id="price_inside_buybox"]'):
            price = response.xpath('//*[@id="price_inside_buybox"]/text()').get()
        else:
            price = response.xpath('//*[@id="outOfStock"]//span[@class="a-color-price a-text-bold"]/text()').get()

        # images
        image_url = response.xpath('//img[@id="landingImage"]/@src').get()
        alt_images = [img for img in
                      response.xpath('//div[@id="altImages"]//span[@class="a-button-text"]/img/@src').getall() if
                      str(img).endswith('.jpg')]

        ingredients = [info.xpath('.//p/text()').get() for info in
                       response.xpath('//*[@id="important-information"]/div') if
                       info.xpath('.//span[@class="a-text-bold"]/text()').get() == 'Ingredients']

        # product details
        product = {
            'ASIN': asin,
            'Link': request_url,
            'Product Name': str(product_name).strip(),
            'Price': str(price).strip(),
            'Ingredients': ingredients.pop(0) if len(ingredients) > 0 else None,
            'Picture (URL)': image_url,
            'Picture of nutritrion information': '\n'.join(alt_images),

        }

        product_info.update(product)
        #print(product_info)
        yield product_info

    def failure(self, failure):
        # log all failures
        print(repr(failure))
        yield None
