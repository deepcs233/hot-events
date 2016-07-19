#encoding=utf-8
import re

class parser():
    def __init__(self,content=[]):
    	if isinstance(content,list):
    		self.content=content
        else:
        	self.content=[content]

    def __str__(self):
        return  '所含网页数量:'+str(len(self.content))

    @property
    def chinese(self):
    	result=[]
    	for each in self.content:
    		result+=re.findall(u"[\u4e00-\u9fa5]+",each)
    	return result

    
    @property
    def tag_a(self):
    	result=[]
    	for each in self.content:
    		t=re.findall(u"<a.*?>([^<>\n\r]{6,}?)</a>",each)
    		t=[x.strip() for x in t]
    		result+=t
    	return result



    @property
    def tag_h(self):
    	result=[]
    	for each in self.content:
    		t=re.findall(u"<h.*?>([^<>\n\r]+?)</h\d*>",each)
    		t=[x.strip() for x in t]
    		result+=t
    	return result


    @property
    def tag_p(self):
    	result=[]
    	for each in self.content:
    		t=re.findall(u"<p.*?>([^<>\n\r]+?)</p>",each)
    		t=[x.strip() for x in t]
    		result+=t
    	return result

