# -*- coding:utf-8 -*-
from bs4 import BeautifulSoup as bs
import requests
import re
url='http://www.dianping.com/'
headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36'
    }

response=requests.get(url,headers=headers)
soup=bs(response.content,'lxml')
data_comment=soup.select('.review-words')
print(soup)