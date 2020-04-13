# -*- coding: utf-8 -*-
import os
from pathlib import Path

import scrapy
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from scrapy_selenium import SeleniumRequest

import pandas as pd
import requests

requests.packages.urllib3.disable_warnings()


class ProductspiderSpider(scrapy.Spider):
    """
    Scrape amazon products from link address
    """

    name = 'ProductSpider'
    allowed_domains = ['www.amazon.com']

    #start_urls = ['https://www.amazon.com/dp/B000ROKSSS']

    def __get_start_urls(self):
        """
        Read input file containing asin link
        :return:
        """
        df = pd.read_excel('{}/../../isin_input.xlsx'.format(Path(__file__).resolve().parent))
        start_urls = list(df['Link'].unique())
        print('total start_urls: {}'.format(len(start_urls)))

        # start_urls = start_urls[:10]
        return start_urls

    def start_requests(self):
        self.start_urls = self.__get_start_urls()
        for url in self.start_urls:
            yield SeleniumRequest(
                url=url,
                callback=self.scrape_product,
                errback=self.failure,
                dont_filter=True,
                wait_time=0.0001,
                wait_until=EC.element_to_be_clickable((By.ID, 'productTitle'))
            )

    def scrape_product(self, response):
        """
        scrape product information
        :param response:
        :return:
        """

        request_url = response.request.url
        print('Scraping: {}'.format(request_url))
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
        # print(product)
        yield product

    def failure(self, failure):
        # log all failures
        print(repr(failure))
        yield None
