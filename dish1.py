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
    code = []
    for m in pattern.finditer(str(text)):      
        code.append(m.group(1))
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
            # print(type(re.search(pattern,(str(i))).group(0)))
            price.append(re.search(pattern,(str(i))).group(0).lstrip('<b>').rstrip('</b>'))
        else:                           #如果原始数据不提供人均价格，那么就用 - 代替
            price.append('-')
    #print(price)
    #爬取单面所有餐馆的地址
    address = []
    data_addr = soup.select('.addr')
    for i in data_addr:
        address.append(i.get_text())
    #print(address)
    #正则爬取单面所有餐馆的星级
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
    #print(grade)
    return (res_name,price,address,star,dish,grade)
def parse_all_pages(url,headers):
    res_name_all = []
    price_all = []
    address_all = []
    star_all = []
    dish_all = []
    grade_all = []
    for i in range(int(parse_page_numeber(url,headers))):
       (res_name , price , address , star , dish , grade) =  parse_one_page(url,headers,i+1)
       res_name_all.extend(res_name)
       price_all.extend(price)
       address_all.extend(price)
       star_all.extend(star)
       dish_all.extend(dish)
       grade_all.extend(grade)
    return(res_name_all,price_all,address_all,star_all,dish_all,grade_all)
def parse_one_city(url,headers):
    res_name_all = []
    price_all = []
    address_all = []
    star_all = []
    dish_all = []
    grade_all = []
    code_all = []
    for i in parse_dish_code(url,headers):
        print(i)
        (res_name , price , address , star , dish , grade) = parse_all_pages(url+'/g'+i,headers)
        for k in range(len(res_name)):
            code_all.append(i)
        res_name_all.extend(res_name)
        price_all.extend(price)
        address_all.extend(address)
        star_all.extend(star)
        dish_all.extend(dish)
        grade_all.extend(grade)
    return(code_all,res_name_all,price_all,address_all,star_all,dish_all,grade_all)
# def parse_all_cities(url,headers):
#     city_url = cityurl.parse_city_url(url,headers)
#     for i in city_url:
#         print(i)
#         print(parse_one_city('http://'+city_url[i]+'/ch10',headers))
if __name__ == '__main__':
    (code_all,res_name_all,price_all,address_all,star_all,dish_all,grade_all)=parse_one_city(url,headers)
    # print(len(code_all))
    # print(len(price_all))
    # print(len(res_name_all))
    # print(len(address_all))
    # print(len(star_all))
    # print(len(dish_all))
    # print(len(grade_all))
    db= pymysql.connect(host="localhost",user="root",password="carnifex",db="food_crawler",port=3306,use_unicode=True, charset="utf8")  
  
    # 使用cursor()方法获取操作游标  
    cur = db.cursor()  
    cur.execute("DROP TABLE IF EXISTS leping")
 
# 使用预处理语句创建表
    sql = """CREATE TABLE leping (
            city_code varchar(200),
            res_name varchar(400),
            price varchar(200),
            address varchar(200),
            star varchar(200),
            dish varchar(200),
            grade varchar(200) 
            )"""
 
    cur.execute(sql)
    for i in range(len(res_name_all)):
        res_name_all[i] = cur.connection.escape(res_name_all[i]);  
        sql_insert =('insert into leping (city_code,res_name,price,address,star,dish,grade)values("%s","%s","%s","%s","%s","%s","%s")'%(code_all[i],res_name_all[i],price_all[i],address_all[i],star_all[i],dish_all[i],grade_all[i]))
        #sql_insert =("insert into leping (city_code,res_name,price,address,star,dish,grade)values('%s','%s','%s','%s','%s','%s','%s')"%(str(code_onecity[i]),str(res_name_onecity[i]),str(price_onecity[i]),str(address_onecity[i]),str(star_onecity[i]),str(dish_onecity[i]),str(grade_onecity[i])))

        cur.execute(sql_insert)
        db.commit()
    sql_select='select * from leping'
    cur.execute(sql_select)
    data=cur.fetchone()
    print(data)
