#encoding:utf-8
from scrapy import cmdline
cmdline.execute("scrapy crawl weibo".split())
# cmdline.execute(["scrapy","crawl","爬虫名称"])