import requests
from multiprocessing.dummy import Pool
import time
import re
import collections

def FastGetText(urls,thread=8):
    
    def get(url):
        try:
            r=requests.get(url,timeout=30)
            txt=r.text
            m=re.search(r'[ ;]charset=[\" ]?(.*?)"',txt)
            r.encoding=m.group(1)
            return r.text
        except Exception,e:
            txt=''
            return txt


    
    a=time.time()
    pool=Pool(thread)

    results=pool.map(get,urls)

    pool.close()
    pool.join()
    b=time.time()

    #print str(b-a)+'s'
    return results

def DictSort(dictionary,key,reverse=True):
    temp=sorted(dictionary.iteritems(),key,reverse)
    dictionary = collections.OrderedDict()

    for each in temp:
        dictionary[each[0]]=each[1]
        
    return dictionary
