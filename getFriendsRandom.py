import requests
import json
import pymongo
import time

# 第几页开始, 0表示第一页
Since_id = 0
# 第几页结束/循环几次, 包括本身
MaxSince = 999
# 间隔多久发一次请求 单位:秒
Sleep_time = 30
# 爬取模式 1分页爬取 2时间段同步
Get_type = 2

# mongo配置.db.集合 (需在mongo自行创建id作为唯一索引)
Collection = pymongo.MongoClient("localhost", 27017).weibo.cxk
# 文件
F = open('./log.log', 'a', encoding="utf=8")
# 每个请求跳页 (修改Base_url的fans_-_地址可以忽略该值,默认1即可)
Jump_count = 1
# 总获取 - 不需要修改
Totle_count = 0

# fans_-_  参数可以获取当天, 进行实时随机粉丝,效果可以获取更多的粉丝 _2438867634
# 详情打开 https://m.weibo.cn/p/index?containerid=2310512_-_fans_-_1776448504  获取
Base_url = "https://m.weibo.cn/api/container/getIndex?containerid=2310512_-_fans_-_1776448504"
Headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36',
    "content-type": "application/json; charset=utf-8",
}


def getFans(since_id_count):

    global Base_url
    global Headers
    global Totle_count
    global Sleep_time
    global Collection
    global Jump_count
    global Get_type
    global F

    if Get_type == 1:
        response = requests.get(
            url=Base_url+'&since_id=' + str(since_id_count), headers=Headers)
    else:
        response = requests.get(url=Base_url, headers=Headers)

    content = response.text
    dictionary_content = json.loads(content)
    try:
        fans_card = dictionary_content['data']['cards'][-1]
    except:
        fans_card = {"card_group": []}
        print("当前返回的List数据为空", file=F)

    card_group = fans_card['card_group']
    for i, user_item in enumerate(card_group):
        card_group[i] = user_item['user']
        print(user_item['user']['id'], file=F)

    Totle_count += len(card_group)

    if dictionary_content['ok'] == 1:
        try:
            Collection.insert_many(card_group, ordered=False)
        except:
            print("出现唯一索引重复问题: 已忽略", file=F)

        print("总获取:", Totle_count, file=F)
        print("第几次获取成功:", since_id_count+1, file=F)
        print("第几次获取成功:", since_id_count+1, "还有几次:", MaxSince-since_id_count)

    if since_id_count < MaxSince:
        time.sleep(Sleep_time)
        getFans(since_id_count + Jump_count)
    else:
        print("已结束", time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime()), file=F)
        print("==========", file=F)
        F.close()


if __name__ == "__main__":
    getFans(Since_id)
