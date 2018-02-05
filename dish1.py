# -*- coding:utf-8 -*-
from bs4 import BeautifulSoup as bs
import requests
import re
import pymysql
import cityurl
import multiprocessing
import time
import daili
import random
url = 'http://www.dianping.com/ciytlist'  #乐平美食初始页面
global headers 
headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'
    }

def parse_dish_code(url):
    response = requests.get(url,headers = headers)
    print(response.status_code)
    soup = bs(response.content,'lxml')
    text = soup.find_all(class_ = 'nc-contain')
    pattern = re.compile(r'data-cat-id="(.*?)" data-click-name="select_cate_(.*?)_click"')  #group(1)为菜系代码，group(2)为菜系
    global code 
    code= {}
    for m in pattern.finditer(str(text)):      
        code[m.group(1)] = m.group(2)
    return(code)
def parse_page_numeber(url):
    response = requests.get(url,proxies = proxies,headers = headers)
    print(response.status_code)
    soup = bs(response.content,'lxml')
    data = soup.select('.PageLink')
    if data:
        page = []
        for i in data:
            page.append(i.get_text())
    else:
        page = [1]
    return (page[-1])
def parse_one_page(url,page_number):
    response =  requests.get(url+'p'+str(page_number),proxies = proxies,headers = headers)
    print(response.status_code)
    soup = bs(response.content,'lxml')
    #爬取单面所有餐馆的名称
    data_res = soup.select('.tit h4')
    res_name = []        #单面所有餐馆名称
    for i in data_res:
        res_name.append(str(i).lstrip('<h4>').rstrip('</h4>'))
    #print(res_name)
    #爬取单面所有餐馆的人均价格
    price = []           #单面所有餐馆的人均价格
    data_price = soup.select('.mean-price')
    pattern = re.compile(r'<b>(.*?)</b>')
    for i in data_price:
        if '<b>' in str(i):             #如果原始数据提供人均价格，那么就对数据进行处理，使其可视化
            price.append(re.search(pattern,(str(i))).group(0).lstrip('<b>').rstrip('</b>'))
        else:                           #如果原始数据不提供人均价格，那么就用 - 代替
            price.append('-')
    #爬取单面所有餐馆的地址
    address = []
    data_addr = soup.select('.addr')
    for i in data_addr:
        address.append(i.get_text())
    #正则爬取单面所有餐馆的星级
    star = []
    pattern = re.compile(r'title="(.*?)"></span>')
    star = pattern.findall(str(response.text))
    del star[0]
    if(len(star)== 0):
        star.append('该商户暂无星级')
    #用bs爬取所有餐馆的星级
    # star = []
    # data = soup.select('.comment span')
    # print(data)
    # for i in data:
    #     star.append(i.get('title'))
    #爬取单面所有餐馆的推荐菜
    dish = []
    data_dish = soup.select('.txt')
    pattern = re.compile(r'data-click-name="shop_tag_dish_click" href="http://www.dianping.com/shop/.*?/dish.*?" target="_blank">(.*?)</a>')
    for i in data_dish:
        if 'recommend' in str(i):
            dish.append(pattern.findall(str(i)))
        else:
            dish.append([])
    #爬取单面所有餐馆的评分
    grade_raw = []
    grade = []
    temp = []
    dat = []
    data_grade = soup.select('.txt')
    for i in data_grade:
        if 'comment-list' in str(i):
            soup_ = bs(str(i),'lxml')
            dat.extend(soup_.select('.comment-list b'))
        else:
            dat.append('-');dat.append('-');dat.append('-')
    for i in dat:
        if i != '-':
            grade_raw.append(str(i).lstrip('<b>').rstrip('</b>'))
        else:
            grade_raw.append('-')
    flag = 0
    for j in grade_raw:
        temp.append(j)
        flag = flag + 1
        if (flag == 3):
            grade.append(temp)
            flag = 0
            temp = []
    return (res_name,price,address,star,dish,grade)
def parse_all_pages(url):
    res_name_all = []
    price_all = []
    address_all = []
    star_all = []
    dish_all = []
    grade_all = []
    pattern = re.compile(r'http://www.dianping.com/(.*?)/ch10/g(.*?)')
    num = int(parse_page_numeber(url))
    print('\n共有%d页'%num)
    for i in range(num):
       print('正在爬取第%d页......'%(i+1))
       (res_name , price , address , star , dish , grade) =  parse_one_page(url,i+1)
       res_name_all.extend(res_name)
       price_all.extend(price)
       address_all.extend(price)
       star_all.extend(star)
       dish_all.extend(dish)
       grade_all.extend(grade)
    return(res_name_all,price_all,address_all,star_all,dish_all,grade_all)
def parse_one_city(url):
    res_name_all = []
    price_all = []
    address_all = []
    star_all = []
    dish_all = []
    grade_all = []
    code_all = []
    for i in parse_dish_code(url):
        print('\n正在爬取%s'%(code[i]))
        (res_name , price , address , star , dish , grade) = parse_all_pages(url+'/g'+i)
        for k in range(len(res_name)):
            code_all.append(i)
        res_name_all.extend(res_name)
        price_all.extend(price)
        address_all.extend(address)
        star_all.extend(star)
        dish_all.extend(dish)
        grade_all.extend(grade)
    return(code_all,res_name_all,price_all,address_all,star_all,dish_all,grade_all)
def parse_all_cities(url):
    city_url = cityurl.parse_city_url(url)
    db= pymysql.connect(host="localhost",user="root",password="carnifex",db="food_crawler",port=3306,use_unicode=True, charset="utf8") 
    # 使用cursor()方法获取操作游标  
    cur = db.cursor() 
    # pool = multiprocessing.Pool(1)
    for name in city_url:
        print('\n\n\n%s'%name)
        # (code_all,res_name_all,price_all,address_all,star_all,dish_all,grade_all) = pool.map(parse_one_city,('http://'+city_url[name]+'/ch10',))
        (code_all,res_name_all,price_all,address_all,star_all,dish_all,grade_all)=parse_one_city('http://'+city_url[name]+'/ch10')
        print('%s的美食信息爬取完毕！'%name)
        print('开始存储%s的美食信息......'%name)
        cur.execute("DROP TABLE IF EXISTS %s"%name)      
    # 使用预处理语句创建表
        sql = """CREATE TABLE %s(
                city_code varchar(10),
                res_name varchar(100),
                price varchar(10),
                address varchar(100),
                star varchar(50),
                dish varchar(100),
                grade varchar(100) 
                )"""%name
        cur.execute(sql)
        for i in range(len(res_name_all)):
            res_name_all[i] = cur.connection.escape(res_name_all[i]);  
            sql_insert =('insert into %s(city_code,res_name,price,address,star,dish,grade)values("%s","%s","%s","%s","%s","%s","%s")'%(name,code_all[i],res_name_all[i],price_all[i],address_all[i],star_all[i],dish_all[i],grade_all[i]))
            cur.execute(sql_insert)
            db.commit()
        print('%s的美食信息存储完毕！'%name)
        time.sleep(5)
if __name__ == '__main__':
    start = time.clock()
    parse_all_cities(url)
    end = time.clock()
    print('共耗时%s秒'%(end-start))'''