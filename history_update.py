#coding='utf-8'
import json
import time
import os
import collections

os.chdir('/home/ubuntu/fenci/') 

tm=time.localtime()

filename='words'+'_'+str(tm[0])+'_'+str(tm[1])+'_'+str(tm[2])+'_'+str(tm[3])

with open('history.json','r') as f:
    history=json.loads(f.read())


with open(filename+'.json','r') as f:
    new=json.loads(f.read())


for each in history:
    del history[each][0]
    if each in new:
         history[each].append(new[each])
    else:
        history[each].append(0)

temp=sorted(history.iteritems(),key=lambda x:sum(x[1]),reverse=True)




history = collections.OrderedDict()

for each in temp:
    history[each[0]]=each[1]

with open('history.json','w') as f:
    f.write(json.dumps(history))

for each in history:
    print sum(history[each])
