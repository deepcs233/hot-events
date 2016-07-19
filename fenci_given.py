# -*- coding: utf-8 -*-
import requests
import re
import json
import time
import logging
import sys
import FastGet
import html_parser
import jieba



class BFS():

    def __init__(self,html='',maxtime=20,deepth=100):
        try:
    #mainhost:eg. xinhua
            self.mainhost=re.findall(r'https?://(?:www.)?(.*)\.(?:com|cn|edu|net).*',html)[0]
            
    #host:eg.http://www.fishc.com/html/       
            self.host=re.findall(r'(https?://.*?)(?:/|$)',html)[0]+'/'
            
            #print 'host:',self.host
        except:
            print'输入的网址非法！'
            return
        self.end_time=maxtime+time.time()
        self.will_processe_html=[html]
        self.processed_html=[]
        self.deepth=deepth
        self.content=[]
        

    def html_process(self,html):#获得前缀
        html=html.strip()
        
        if html.endswith('com') or html.endswith('cn') or html.endswith('net') or html.endswith('edu'):
            html+='/'
            
        if html.endswith('html/') or html.endswith('htm/'):
            html=html[0:-1]

       
        t=html.split('/')
        if t[-1] !='':
            del t[-1]
        if t[-1] !='':    
            t.append('')
        result='/'.join(t)

        return  result


    def get_html(self,text,url):#重点处理相对地址

        def f(text,url):
            
          
            htmls=re.findall(r'href=(?:\"|\')([^\"\'<>#]html*?)(?:\"|\').*?>(?!<)(?:[^<>\'\"]+?)</a>',text)#强模式，仅匹配html

            #若强模式下无法匹配到链接，则起用弱模式
            if len(htmls)==0:
                htmls=re.findall(r'href=(?:\"|\')([^\"\'<>#]*?)(?:\"|\').*?>(?!<)(?:[^<>\'\"]+?)</a>',text)#弱模式，匹配所有href
            
            

            prefix=self.html_process(url)
            #print 'prefix:',prefix
            result=[]
            for html in htmls:
                if 'http://' not in html:
                    if '/' not in html[1:]:
                        if html.startswith('/'):
                            result.append(prefix+html[1:])
                        else:
                            result.append(prefix+html)
                    else:
                        if html.startswith('/'):
                            result.append(self.host+html[1:])
                        else:
                            result.append(self.host+html)

                else:
                    result.append(html)
                    
            #逐个检查网址是否已经记录过
            result=[x for x in result if x not in self.processed_html]
            result=[x for x in result if self.mainhost in x ]
            return result
        
        #多态
        result=[]

        if  isinstance(text,str):
            result=f(text,url)

        else:
            for i in range(len(text)):
                result+=f(text[i],url[i])
                #print result     
        return result
    

    def download(self,html):
        try:
            r=requests.get(html,timeout=3)
            m=re.search(r'[ ;]charset=[\" ]?(.*?)"',r.text)
            r.encoding=m.group(1)
            text=r.text
            #print text
        except Exception,e:
            print e
            text=''

        return text
#单线程版本
    def run(self):
        tag=1
        numOfProcessed=0
        
        while self.deepth>0 and time.time() < self.end_time+10000 and len(self.will_processe_html)>0:
            
            #self.deepth-=1
            pop_html=self.will_processe_html.pop(0)
            text=self.download(pop_html)
            self.will_processe_html+=self.get_html(text,pop_html)
            print len(self.will_processe_html)
            print pop_html ,'OK'
            self.processed_html.append(pop_html)
            numOfProcessed+=1
            if tag<=numOfProcessed:
                tag+=numOfProcessed
                self.deepth-=1
            self.content.append(text)
            print numOfProcessed
            

#多线程版本,计算层数时可能会产生误差(<=12)
    #tag 用于记录最新层所对应的最大的网页编号
    def mult_run(self):
        tag=1
        numOfProcessed=0
        htmls_in_each_deepth=[] #
        while time.time() < self.end_time and len(self.will_processe_html)>0 and self.deepth>0:
            
            if len(self.will_processe_html)<12:
                pop_htmls=self.will_processe_html
                self.will_processe_html=[]
            else:
                pop_htmls=self.will_processe_html[0:12] #取前十二个
                self.will_processe_html[0:12]=''
           
            texts=FastGet.FastGetText(pop_htmls,thread=6)
            
            self.will_processe_html+=self.get_html(texts,pop_htmls)
            
            
            print '处于队列中的网页数量:',len(self.will_processe_html)
            print '正在处理：',pop_htmls ,'OK'
            
            self.processed_html+=pop_htmls
            numOfProcessed+=len(pop_htmls)
            self.content+=texts
            if tag<=numOfProcessed:
                tag+=numOfProcessed
                self.deepth-=1
                
            print '已处理网页数量:',numOfProcessed
            print  '=================================================================='
            
def fenci(textlist):
    words={}
    filter_low=['如何','quot','$#','精装','这里','为何','什么','分钟','发生','这些','SUV','不是','这样','这么','搜狐','还是','可以','哪些','这个','...','凤凰网','秒杀','精装','不能','许可证']
    for each in textlist:
        for i in jieba.cut(each):
            if len(i)>1 and i.encode('utf-8') not in filter_low:
                if i in words:
                    words[i]+=1
                else:
                    words[i]=1
    return words

def sen_freq(textlist,words):
    slist_q={}
    for each in textlist:
        
        slist_q[each]=0
        for one in words:
            if one in each:
                slist_q[each]+=words[one]
    return slist_q
        
if __name__ =='__main__':
    #c=BFS('https://www.zhihu.com/question/48492621')
    c=BFS('http://www.jb51.net/article/58457.htm')
    #c=BFS('http://www.ziqiangxuetang.com/html/html-tutorial.html')
    #text=c.download('http://www.ziqiangxuetang.com/html/html-images.html')
    #pl=c.get_html(text,'http://www.ziqiangxuetang.com/html/html-images.html')
    #for each in pl:
    #    print each
    c.mult_run()

    p=html_parser.parser(c.content)

    words=fenci(p.chinese)
    num=0
    for each in p.chinese:
        num+=len(each)
    print num
    slist_q=sen_freq(p.tag_a,words)

    for each in slist_q:
        print each,slist_q[each]
