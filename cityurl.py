# -*- coding:utf-8 -*-
from bs4 import BeautifulSoup as bs
import requests
import re

global first_url
first_url='http://www.dianping.com/citylist'
headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36'
    }
def parse_city_url(url):
    global city_dic
    response=requests.get(url,headers=headers)
    soup=bs(response.content,'lxml')
    data_city=soup.find_all(class_ = 'findHeight')
    city_url=[]
    city_dic={}
    for i in data_city:
        pattern = re.compile(r'<a class="link onecity" href="//(.*?)">(.*?)</a>')
        city_url.append(pattern.findall(str(i)))
    for j in city_url:
        for k in j:
            city_dic['%s'%k[1]]='%s'%k[0]
    print(city_dic)
    return(city_dic)

if __name__ == '__main__':
    parse_city_url(first_url)
    
