# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import os
import json
import hashlib

OLD_DATA_FILEPATH = "spiders/old_data/"
NEW_DATA_FILEPATH = "spiders/new_data/"

class WxGzhPipeline(object):
    def process_item(self, item, spider):
        count_ = len(item["gzh"])
        if count_:
            news = [{'source':item["source"][i], 'title':item["title"][i], 'gzh':item["gzh"][i], 'public_time':item["public_time"][i], 'url':item["url"][i], 'summary':item["summary"][i]} for i in range(count_)]
        else:
            news = [{'source':"", 'title':"", 'gzh':"", 'public_time':"", 'url':"", 'summary':""}]
        print("----------------------------------------------------")
        print(news)
        if news[0]['gzh']:
            for each_data in news:
                # url = each_data['url']
                title = each_data['title']
                # each_data['content']  = self.detail(url)
                # print(title, detail, desp, account, date)
                # print(hashlib.new('md5', bytes(title)).hexdigest())
                if not os.path.isfile(OLD_DATA_FILEPATH+hashlib.new('md5', title.encode(encoding='UTF-8')).hexdigest()+".txt") :
                    try:
                        fo = open(NEW_DATA_FILEPATH+hashlib.new('md5', title.encode(encoding='UTF-8')).hexdigest()+".txt", "w")
                        fo.write(json.dumps(each_data))
                        fo.close()
                        print("新增：{}".format(title))
                    except:
                        print(each_data)
                        print("写入失败")
                else:
                    print("重复：{}".format(title))
                # time.sleep(1)
        else:
            pass
        return item
