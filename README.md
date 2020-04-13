# Web Scrapping/Crawler/Bots

Scrapping web content using python scrapy. This bot intended to scrape amazon product details based on the ISIN Link provided as input.

### Prerequisites

Python 3.6.0 or higher.
Dependency lib's are added into requirement.txt, run dependency.txt to install required python packages.

### Installing and running

A step by step series of examples that tell you how to get a development env running

Install dependency packages 

```
    pip install -r requirement.txt

```

### One time Settings

Download chrome web driver and unzip to your driver https://chromedriver.chromium.org/

open amazon_products/settings.py and change the below path to installed chrome web driver
SELENIUM_DRIVER_EXECUTABLE_PATH = 'E:/chromedriver_win32/chromedriver.exe'

### Running program

```
cd E:\python\amazon_products
scrapy crawl ProductSpider

csv will be generated under ./amazon_products/output folder of your current directory.
```

## Author

**Deepa Aswathaiah**


