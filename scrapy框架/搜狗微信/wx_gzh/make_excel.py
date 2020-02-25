import os
import json
from xlutils.copy import copy
import xlwt, xlrd
import shutil
import time, datetime

OLD_DATA_FILEPATH = "./spiders/old_data/"
NEW_DATA_FILEPATH = "./spiders/new_data/"
# print(os.listdir(NEW_DATA_FILEPATH))
CURRENT_DATE = datetime.datetime.now()
FILENAME = '搜狗_{}-{}-{}已排重.xls'.format(str(CURRENT_DATE.year),str(CURRENT_DATE.month),str(CURRENT_DATE.day))

GZH_LIST = []
with open("wx-gzh_list.txt", 'r') as f: 
    GZH_LIST.append(f.read().replace("\t","").replace("\n","").strip()[:-1])


if __name__ == '__main__': 
    count = 0

    if os.path.isfile(FILENAME):
        workbook = xlrd.open_workbook(FILENAME, formatting_info=True)
        count = workbook.sheet_by_name(u"疫情数据").nrows
        workbook_ = copy(workbook)
        sheet = workbook_.get_sheet(0)
        for root, dirs, files in os.walk(NEW_DATA_FILEPATH):
            for file in files:
                # print(file)
                filename = NEW_DATA_FILEPATH + file
            
                if os.path.isfile(OLD_DATA_FILEPATH + file):
                    # print(os.path.isfile(OLD_DATA_FILEPATH + file))
                    os.remove(filename) 
                    continue
                with open(filename, 'rb') as f:
                    data = json.loads(f.read().decode())
                    # print(data)
                    sheet.write(count, 0, data["source"]) 
                    sheet.write(count, 1, data['title'])
                    sheet.write(count, 2, data['gzh'])
                    sheet.write(count, 3, data['public_time'])
                    sheet.write(count, 4, data['url'])
                    sheet.write(count, 5, data['summary'])
                    if data['gzh'] in GZH_LIST:
                        sheet.write(count, 6, 1)
                    else:
                        sheet.write(count, 6, 0)  
                    # TODO 2020/02/25-3:54: use NLP or other algorithm to selct better article 
                    f.close()

                count = count + 1
                shutil.move(filename, "OLD_DATA_FILEPATH") 
        workbook_.save(FILENAME)            
    else:
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet("疫情数据")
        sheet.write(count, 0, '来源') # row, column, value
        sheet.write(count, 1, '标题')
        sheet.write(count, 2, '公众号')
        sheet.write(count, 3, '发布时间')
        sheet.write(count, 4, '链接')
        sheet.write(count, 5, '摘要')
        sheet.write(count, 6, '重要性')
        count = count + 1

        for root, dirs, files in os.walk(NEW_DATA_FILEPATH):
            for file in files:
                # print(file)
                filename = NEW_DATA_FILEPATH + file
            
                if os.path.isfile(OLD_DATA_FILEPATH + file):
                    print(os.path.isfile(OLD_DATA_FILEPATH + file))
                    os.remove(filename) 
                    continue
                with open(filename, 'rb') as f:
                    data = json.loads(f.read().decode())
                    print(data)
                    sheet.write(count, 0, data["source"]) 
                    sheet.write(count, 1, data['title'])
                    sheet.write(count, 2, data['gzh'])
                    sheet.write(count, 3, data['public_time'])
                    sheet.write(count, 4, data['url'])
                    sheet.write(count, 5, data['summary'])
                    if data['gzh'] in GZH_LIST:
                        sheet.write(count, 6, 1)
                    else:
                        sheet.write(count, 6, 0)  
                    # TODO 2020/02/25-3:54: use NLP or other algorithm to selct better article 
                    f.close()

                count = count + 1
                shutil.move(filename, "OLD_DATA_FILEPATH")             
        workbook.save(FILENAME)


