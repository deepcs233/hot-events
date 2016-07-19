import json
import mysql.connector
import math
total=0
words={}
for i in xrange(1,61,1):
    print i
    filename='words_'+str(i)+'.json'
    with open(filename,'r') as f:
        text=f.read()

    
    temp=json.loads(text)
    for each in temp:
        if each not in words:
            words[each]=temp[each]
        else:
            words[each]+=temp[each]
        total+=words[each]
total+=300000

print total,len(words)

with open('stats.json','w') as f:
    f.write(json.dumps(words))

stat={}

for each in words:
    freq=words[each]
    if freq in stat:
        stat[freq]+=1
    else:
        stat[freq]=1

stata=sorted(stat.iteritems(),key=lambda x: x[1],reverse=True)
        
for each in stata:
    print each[0],each[1]
    

for each in words:
    words[each]=-math.log(float(words[each])/total,10)#,math.e)

with open('result.json','w') as f:
    f.write(json.dumps(words))


words=sorted(words.iteritems(),key=lambda x:x[1],reverse=False)

for each in words:
    print each[0],each[1]

