# 爬取微博粉丝/粉丝用户资料

- 仓库不能直接使用, 不建议clone直接run, 可参考思路/解决方案

- 爬取数据存至mongodb(v4.0.9)
- 因为微博接口限制,只能爬取5000粉丝, 但有解决思路,代码中的getFriendsRandom.py,每次获取可以多获取百个/几百个. 定时刷新频率建议在10s以上
- 请求频率限制原因, 加入代理列表自动切换, 需要自己调
- 爬取粉丝时候, 粉丝信息不完整, 需要再次每个粉丝获取个人信息, 出现checkNoneUserInfo.py 解决方案
- 检测数据库数据是否有不完整数据(可能原因,服务器没返回,获取失败)

![mongodb.png](https://github.com/sherwin/WeiboFansSpider/blob/master/mongodb.png "mongodb")