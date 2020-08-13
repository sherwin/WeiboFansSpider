import requests
import json
import pymongo
import time
import random
import sys
import os
import string

# 间隔多久发一次请求 单位:秒
Sleep_time = 0
# mongo配置.db.集合 (需在mongo自行创建id作为唯一索引)
Collection = pymongo.MongoClient("localhost", 27017).weibo.cxk
# 文件
F = open('./noneUserInfo.list', 'a', encoding="utf-8")
# 单前轮询下标
Polling_index = 0
# 用户列表
User_id_list = []
# 代理列表配置
Ip_list = [
    "127.0.0.1:9999",
]
#
Weibo_account_index = 0
# 微博小号列表 - 在cookie内截取 SUB=_xxx; 表示登录凭证
Weibo_account = [
    "SUB=_2A12yJMXkDeRhGeFK41YT8ybFyzmIHXVR5uusrDV6PUJbkdANLWX2kW1NQvUbm2Jlf_U1U3b3pJpXds9ucZ40P6Yb;",
]
# 正在使用代理下标
Proxies_index = 0
# 思路
# 先获取用户信息
# 在获取注册时间/地区/生日等等
# url加&containerid= 作为取注册时间/地区/生日
Base_url = "https://m.weibo.cn/api/container/getIndex?uid={0}&type=uid&value={1}"
Headers = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.41.89 Mobile Safari/537.32",
}


def printLog(*args):
    global F
    print(*args)
    print(*args, file=F)


def getUserInfo():

    global Base_url
    global Headers
    global Collection
    global Polling_index
    global User_id_list
    global Ip_list
    global Proxies_index
    global Weibo_account
    global Weibo_account_index

    proxies = {"https": Ip_list[Proxies_index]}
    cookie = {"cookie": Weibo_account[Weibo_account_index]}
    cookie.update(Headers)

    userid = User_id_list[Polling_index]
    insert_userinfo = {}
    base_url = Base_url.format(userid, userid)

    # printLog("+=====================", proxies)
    response = requests.get(url=base_url + "&code=" + random.choice(
        string.ascii_letters), headers=Headers, proxies=proxies)
    content = response.text
    try:
        dictionary_content = json.loads(content)
        pass
    except:
        printLog("出现json解析错误", response.text)
        time.sleep(4)
        return getUserInfo()

    try:
        printLog('user', dictionary_content['ok'], dictionary_content['msg'])
        pass
    except:
        printLog('user', dictionary_content['ok'])
        pass
    # printLog("=======================",dictionary_content)
    if dictionary_content['ok'] == 1:
        # 获取用户信息
        dict_userinfo = dictionary_content['data']['userInfo']
        try:
            containerid = dictionary_content['data']['tabsInfo']['tabs'][0]['containerid']
        except:
            printLog("出现内容缺失")
            return

        insert_userinfo['containerid'] = containerid
        insert_userinfo["id"] = dict_userinfo["id"]
        insert_userinfo["screen_name"] = dict_userinfo["screen_name"]
        insert_userinfo["profile_image_url"] = dict_userinfo["profile_image_url"]
        insert_userinfo["profile_url"] = dict_userinfo["profile_url"]
        insert_userinfo["statuses_count"] = dict_userinfo["statuses_count"]
        insert_userinfo["verified"] = dict_userinfo["verified"]
        insert_userinfo["verified_type"] = dict_userinfo["verified_type"]
        insert_userinfo["close_blue_v"] = dict_userinfo["close_blue_v"]
        insert_userinfo["description"] = dict_userinfo["description"]
        insert_userinfo["gender"] = dict_userinfo["gender"]
        insert_userinfo["mbtype"] = dict_userinfo["mbtype"]
        insert_userinfo["urank"] = dict_userinfo["urank"]
        insert_userinfo["mbrank"] = dict_userinfo["mbrank"]
        insert_userinfo["follow_me"] = dict_userinfo["follow_me"]
        insert_userinfo["following"] = dict_userinfo["following"]
        insert_userinfo["followers_count"] = dict_userinfo["followers_count"]
        insert_userinfo["follow_count"] = dict_userinfo["follow_count"]
        insert_userinfo["cover_image_phone"] = dict_userinfo["cover_image_phone"]
        insert_userinfo["avatar_hd"] = dict_userinfo["avatar_hd"]

        account_response = requests.get(
            url=base_url + '&containerid=' + str(containerid) + "&code=" + random.choice(string.ascii_letters), headers=cookie, proxies=proxies)
        account_content = account_response.text
        try:
            account_dictionary_content = json.loads(account_content)
            pass
        except:
            printLog("出现json解析错误2", account_content)
            time.sleep(4)
            return getUserInfo()

        # printLog("========", account_dictionary_content)
        try:
            printLog('account', account_dictionary_content['ok'])
            pass
        except:
            printLog('account', account_dictionary_content['ok'])
            pass

        if account_dictionary_content['ok'] == 1:
            # printLog("----", account_dictionary_content)
            # 第一个(0)是空的
            try:
                account_cards1 = account_dictionary_content['data']['cards'][1]['card_group']
                account_cards2 = account_dictionary_content['data']['cards'][2]['card_group']
            except:
                printLog("出现内容缺失2")
                return
            account_cards_merge = account_cards1 + account_cards2
            # printLog(account_cards_merge)

            for i, info_card in enumerate(account_cards_merge):
                if('item_name' in info_card.keys()) and info_card['item_name'] == '注册时间':
                    insert_userinfo["registration_time"] = info_card['item_content']

            if dictionary_content['ok'] == 1:
                try:
                    Collection.update_one({"id": int(userid)}, {
                                          "$set": insert_userinfo})
                    printLog("完成:", userid)
                except Exception as eror:
                    printLog("error.......", eror)
        else:
            printLog("出现调用频繁2")
            time.sleep(1)
            Polling_index -= 1
            Weibo_account_index = random.randint(0, len(Weibo_account)-1)
            printLog("已自动更换小号:", Weibo_account_index, Weibo_account[Weibo_account_index])
    else:
        printLog("出现调用频繁1")
        # time.sleep(10)
        # Polling_index -= 1
        Proxies_index = random.randint(0, len(Ip_list)-1)
        Weibo_account_index = random.randint(0, len(Weibo_account)-1)
        printLog("已自动更换ip/小号:", Proxies_index, Ip_list[Proxies_index])


def init():
    global Polling_index
    global Sleep_time
    global User_id_list

    f = open('./noneUserInfo11.list', 'r', encoding='utf8')
    content = f.read().split('\n')
    for i, item in enumerate(list(set(content))):
        try:
            User_id_list.append(int(item))
        except:
            pass
    pass
    for i in range(len(User_id_list) - Polling_index):
        if Polling_index <= len(User_id_list):
            time.sleep(Sleep_time)
            Polling_index += 1
            printLog('开始:', Polling_index, '/', len(User_id_list), User_id_list[Polling_index])
            getUserInfo()
        else:
            printLog("已结束", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
            printLog("==========")
            F.close()
        pass


if __name__ == "__main__":
    init()
