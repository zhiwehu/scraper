# -*- coding: utf-8 -*-
from contextlib import closing
import urllib2
import re
from bs4 import BeautifulSoup

def scrap_facebook_raw_data(url):
    data = {'likes': 0, 'talking_about_count': 0, 'checkins': 0}
    number_pat = "[0-9]+"
    stat_pat ='<div class="fsm fwn fcg">([0-9]+)(.*)([0-9]+)(.*)([0-9]+)(.*)\w+</div>'
    with closing(urllib2.urlopen(url)) as page:
        content = page.read()
        content= re.sub(',', '', content)
        result = re.search(stat_pat, content)
        if result:
            #print result.group()
            result = re.findall(number_pat, result.group())
            if len(result)>=3:
                data['likes']=result[0]
                data['talking_about_count']=result[1]
                data['checkins']=result[2]
                return data
            elif len(result)>=2:
                data['likes']=result[0]
                data['talking_about_count']=result[1]
                return data

def get_stat_numbers(str):
    str= re.sub(',', '', str)
    num_pat="[0-9]+"
    print str
    result = re.findall(num_pat, str)
    if len(result)==3:
        return tuple(result)
    else:
        return None



if __name__ == '__main__':
    print scrap_facebook_raw_data("http://www.facebook.com/applebees")
    print scrap_facebook_raw_data("http://www.facebook.com/wendys")
    print scrap_facebook_raw_data("http://www.facebook.com/PizzaHut")
    #get_stat_numbers("2,798,030 likes · 100,398 talking about this · 1,288,102 were here")
    pass