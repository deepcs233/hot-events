# -*- coding: utf-8 -*-
import requests
import jieba
import os
import re
import csv
import json
import time
import logging
import sys
from multiprocessing.dummy import Pool
import FastGet
import collections 


class fenci(object):
   
    def __init__(self,htmls=[],txt=0,csv=0,json=1,mysql=0,usernames='',mode='client',add_file_name=''):#0表示不以某种方式记录
        if len(htmls)==0:
            self.url=['http://www.sohu.com/','http://www.ifeng.com/',
                  'http://www.xinhuanet.com/','http://www.sina.com/',
                  'http://www.163.com.cn/','http://www.qq.com/',
                  'http://www.firefoxchina.cn/','http://www.people.com.cn/','http://www.cri.cn/'
                  ,'http://cn.chinadaily.com.cn/','http://www.china.com.cn/','http://www.ce.cn/'
                    ,'http://www.youth.cn/']
        self.url=htmls
        self.txt_written=txt
        self.csv_written=csv
        self.json_written=json
        self.mysql_written=mysql
        self.mode=mode #mysql记录模式(本地/远程主机)

        self.slist_100_dict={} #返回给网页的100个最热句子
        self.words_100_dict={} #返回给网页的100个最热词语
        #完全无意义的词语,过滤级别低
        self.filter_low=['如何','quot','$#','精装','这里','为何','什么','分钟','发生','这些','SUV','不是','这样','这么','搜狐','还是','可以','哪些','这个','...','凤凰网','秒杀','精装','不能','许可证']
        #有一定意义但是单词无意义的词语，过滤级别高
        self.filter_high=['gt','&#','最新','没有','喜欢','男子','城市','事件','时代','问题','发现','启动','进入','今年','公布','报告','加速','协议','故事','女儿','我们','个人','开始','遭遇','项目','亿元','要求','回应','全面','即将','对话','出席','会见','发布会','模式','均价','国际','影响','最高','揭秘','开幕','盘点','男人','开展','曝光','现场','推荐','首次','亮相','节目','举行','平台','关于','第一','大型','名单','产业','助力','真正','行业','成为','出现','聚焦','史上','一个','价格','严重']
        self.add_file_name=add_file_name
#日志记录
        logging.basicConfig(level=logging.DEBUG,
                format='<%(levelname)s>%(asctime)s %(filename)s[line:%(lineno)d]  %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='fenci.log',
                filemode='a')


    def getText(self):
             
        def getx(url):
            print 'get'+url
            try:
                r=requests.get(url,timeout=5)
                txt=r.text
                m=re.search(r'[ ;]charset=[\" ]?(.*?)"',txt)
                r.encoding=m.group(1)
                return r.text
            except Exception,e:
                print e


      
        a=time.time()
        pool=Pool(7)
    
        results=pool.map(getx,self.url)
        print len(results)
        pool.close()
        pool.join()
        b=time.time()

        print str(b-a)+'s'

        text=''.join(x for x in results if x is not None)
        print len(text)
        return text

           
    def extract(self,text): #提取
        a=time.time()
        #p=re.findall(r'(?:_blank|html?)">(?!<)([^<>\'\"]{5,30}?)</a>',text)#滤去过长或过短的语句
        p=re.findall(r'href="([^\"\'<>\[\]]*?html?)(?:.*?_blank)?">(?!<)([^<>\'\"]{6,30}?)</a>',text)
        sent_html=p
        slist=[]
        for each in p:
            slist.append(each[1])
        b=time.time()
        print b-a
        print 'sent_html',len(sent_html)
        return sent_html

    def analyse_w(self,sent_html):#sentence list #计算新闻热度，并生成slist_q
        words={}
        #fp=open('words.json','r')
        #words=json.dumps(fp.read())
        for each in sent_html:
            for i in jieba.cut(each[1]):
                if len(i)>1 and i.encode('utf-8') not in self.filter_low:
                    if i in words:
                        words[i]+=1
                    else:
                        words[i]=1
        return words

    def analyse_s(self,words,sent_html):
        slist_q={}
        i=0
        for each in sent_html:
            
            slist_q[each[1]]=[sent_html[i][0],0]
            for one in words:
                if one in each[1]:
                    slist_q[each[1]][1]+=words[one]
            i+=1
        return slist_q              # {content:[html,hot]}
        
    def filtrate(self,words,slist_q):
        a=time.time()
        #slist_q  ------->  {content:[html,hot]}
        
        #以下部分为语句的重复性检查，仍存在一定问题 如 中国法治白皮书 与 中国环境白皮书 会被误判
            #排序
        s=sorted(slist_q.iteritems(),key=lambda x:x[1][1],reverse=True)#s=[('as',[]),('sd',[])]形式
                

        for i in xrange(len(s)-10):
            
            for j in xrange(1,8,1):
               
                if self.repeatability(s[i][0],s[i+j][0]) and s[i][1][1]>0 and s[i+j][1][1]>0:
                    
                    if(len(s[i][0])>s[i+j][0]):#删除较短的
                       s[i+j]=(s[i+j][0],[s[i+j][1][0],-1])#hot=-1的即为等待删除的句子
                    else:
                        s[i]=(s[i][0],[s[i][1][0],-1])

                        
        num=0 #计数 取前一百个
        for each in s:
            if each[1][1]>0 and num <100 :#hot<0 即为等待被删除
                self.slist_100_dict[each[0]]=each[1]
                num+=1
                
        slist_q=s
        
        #------------------------------------------
        
        w=sorted(words.iteritems(),key=lambda x:x[1],reverse=True)
 
        num=0
        for each in w:
            if num<100:
                if len(re.findall(r'^\d*$',each[0]))==0:
                    if each[0].encode('utf-8') not in self.filter_high:
                       # print each[0]
                        self.words_100_dict[each[0]]=each[1]
                        num+=1
        #for each in  self.words_100_dict:
           # print each ,self.words_100_dict[each]
        b=time.time()
        print a-b
        return slist_q
    
  #将前100热度的词语和新闻进行从大到小的排序
    
    def sort(self):
        temp=sorted(self.slist_100_dict.iteritems(),key=lambda x:x[1][1],reverse=True)
        self.slist_100_dict = collections.OrderedDict()

        for each in temp:
            self.slist_100_dict[each[0]]=each[1]

        temp=sorted( self.words_100_dict.iteritems(),key=lambda x:x[1],reverse=True)
        self.words_100_dict = collections.OrderedDict()

        for each in temp:
             self.words_100_dict[each[0]]=each[1]

    def output(self,sent_html,words): 
        for each in sent_html:
            print (each[1])
            
        for i in words:
            if words[i]>1:
                print i ,words[i]


    def save2json (self,slist_q,words):

        tm=time.localtime()
        #>>> time.localtime()
        #time.struct_time(tm_year=2016, tm_mon=6, tm_mday=13, tm_hour=21, tm_min=5, tm_sec=28, tm_wday=0, tm_yday=165, tm_isdst=0)
        
        days=int(time.time()/(3600*12)-33988)+61
        with open('words_'+str(days)+'.json','w') as f:#此系列json用于后来分析tf-idf，每天两次，并用于历史趋势的分析
            f.write(json.dumps(words))

        with open('words'+'_'+str(tm[0])+'_'+str(tm[1])+'_'+str(tm[2])+'_'+str(tm[3])+'.json','w') as f:#用于保存平时记录（each hour）
            f.write(json.dumps(words))
                       
        with open('sentences.json','w') as f:
            f.write(json.dumps(str(slist_q)))

        with open('sentences_100'+'_'+str(tm[0])+'_'+str(tm[1])+'_'+str(tm[2])+'_'+str(tm[3])+'.json','w') as f:
            f.write(json.dumps(self.slist_100_dict))

        with open('words_100'+'_'+str(tm[0])+'_'+str(tm[1])+'_'+str(tm[2])+'_'+str(tm[3])+'.json','w') as f:
            f.write(json.dumps(self.words_100_dict))
        
    def save2csv (self,slist_q,words):
        
        writer=csv.writer(file('data_sentences.csv','w'))
        writer.writerow(['content','hot'])
        for each in slist_q:
            writer.writerow([each.encode('utf-8'),str(slist_q[each])])
            
        writer=csv.writer(file('data_words.csv','w'))
        writer.writerow(['content','frequency'])
        for each in words:
            writer.writerow([each.encode('utf-8'),str(words[each])])
            
    def save2txt (self,slist_q,words):
        with open("sentences.txt","w") as f:
            for each in slist_q:
                f.write(each.encode('utf-8'))
                f.write('   ')
                f.write(str(slist_q[each]))
                f.write("\n")
                
        with open("words.txt","w") as f:     
            for i in words:
                if words[i]>1:
                        f.write(i.encode('utf-8'))
                        f.write(str(words[i]))
                        f.write("\n")
                        
    def save2mysql_client(self,slist_q,words):
        import mysql.connector
        

        try:
            cnx = mysql.connector.connect(user=self.db_user, password=self.db_password, host=self.db_host,database=self.db_database)

        except Exception,e :
            print e
            logging.error(e)
            return

        try:
            cur = cnx.cursor(buffered=True)
            cur.execute("SELECT * from "+ self.db_table_1)
                
            if cur.fetchone() :
                
                cur.execute("TRUNCATE TABLE "+ self.db_table_1)
                cur.execute("TRUNCATE TABLE "+ self.db_table_1)#自动清空数据库
            print len(slist_q)
            
            for i in range(len(slist_q)):

                if slist_q[i][1][1]>0:#hot=-1的即为等待删除的句子
                    try:
                        cur.execute("INSERT INTO "+ self.db_table_1+" VALUES"
                                +"("+"NULL"+","+"'"+slist_q[i][0]+"'"+","+str(slist_q[i][1][1])+","+"'"+slist_q[i][1][0].strip()+"'"+","+"'"+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+"'"+")"
                                    )
                    except:
                        cur.execute("INSERT INTO "+ self.db_table_1+" VALUES"
                                +"("+"NULL"+","+"'"+slist_q[i][0]+"'"+","+str(slist_q[i][1][1])+","+"NULL"+","+"'"+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+"'"+")"
                                    )    
     


            for each in words:
                cur.execute("INSERT INTO "+ self.db_table_2+" VALUES"
                            +"("+"NULL"+","+"'"+each+"'"+","+str(words[each])+","+"'"+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+"'"+")"
                                )
                
        except Exception,e :
            print e
            logging.error(e)

        
        cur.close()
        cnx.commit()
        cnx.close()
                            
    def save2mysql_server(self,slist_q,words):
        print 'import ok'
        import MySQLdb        

        #try:
        print self.db_database
        cnx = MySQLdb.connect(user=self.db_user , passwd=self.db_password , host=self.db_host , db=self.db_database)#'115.159.185.126'
        #except Exception,e :
        #print e
        #logging.error(e)
        #return


        try:
            print 'connect ok'
            cur = cnx.cursor()
            cnx.set_character_set('utf8')
            cur.execute('SET NAMES utf8;')
            cur.execute('SET CHARACTER SET utf8;')
            cur.execute('SET character_set_connection=utf8;')
            cur.execute("SELECT * from "+ self.db_table_1)
        
            if cur.fetchone() :
                
                cur.execute("TRUNCATE TABLE "+ self.db_table_1)
                cur.execute("TRUNCATE TABLE "+ self.db_table_1)#自动清空数据库

            for i in xrange(len(slist_q)):
                if slist_q[i][1][1]>0:#hot=-1的即为等待删除的句子
                    try:
                        cur.execute("INSERT INTO "+ self.db_table_1+" VALUES"
                                +"("+"NULL"+","+"'"+slist_q[i][0]+"'"+","+str(slist_q[i][1][1]).encode('utf-8')+","+"'"+slist_q[i][1][0].strip()+"'"+","+"'"+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+"'"+")"
                                    )
                    except:
                        cur.execute("INSERT INTO "+ self.db_table_1+" VALUES"
                                +"("+"NULL"+","+"'"+slist_q[i][0]+"'"+","+str(slist_q[i][1][1]).encode('utf-8').decode('latin-1')+","+"NULL"+","+"'"+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+"'"+")"
                                    )    
     

                
            for each in words:
                cur.execute("INSERT INTO "+ self.db_table_2+" VALUES"
                            +"("+"NULL"+","+"'"+each+"'"+","+str(words[each]).encode('utf-8').decode('latin-1')+","+"'"+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+"'"+")"
                                )
        except Exception,e:
            print e
            logging.error(e)

        finally:    
            cur.close()
            cnx.commit()
            cnx.close()
    def SetDatabase(self,user='root',password='',host='127.0.0.1',database='data',table_1='sentences',table_2='words'):
        self.db_user=user
        self.db_password=password
        self.db_host=host
        self.db_database=database
        self.db_table_1=table_1
        self.db_table_2=table_2
        
    def repeatability(self ,str_1,str_2): #判断语句是否重复，是则返回1
        list_1=jieba.cut(str_1)
        list_2=jieba.cut(str_2)
        
        a=list(list_1)
        b=list(list_2)

        count_a=count_b=0
        
        for i in a:
            for j in b:
                if i==j :
                    count_a+=1
                    break

        for j in b:
            for i in a:
                if i==j :
                    count_b+=1
                    break

        if  float(count_a)/len(a)>0.78 or float(count_b)/len(b)>0.78:
            return 1
        else:
            return 0
        
    def start(self):
        time_start=time.time()
        text=self.getText()


        sent_html=self.extract(text)
        ccc=time.time()
        print ccc-time_start
        words=self.analyse_w(sent_html)
 #slist_q:{content:[html,hot]}
        slist_q=self.analyse_s(words,sent_html)
        
        slist_q=self.filtrate(words,slist_q)
        self.sort()
        os.chdir('/var/www/html/fenci/')
        if self.txt_written:
            self.save2txt(slist_q,words)
        if self.csv_written:
            self.save2csv(slist_q,words)
        if self.json_written:
            self.save2json(slist_q,words)
            
        if self.mysql_written:
            if self.mode=='client':
                self.SetDatabase(user='root', password='1997211', host='127.0.0.1',database='sakila',table_1='sentences',table_2='words')
                self.save2mysql_client(slist_q,words)
            if self.mode=='server':
                self.SetDatabase(user='root', password='222293', host='127.0.0.1',database='data',table_1='sentences',table_2='words')
                self.save2mysql_server(slist_q,words)
          
        #self.save2mysql_client(slist_q,words)
        #self.output(sent_html,words)
        time_end=time.time()
        print 'All time cost is '+str(time_end-time_start)+'s'


if __name__=='__main__':
    os.chdir('/home/ubuntu/fenci/') 
    default=['http://www.sohu.com/','http://www.ifeng.com/',
                  'http://www.xinhuanet.com/','http://www.sina.com/',
                  'http://www.163.com.cn/','http://www.qq.com/',
                  'http://www.firefoxchina.cn/','http://www.people.com.cn/','http://www.cri.cn/'
                  ,'http://cn.chinadaily.com.cn/','http://www.china.com.cn/'
                  ,'http://www.ce.cn/','http://www.youth.cn/']
    s=fenci(htmls=default,mysql=1,json=1,mode='server')
    s.start()


#tf-idf
#sentences加入对应网址
#中国屏蔽？
#上升最快
#文件命名，数据库命名问题,given 所返回的json命名问题
#\\\\反斜杠！
