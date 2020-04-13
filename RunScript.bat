@echo off
echo "Running amazon product bot"
python -V
rem pip install -r requirement.txt
scrapy crawl ProductSpider
echo "Output file generated under output directory"