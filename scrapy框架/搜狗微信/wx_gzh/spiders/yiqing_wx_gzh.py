# -*- coding: utf-8 -*-
import re
import scrapy
# import json
import time, datetime
import random
# from requests import Session
# from urllib.parse import urlencode
from scrapy_redis.spiders import RedisSpider
# from wx_gzh.settings import HEADERS, START_TIME
from wx_gzh.items import WxGzhItem

import hashlib
from pyquery import PyQuery as pq
import sys
sys.setrecursionlimit(1000000)


class YiqingWxGzhSpider(RedisSpider):
    name = 'yiqing_wx_gzh'
    allowed_domains = ['sogou.com']
    base_url = 'https://weixin.sogou.com/weixin?type={}&s_from=input&query={}'
    base_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,ja;q=0.4,zh-TW;q=0.2,mt;q=0.2',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Cookie': '',
        'Host': 'weixin.sogou.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3452.0 Safari/537.36'
    }
    custom_settings = {
        'DOWNLOAD_DELAY': 10,  #每个request的间隔
        'CONCURRENT_REQUESTS': 1,  #线程数
        'CONCURRENT_REQUESTS_PER_IP': 16,
        # 'SCHEDULER_PERSIST': True,
        'DOWNLOAD_TIMEOUT': 5,
        'DOWNLOADER_MIDDLEWARES': {
            # 'wx_gzh.middlewares.RandomProxy': 100,
            'wx_gzh.middlewares.RandomUserAgentMiddleware': 400,
        },
        'ITEM_PIPELINES': {
            # 'wx_gzh.pipelines.WxGzhPipeline': 100,
            'scrapy_redis.pipelines.RedisPipeline': 300
        }
    }
    news = {
        'source': [],
        'title': [],
        'gzh': [],
        'public_time': [],
        'url': [],
        'summary': []
    }
    # session = Session()
    url_temp = ""
    START_TIME = int(time.mktime((datetime.datetime.now() - datetime.timedelta(days=14)).timetuple()))  #只爬取这个时间戳之后的数据，目前设置为2周前
    empt = 0
    # keywords= []
    # with open("./keywords.txt", 'rb') as f:
    #     keywords.append(f.readline().decode())


    def start_requests(self):
        with open("./keywords.txt", 'rb') as f:
            keywords = f.read()
            for keyword in keywords.decode().split('\n'):
                if "#" not in keyword:
                    # count = 0
                    print("正在爬取的关键词：", keyword)
                    start_url = self.base_url.format(2, keyword)
                    print("正在爬取的搜索页：", start_url)
                    # 设置跳过指定页面
                    # if count == 1:
                    #     params['page'] = 10
                    #     continue
                    # elif count == 2:
                    #     params['page'] = 70
                    #     continue
                    # elif count == 3:
                    #     params['page'] = 93
                    # else:
                    #     pass
                    # print("爬取搜索页：", self.base_url.format(urlencode(params)))
                    self.url_temp = start_url
                    # self.update_request(start_url, self.init_headers())
                    yield scrapy.Request(
                        url=self.url_temp,
                        callback=self.parse,
                        dont_filter=False
                    )
                    # TODO 2020/02/25-2:25: how to deal the failure during the scrapy yield?

    def parse(self, response):  
        # TODO 2020/2/24-23:35: check the format of "response.url"
        # if u'出错了' in response.text:
        if 'com/antispider' in response.url:
            headers_ = self.update_cookie(self.init_headers())
            print("---------------------------------------------------")
            print(self.url_temp)
            yield scrapy.Request(
                headers=headers_,
                url=self.url_temp,
                callback=self.parse_,
                dont_filter=False)
        else:
            yield scrapy.Request(
                url=self.url_temp,
                callback=self.parse_,
                dont_filter=False)

    def parse_(self, response):  
        item_ = WxGzhItem()

        doc = pq(response.text)
        items = doc('.news-box .news-list li .txt-box').items()

        for item in items:
            a = item.find("h3 a")
            url = a.attr('href')
            if not re.match('https://', url):
                url = url.replace('http:', 'https:', 1)
            if not re.match('https://', url):
                url = 'https://weixin.sogou.com' + url
            title = a.text()
            desp = item.find('.txt-info').text()
            account = item.find('.account').text()
            ts = int(item.find('.s2').text()[28:-3])
            if ts > self.START_TIME: 
                self.news['source'].append("搜狗微信搜索")
                self.news['title'].append(title)
                self.news['gzh'].append(account)
                self.news['public_time'].append(self.pase_date(ts))
                self.news['url'].append("")
                self.news['summary'].append(desp)

        next_page = doc('#sogou_next').attr('href')
        if next_page:
            if not re.match('https://', next_page):
                next_page = self.url_temp + next_page
            print("下一页：", next_page)
            if len(self.news['url']) > 0:
                self.empt = 0        
                yield scrapy.Request(
                    url=next_page,
                    callback=self.parse,
                    dont_filter=True
                )
            elif self.empt < 4:
                self.empt +=1
                yield scrapy.Request(
                    url=next_page,
                    callback=self.parse,
                    dont_filter=True
                )

        item_['source'] = self.news['source']
        item_['title'] = self.news['title']
        item_['gzh'] = self.news['gzh']
        item_['public_time'] = self.news['public_time']
        item_['url'] = self.news['url']
        item_['summary'] = self.news['summary']
        yield item_
    
    # def update_request(self, start_url, headers):
    #     start_url_ = start_url
    #     self.session.headers.update(headers)
    #     resp = self.session.get(
    #         start_url_,
    #         # proxies={
    #         #     'http': "http://127.0.0.1:8888",
    #         #     'https': "http://127.0.0.1:8888"},
    #         verify=False
    #     )
    #     if 'com/antispider' in resp.url:
    #         headers_ = self.update_cookie(headers)
    #         time.sleep(15)
    #         self.update_request(start_url_, headers_)
    #     else:
    #         pass

    def init_headers(self):
        headers = self.base_headers
        with open("cookies.txt", 'rb') as f:
            headers['Cookie'] = f.read().decode() 
        # USER_AGENT = [
        #     "User-Agent, Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
        #     "User-Agent, Mozilla/5.0 (iPad; U; CPU OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
        #     "User-Agent, MQQBrowser/26 Mozilla/5.0 (Linux; U; Android 2.3.7; zh-cn; MB200 Build/GRJ22; CyanogenMod-7) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
        #     "User-Agent, Mozilla/5.0 (BlackBerry; U; BlackBerry 9800; en) AppleWebKit/534.1+ (KHTML, like Gecko) Version/6.0.0.337 Mobile Safari/534.1+",
        #     "User-Agent, Mozilla/5.0 (compatible; MSIE 9.0; Windows Phone OS 7.5; Trident/5.0; IEMobile/9.0; HTC; Titan)",
        #     "User-Agent, Mozilla/4.0 (compatible; MSIE 6.0; ) Opera/UCWEB7.0.2.37/28/999",
        #     "User-Agent, NOKIA5700/ UCWEB7.0.2.37/28/999",
        #     "User-Agent, Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
        #     "User-Agent, Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
        #     "User-Agent, Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 UBrowser/6.2.4094.1 Safari/537.36",
        #     "User-Agent, Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)",
        #     "User-Agent, Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)",
        #     "User-Agent, Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)",
        #     "User-Agent, Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)",
        #     "User-Agent, Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
        #     "User-Agent, Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11",
        #     "User-Agent, Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11",
        #     "User-Agent, Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv,2.0.1) Gecko/20100101 Firefox/4.0.1"
        # ]
        # headers['User-Agent'] = random.choice(USER_AGENT)
        return headers

    def update_cookie(self, headers):
        headers_ = headers
        while True:
            print("请输入验证码...并更新：cookies.txt")
            input("请确定修改，确认完毕后请输入数字1：")  #TODO 2020/2/25-1:05: need validation?
            with open("cookies.txt", 'rb') as f:
                cookie = f.read().decode()
                if cookie and cookie != '' and cookie != headers_["Cookie"] : 
                    headers_['Cookie'] = cookie
                    break      
        time.sleep(10)
        print("cookie已更新")
        return headers_   
    
    # def valid_url(self, url, headers):
    #     url += '&k=30&h=g'
    #     headers['Referer'] = 'https://weixin.sogou.com/weixin'       
    #     resp = self.session.get(
    #         url, 
    #         proxies = {
    #             'http': "http://127.0.0.1:8888",
    #             'https': "http://127.0.0.1:8888"}, 
    #         verify = False
    #     )
    #     if 'com/antispider' in resp.url:
    #         self.update_cookie()
    #         return self.get_url(url, HEADERS)
    #     m = re.findall(r"url \+\= '(.*)';", resp.text)
    #     return "".join(m).replace("@","")

    def pase_date(self, ts):
        timeArray = time.localtime(ts)
        otherStyleTime = time.strftime("%Y-%m-%d", timeArray)
        return otherStyleTime

