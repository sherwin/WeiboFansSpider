import pymongo

F = open('./noneUserInfo11.list', 'a', encoding="utf=8")
client = pymongo.MongoClient(host='localhost', port=27017)
cxk = client.weibo.cxk
queryArgs = {"gender": None}
projectionFields = {'id': True}
searchRes = cxk.find(queryArgs, projection=projectionFields)

for i,item in enumerate(list(searchRes)):
    print(item['id'],file=F)

print("剩余:", len(list(searchRes)))
