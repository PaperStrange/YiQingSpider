# from scrapy.cmdline import execute
from scrapy import cmdline
import os

cmdline.execute('scrapy crawl yiqing_zhihu'.split())
# TODO 2020/02/27-1:35: deal with the stop time
# os.system("shutdown -s -t  60 ")