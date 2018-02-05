# encoding:utf-8
import requests  # 导入requests模块用于访问测试自己的ip
from bs4 import BeautifulSoup as bs
import random
import re
import time
def ip_poor():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    url = 'http://www.xdaili.cn/ipagent//freeip/getFreeIps?page=1&rows=10'  # 你用于测试自己ip的网站

    response=requests.get(url,headers=headers)
    response.encoding='utf-8'
    pattern_ip = re.compile(r'"ip":"(.*?)"')
    pattern_port = re.compile(r'"port":"(.*?)"')
    ip = pattern_ip.findall(str(response.text))
    port=pattern_port.findall(str(response.text))
    result=[]
    for i in range(len(ip)):
        result.append(ip[i]+':'+port[i])
    return result

if __name__ == '__main__':
    ip_poor()