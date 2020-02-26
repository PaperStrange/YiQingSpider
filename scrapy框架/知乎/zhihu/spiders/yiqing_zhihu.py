# -*- coding: utf-8 -*-
import re
import scrapy
import json
import time
from scrapy_redis.spiders import RedisSpider
from zhihu.items import ProjectItem


class YiQingZhihuSpider(RedisSpider):
    '''
    请务必修改setting.py
    REDIS_HOST
    REDIS_PORT
    REDIS_PASSWORD

    默认情况下以单线程线程间隔为1S本地IP运行
    可能会比较慢，请适当添加线程数

    多线程并发请修改zhihu.middlewares.RandomUserAgentMiddleware
    并修改custom_settings、配置代理池
    '''

    name = 'yiqing_zhihu'
    allowed_domains = ['zhihu.com']
    base_url = 'https://www.zhihu.com/api/v4/search_v3?t=general&q={}&correction=1&offset={}&limit=20'
    Key_words = []
    with open("./keywords.txt", 'rb') as f: 
        Key_words.append(f.read())
    # Key_words = [
    #     '防护服',
    #     '医用手套',
    #     '体温枪',
    #     '洗手液',
    #     '口罩',
    #     '假口罩',
    #     '假物资',
    #     '假物流',
    #     '假募捐',
    #     '假消息',        
    #     '假筹款',
    #     '虚假+口罩',        
    #     '虚假+物资',
    #     '虚假+物流',
    #     '虚假+募捐',
    #     '虚假+消息',
    #     '虚假+筹款',
    #     '奸商',
    #     '贵',
    #     '死贵',
    #     '没良心',
    #     '无良',
    #     '无良商家',
    #     '没底线',
    #     '国难财',
    #     '被查',
    #     '被抓',
    #     '被罚',
    #     '曝光',
    #     '谣言',
    #     '辟谣'
    #     ]
    PATH_TITLE = '//*[@class="QuestionHeader-title"]/text()'
    PATH_AUTHOR = '//div[@class="Popover"]/div/a/text()'
    PATH_AUTHOR_URL = '//div[@class="Popover"]/div/a/@href'
    PATH_TIME = '//div[@class="ContentItem-time"]/a/span/text()'
    custom_settings = {
        'DOWNLOAD_DELAY': 10, # 每个request的间隔
        'CONCURRENT_REQUESTS': 3, # 线程数
        'CONCURRENT_REQUESTS_PER_IP': 16,
        'SCHEDULER_PERSIST': True,
        'DOWNLOAD_TIMEOUT': 5,
        'DOWNLOADER_MIDDLEWARES': {
            'zhihu.middlewares.RandomUserAgentMiddleware': 400,
        },
        'ITEM_PIPELINES': {
            'zhihu.pipelines.ZhihuPipeline': 100,
            'scrapy_redis.pipelines.RedisPipeline': 300
        }
    }
    
    def start_requests(self):
        for key in self.Key_words:
            for num in range(0,200,20):
                yield scrapy.Request(
                    url=self.base_url.format(key,str(num)),
                    callback=self.parse,
                    dont_filter=True
                )

    def parse(self, response):
        response_json = json.loads(response.text)
        for i in range(0, 20):
            try:
                id = response_json['data'][i]['object']['id']
            except:
                id = None
            try:
                type_ = response_json['data'][i]['object']['type']
            except:
                type_ = 'answer'
            try:
                question_id = response_json['data'][i]['object']['question']['id']
            except:
                question_id = None
            try:
                question_type = response_json['data'][i]['object']['question']['type']
            except:
                question_type = 'question'
            try:
                description = response_json['data'][i]['highlight']['description']
            except:
                description = None
            if description == None:
                continue
            if id != None and question_id != None:
                url = 'https://www.zhihu.com/{}/{}/{}/{}'.format(question_type,question_id,type_,id)
            elif question_id == None:
                if id == None:
                    continue
                else:
                    url = 'https://api.zhihu.com/articles/{}'.format(id)
            yield scrapy.Request(
                url=url,callback=self.parse_,
                meta={'description':description},
                dont_filter=False
            )
    
    def parse_(self,response):
        if 'api' in response.url:
            item = ProjectItem()
            response_json = json.loads(response.text)
            item['source'] = '知乎'
            try:
                temp = re.findall('<(.*)>', response_json['excerpt'])[0]
                description = response_json['excerpt'].replace(temp, '').strip('<>')
            except:
                item['description'] = response_json['excerpt']
            else:
                item['description'] = description
            try:
                timestamp = int(response_json['created'])
                urltimeArr = time.localtime(int(timestamp))
                t = time.strftime("%Y-%m-%d %H:%M:%S", urltimeArr)
                item['time'] = str(t)
            except:
                item['time'] = None
            try:
                url = response.url
                url = url.replace('https://api.zhihu.com/articles/','https://zhuanlan.zhihu.com/p/')
                item['url'] = url
            except:
                item['url'] = ''
            try:
                item['title'] = response_json['title']
            except:
                item['title'] = ''
            try:
                item['author'] = response_json['author']['name']
            except:
                item['author'] = '知乎用户'
            try:
                item['author_url'] = response_json['author']['url'].replace('api.','')
            except:
                item['author_url'] = ' '
            yield item
        else:
            item = ProjectItem()
            item['source'] = '知乎'
            # item['description'] = response.meta['description']
            try:
                temp = re.findall('<(.*)>', response.meta['description'])[0]
                description = response.meta['description'].replace(temp, '').strip('<>')
            except:
                item['description'] = response.meta['description']
            else:
                item['description'] = description
            try:
                item['time'] = response.xpath(self.PATH_TIME).extract()[0]
            except:
                item['time'] = None
            item['url'] = response.url
            try:
                item['title'] = response.xpath(self.PATH_TITLE).extract()[0]
            except:
                item['title'] = ''
            try:
                item['author'] = response.xpath(self.PATH_AUTHOR).extract()[0]
            except:
                item['author'] = '知乎用户'
            try:
                if 'https:' not in response.xpath(self.PATH_AUTHOR_URL).extract()[0]:
                    author_url = 'https:'+response.xpath(self.PATH_AUTHOR_URL).extract()[0]
                item['author_url'] = author_url
            except:
                item['author_url'] = ' '
            yield item