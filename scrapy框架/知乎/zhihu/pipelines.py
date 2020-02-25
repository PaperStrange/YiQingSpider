# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import csv
import re
import datetime


CURRENT_DATE = datetime.datetime.now()
FILENAME = '知乎_{}-{}-{}.csv'.format(str(CURRENT_DATE.year),str(CURRENT_DATE.month),str(CURRENT_DATE.day))

class ZhihuPipeline(object):
    def process_item(self, item, spider):
        if item['time'] == None:
            pass
        else:
            with open(FILENAME, 'a+', newline='', encoding='utf_8') as f:
                fieldnames = [
                    'source', 'title', 'url', 'time', 'author', 'author_url', 'description'
                    ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                if '2020' in item['time']:
                    try:
                        year = re.findall('2020-(.*?)-',item['time'])[0]
                    except:
                        year = '01'
                    day = int(re.findall('2020-\d\d-(\d\d)',item['time'])[0])
                    if year == '01':
                        if day >= 23:
                                writer.writerow(
                                    {
                                        'source': item['source'], 
                                        'title': item['title'],
                                        'url': item['url'],
                                        'time': item['time'], 
                                        'author': item['author'],
                                        'author_url':item['author_url'],
                                        'description':item['description']
                                    }
                                )
                    else:
                        writer.writerow(
                            {
                                'source': item['source'], 
                                'title': item['title'], 
                                'url': item['url'], 
                                'time': item['time'],
                                'author': item['author'], 
                                'author_url': item['author_url'],
                                'description': item['description']
                            }
                        )
                elif '昨天' in item['time']:
                        writer.writerow(
                            {
                                'source': item['source'], 
                                'title': item['title'],
                                'url': item['url'],
                                'time': '{}-{}-{}'.format(str(CURRENT_DATE.year),str(CURRENT_DATE.month),str(CURRENT_DATE.day-1)), 
                                'author': item['author'],
                                'author_url': item['author_url'],
                                'description':item['description']
                            }
                        )
                elif len(item['time']) < 10:
                        writer.writerow(
                            {
                                'source': item['source'], 
                                'title': item['title'], 
                                'url': item['url'], 
                                'time': '{}-{}-{}'.format(str(CURRENT_DATE.year),str(CURRENT_DATE.month),str(CURRENT_DATE.day)),
                                'author': item['author'], 
                                'author_url': item['author_url'],
                                'description': item['description']
                            }
                        )
        return item