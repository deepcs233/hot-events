#coding=utf-8

import json
import re

filter_high=['最新','没有','喜欢','男子','gt','&#','城市','事件','时代','问题','发现','启动','进入','今年','公布','报告','加速','协议','故事','女儿','我们','个人','开始','遭遇','项目','亿元','要求','回应','全面','即将','对话','出席','会见','发布会','模式','均价','国际','影响','最高','揭秘','开幕','盘点','男人','开展','曝光','现场','推荐','首次','亮相','节目','举行','平台','关于','第一','大型','名单','产业','助力','真正','行业','成为','出现','聚焦','史上','一个','价格','严重']
max_500={}
with open ('stats.json','r') as f:
    text=f.read()

temp=json.loads(text)

s=sorted(temp.iteritems(),key=lambda x:x[1],reverse=True)

num=0

for i in xrange(500):
    if len(re.findall(r'^\d*$',s[i][0]))==0:
        if s[i][0].encode('utf-8') not in filter_high:
            print i
            max_500[s[i][0]]=s[i][1]

for each in max_500:
    print each,max_500[each]
    
with open('words_max_500.json','w') as f:
    f.write(json.dumps(max_500))
            
