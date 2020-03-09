from requests import Session
from config import *
import random
import time, datetime
import json, hashlib
from urllib.parse import urlencode
import requests
from pyquery import PyQuery as pq
from requests import ReadTimeout, ConnectionError
import re
import redis
import sys
sys.setrecursionlimit(1000000)


# redis代理
REDIS_HOST = '127.0.0.1'
REDIS_PORT = '6379'
REDIS_PASS = ''
REDIS_DB = 2
__redis = redis.Redis(host=REDIS_HOST, port= REDIS_PORT, password=REDIS_PASS, db = REDIS_DB, decode_responses=True) 

OLD_DATA_FILEPATH = "./old_data/"
NEW_DATA_FILEPATH = "./new_data/"

START_TIME = int(time.mktime((datetime.datetime.now() - datetime.timedelta(days=14)).timetuple()))  #只爬取这个时间戳之后的数据，目前设置为2周前
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

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,ja;q=0.4,zh-TW;q=0.2,mt;q=0.2',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Cookie': '',
    'Host': 'weixin.sogou.com',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': ''}
# headers['User-Agent'] = random.choice(USER_AGENT)
headers['User-Agent'] = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3452.0 Safari/537.36"
with open("cookies.txt", 'rb') as f:
    headers["Cookie"] = f.read().decode()

# def get_proxy():
#     ip = __redis.rpop("iptest")
#     __redis.lpush(ip, "iptest")
#     proxies = {
#         'http': ip,
#         'https': ip
#     }
#     return proxies

def pase_date(ts):
    timeArray = time.localtime(ts)
    otherStyleTime = time.strftime("%Y/%m/%d", timeArray)  # Keep the same style of excel setting
    return otherStyleTime

class Spider():
    base_url = 'https://weixin.sogou.com/weixin?type={}&s_from=input&query={}'
    session = Session()
    empt = 0

    def start(self):
        # 全局更新Headers，使得所有请求都能应用cookie
        self.session.headers.update(headers)
        # self.session.headers['User-Agent'] = random.choice(USER_AGENT)
        # print(self.session.headers['User-Agent'])

        print("爬取搜索页：", self.start_url)
        # proxies = get_proxy()
        # resp = self.session.get(self.start_url, proxies=proxies, verify=False)
        resp = self.session.get(self.start_url, verify=False)
        if 'com/antispider' in resp.url:
            self.update_cookies()
            self.start()
        else:
            self.parse_index(resp)

    def update_cookies(self):
        global headers
        while True:
            print("请输入验证码...并更新：cookies.txt")
            with open("cookies.txt", 'rb') as f:
                cookies = f.read().decode()
                if cookies and cookies != '' and cookies != headers["Cookie"]:
                    headers["Cookie"] = cookies            
                    self.session.headers.update(headers)
                    break
            time.sleep(10)
        print("cookie已更新")

    def parse_index(self, response):
        doc = pq(response.text)
        items = doc('.news-box .news-list li .txt-box').items()
        news = []
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
            if ts > START_TIME:
                
                date = pase_date(ts)
                data = {
                    'title': title,
                    'description': desp,
                    'account': account,
                    'date': date,
                    'url': url
                }
                news.append(data)
            
        for data in news:
            url = data["url"]
            title = data["title"]
            data["url"] = self.update_url(url)
            if not os.path.isfile(OLD_DATA_FILEPATH + hashlib.new('md5', title.encode(encoding='UTF-8')).hexdigest() + ".txt"):
                try:
                    fo = open(NEW_DATA_FILEPATH + hashlib.new('md5', title.encode(encoding='UTF-8')).hexdigest()+".txt", "w")
                    fo.write(json.dumps(data))
                    fo.close()
                    print("新增：{}".format(title))
                except:
                    # print(data)
                    print("写入失败")
            else:
                print("重复：{}".format(title))
            time.sleep(5)
         
        next_page = doc('#sogou_next').attr('href')
        if next_page:
            if not re.match('https://', next_page):
                next_page = self.base_url + next_page
            print("下一页：", next_page)
            if len(news) > 0:
                self.empt = 0
                self.start_url = next_page
                self.start()
            elif self.empt < 4:
                self.empt += 1
                self.start_url = next_page
                self.start()
    
    def update_url(self, url):
        # proxies = get_proxy()
        url += '&k=30&h=g'
        self.session.headers['Referer'] = self.base_url
        # self.session.headers['User-Agent'] = random.choice(USER_AGENT)
        resp = self.session.get(url, verify=False)
        # resp = self.session.get(url, proxies=proxies, verify=False)
        if 'com/antispider' in resp.url:
            self.update_cookies()
            return self.update_url(url)
        m = re.findall(r"url \+\= '(.*)';", resp.text)
        return "".join(m).replace("@", "")


if __name__ == '__main__':
 
    sp = Spider()
    with open("keywords.txt", 'rb') as f:
        env = f.read()
        i = 0
        for kw in env.decode().split('\n'):
            if "#" not in kw:
                i += 1
                print("爬取关键词：", kw)
                sp.keyword = kw
                # 设置页面跳过
                # if i == 1:
                #     #params['page'] = 10
                #     continue
                # elif i == 2:
                #     #params['page'] = 70
                #     continue
                # elif i == 3:
                #     params['page'] = 93
                # else:
                #     pass
                sp.start_url = sp.base_url.format(2, sp.keyword)
                sp.start()
                time.sleep(5)
