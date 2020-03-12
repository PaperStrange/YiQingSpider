# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import csv
import re
import time, datetime


CURRENT_DATE = datetime.datetime.now()
START_DATE = int(time.mktime((CURRENT_DATE - datetime.timedelta(days=7)).timetuple()))  # 只抓取距现在一周内的文章，考虑到知乎上文章的更新速度做出调整
FILENAME = '知乎_{}-{}-{}.csv'.format(str(CURRENT_DATE.year), str(CURRENT_DATE.month), str(CURRENT_DATE.day))

class ZhihuPipeline(object):
    def process_item(self, item, spider):
        if item['time'] is None:
            pass
        else:
            with open(FILENAME, 'a+', newline='', encoding='utf_8') as f:
                fieldnames = [
                    'source', 
                    'title', 
                    'author',
                    'time', 
                    'url', 
                    'description', 
                    'author_url', 
                    'importance'
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                if 'question' not in item['url']:           
                    if '2020' in item['time']:
                        try:
                            year = re.findall('2020-(.*?)-', item['time'])[0]
                        except:
                            year = '01'
                        day = int(re.findall('2020-\d\d-(\d\d)', item['time'])[0])
                        if year == '01':
                            if day >= 23:
                                part = item['time'].split(" ")
                                if len(part) == 2:
                                    if len(part[0]) > len(part[1]):
                                        shorttime = part[0]
                                    else:
                                        shorttime = part[1]
                                    try:
                                        Article_date = time.mktime(time.strptime(shorttime, "%Y-%m-%d"))
                                    except:
                                        print("---X----------------------------------------")
                                        print(shorttime)
                                    else:
                                        if Article_date > START_DATE:                                        
                                            writer.writerow(
                                                {
                                                    'source': item['source'], 
                                                    'title': item['title'],
                                                    'author': item['author'],
                                                    'time': shorttime,
                                                    'url': item['url'],
                                                    'description': item['description'],
                                                    'author_url': item['author_url'],
                                                    'importance': "" 
                                                }
                                            )                                           
                                else:
                                    print("G---What's Happen？----------------------------------------")
                                    print(item['time'])                                    
                                    writer.writerow(
                                        {
                                            'source': item['source'], 
                                            'title': item['title'],
                                            'author': item['author'],
                                            'time': item['time'],
                                            'url': item['url'],
                                            'description': item['description'],
                                            'author_url': item['author_url'],
                                            'importance': "" 
                                        }
                                    ) 
                        else:
                            part = item['time'].split(" ")
                            if len(part) == 2:
                                if len(part[0]) > len(part[1]):
                                    shorttime = part[0]
                                else:
                                    shorttime = part[1] 
                                try:
                                    Article_date = time.mktime(time.strptime(shorttime, "%Y-%m-%d"))
                                except:
                                    print("---Y----------------------------------------")
                                    print(shorttime)
                                else:
                                    if Article_date > START_DATE:                                       
                                        writer.writerow(
                                            {
                                                'source': item['source'], 
                                                'title': item['title'],
                                                'author': item['author'],
                                                'time': shorttime,
                                                'url': item['url'],
                                                'description': item['description'],
                                                'author_url': item['author_url'],
                                                'importance': "" 
                                            }
                                        )                                           
                            else:
                                print("Q---What's Happen？----------------------------------------")
                                print(item['time'])                                  
                                writer.writerow(
                                    {
                                        'source': item['source'], 
                                        'title': item['title'],
                                        'author': item['author'],
                                        'time': item['time'],
                                        'url': item['url'],
                                        'description': item['description'],
                                        'author_url': item['author_url'],
                                        'importance': "" 
                                    }
                                )                                                        
                    elif '昨天' in item['time']:
                        writer.writerow(
                            {
                                'source': item['source'], 
                                'title': item['title'],
                                'author': item['author'],
                                'time': '{}-{}-{}'.format(str(CURRENT_DATE.year), str(CURRENT_DATE.month), str(CURRENT_DATE.day-1)),
                                'url': item['url'],
                                'description': item['description'],
                                'author_url': item['author_url'],
                                'importance': "" 
                            }
                        )  
                    elif len(item['time']) < 10:
                        try:
                            Article_date = time.mktime(time.strptime(item['time'], "%Y-%m-%d"))
                        except:
                            print("---Z----------------------------------------")
                            print(item['time'])
                        else:
                            if Article_date > START_DATE:
                                writer.writerow(
                                {
                                    'source': item['source'], 
                                    'title': item['title'],
                                    'author': item['author'],
                                    'time': '{}-{}-{}'.format(str(CURRENT_DATE.year), str(CURRENT_DATE.month), str(CURRENT_DATE.day)),
                                    'url': item['url'],
                                    'description': item['description'],
                                    'author_url': item['author_url'],
                                    'importance': "" 
                                }
                            ) 
        return item