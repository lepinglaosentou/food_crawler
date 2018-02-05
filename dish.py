# -*- coding:utf-8 -*-
from bs4 import BeautifulSoup as bs
import requests
import re
import pymysql

url = 'http://www.dianping.com/leping/ch10'  #乐平美食初始页面
headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36'
    }
def parse_dish_code(url,headers):
    response = requests.get(url,headers = headers)
    #print(response.text)
    soup = bs(response.content,'lxml')
    text = soup.find_all(class_ = 'nc-contain')
    # print(text)
    pattern = re.compile(r'data-cat-id="(.*?)" data-click-name="select_cate_(.*?)_click"')  #group(1)为菜系代码，group(2)为菜系
    global code
    code = {}
    for m in pattern.finditer(str(text)):      
        code["%s"%m.group(1)]="%s"%m.group(2)
    print(code)
    return(code)
def parse_page_numeber(url,headers):
    response = requests.get(url,headers = headers)
    soup = bs(response.content,'lxml')
    data = soup.select('.PageLink')
    if data:
        page = []
        for i in data:
            page.append(i.get_text())
    else:
        page = [1]
    print(page[-1])
    return (page[-1])
def parse_one_page(url,headers,page_number):
    response =  requests.get(url+'p'+str(page_number),headers = headers)
    soup = bs(response.content,'lxml')
    #爬取单面所有餐馆的名称
    data_res = soup.select('.tit h4')
    global res_name
    res_name = []        #单面所有餐馆名称
    for i in data_res:
        res_name.append(str(i).lstrip('<h4>').rstrip('</h4>'))
    #print(res_name)
    #爬取单面所有餐馆的人均价格
    global price
    price = []           #单面所有餐馆的人均价格
    data_price = soup.select('.mean-price')
    pattern = re.compile(r'<b>(.*?)</b>')
    for i in data_price:
        if '<b>' in str(i):             #如果原始数据提供人均价格，那么就对数据进行处理，使其可视化
            # print(type(re.search(pattern,(str(i))).group(0)))
            price.append(re.search(pattern,(str(i))).group(0).lstrip('<b>').rstrip('</b>'))
        else:                           #如果原始数据不提供人均价格，那么就用 - 代替
            price.append('-')
    #print(price)
    #爬取单面所有餐馆的地址
    global address
    address = []
    data_addr = soup.select('.addr')
    for i in data_addr:
        address.append(i.get_text())
    #print(address)
    #正则爬取单面所有餐馆的星级
    global star
    star = []
    pattern = re.compile(r'title="(.*?)"></span>')
    star = pattern.findall(str(response.text))
    del star[0]
    #print(star)
    #用bs爬取所有餐馆的星级
    # star = []
    # data = soup.select('.comment span')
    # print(data)
    # for i in data:
    #     star.append(i.get('title'))
    #爬取单面所有餐馆的推荐菜
    global dish
    dish = []
    data_dish = soup.select('.txt')
    pattern = re.compile(r'data-click-name="shop_tag_dish_click" href="http://www.dianping.com/shop/.*?/dish.*?" target="_blank">(.*?)</a>')
    for i in data_dish:
        if 'recommend' in str(i):
            dish.append(pattern.findall(str(i)))
        else:
            dish.append([])
    #print(dish)
    #爬取单面所有餐馆的评分
    grade_raw = []
    global grade
    grade = []
    temp = []
    data_grade = soup.select('.comment-list b')
    for i in data_grade:
        grade_raw.append(str(i).lstrip('<b>').rstrip('</b>'))
    flag = 0
    for j in grade_raw:
        if (flag == 3):
            grade.append(temp)
            flag = 0
            temp = []
        temp.append(j)
        flag = flag + 1
    #print(grade)
def parse_all_pages(url,headers):
    for i in range(int(parse_page_numeber(url,headers))):
        parse_one_page(url,headers,i+1)
def parse_one_city(url,headers):
    for i in parse_dish_code(url,headers):
        print(i)
        parse_all_pages(url+'/g'+i,headers)
if __name__ == '__main__':
    parse_dish_code(url,headers)
    #parse_one_city(url,headers)
    db= pymysql.connect(host="localhost",user="root",password="carnifex",db="food_crawler",port=3306,use_unicode=True, charset="utf8")  
  
    # 使用cursor()方法获取操作游标  
    cur = db.cursor()  
    cur.execute("DROP TABLE IF EXISTS leping")
 
# 使用预处理语句创建表
    sql = """CREATE TABLE leping (
    res_name CHAR(100) NOT NULL,
    price CHAR(10),
    address char(100),
    star char(20),
    dish CHAR(100),
    grade char(10) );"""
 
    cur.execute(sql)
    for i in parse_one_city(url,headers):

        sql_insert ="insert into leping (res_name,price,address,star,dish,grade)values(%s,%s,%s,%s,%s,%s)"%(res_name[i],price[i],address[i],star[i],dish[i],grade[i])

        
  

    
        cur.execute(sql_insert)
        db.commit() 
