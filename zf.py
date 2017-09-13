# -*- coding:utf-8 -*-
# 正方的模拟登录

import os
import requests
from lxml import etree
from urllib.parse import quote  # 用于转换带有中文的URL


# 第一次简单请求
def letsget(url):
    s = requests.session()
    html = s.get(url).content
    html_obj = etree.HTML(html)

    # 获取特殊参数 __VIEWSTATE
    __VIEWSTATE = html_obj.xpath("//input[@name='__VIEWSTATE']/@value")[0]
    return s, __VIEWSTATE


# 验证码的处理
# 后来发现可以绕过处理，也就是说不去请求这个验证码就不验证，现在好像又不行了
def deal_code(s):
    img_url = "https://jwc.scnu.edu.cn/CheckCode.aspx"
    img = s.get(img_url, stream=True).content
    dir = os.getcwd()+"\\"
    print("保存验证码到:"+dir+"code.jpg")
    try:
        with open(dir+"code.jpg", "wb") as jpg:
            jpg.write(img)
    except Exception as e:
        print(e)
    code = input("请输入验证码：")
    return code


# 构建登录的POST请求
def login_post(url, s, __VIEWSTATE, code):
    # 构建请求头
    name = input("请输入学号：")
    password = input("请输入密码：")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Connection": "keep-alive",
        "Host": "jwc.scnu.edu.cn",
        "Origin": "https://jwc.scnu.edu.cn",
        "Referer": "https://jwc.scnu.edu.cn / default2.aspx"
    }
    # 构建表单数据
    data = {
        "__VIEWSTATE": __VIEWSTATE,
        "txtUserName": name,  # 用户名
        "Textbox1": "",
        "TextBox2": password,  # 密码
        "txtSecretCode": code,  # 验证码，可以直接不带
        'RadioButtonList1': '学生',
        'Button1': '',
        'lbLanguage': '',
        'hidPdrs': '',
        'hidsc': ''
    }
    response = s.post(url, headers=headers, data=data)
    if response.status_code == 200:  # requests.codes.ok
        print("登录成功")
        # print(response.content)
        return response.content
    else:
        print("登录失败", response.status_code)


# 获取成绩
def get_score(s, content):
    # 获取链接
    url = "https://jwc.scnu.edu.cn/" + etree.HTML(content).xpath("//ul[@class='nav']/li[5]/ul/li[4]/a/@href")[0]
    # 构建请求头
    headers1 = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Connection": "keep-alive",
        "Host": "jwc.scnu.edu.cn",
        "Origin": "https://jwc.scnu.edu.cn",
        "Referer": quote(url, safe="/:?=", encoding="gb2312")
    }
    score_content = s.get(url, headers=headers1).content  # 进入查询成绩的页面
    score_obj = etree.HTML(score_content)
    __VIEWSTATE = score_obj.xpath("//input[@name='__VIEWSTATE']/@value")[0]  # 解析成绩查询页面，获取特殊参数__VIEWSTATE

    # 构建POST请求
    data = {
        "__VIEWSTATE": __VIEWSTATE,
        "hidLanguage": "",
        "ddlXN": "",
        "ddlXQ": "",
        "ddl_kcxz": "",
        "btn_zcj": u"历年成绩"
    }
    headers2 = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Connection": "keep-alive",
        "Host": "jwc.scnu.edu.cn",
        "Origin": "https://jwc.scnu.edu.cn",
        "Referer": "https://jwc.scnu.edu.cn/xscjcx.aspx?xh=20143201055&xm=%C1%D6%DE%C8&gnmkdm=N121605"
    }

    score_statistic = etree.HTML(s.post(url, headers=headers2, data=data).content)
    print(score_statistic.xpath("//table[@class='datelist']/tr[1]/td//text()"))
    # 各科成绩，打印
    number = len(score_statistic.xpath("//table[@class='datelist']/tr/td[1]/text()"))
    for i in range(number):
        print(score_statistic.xpath("//table[@class='datelist']/tr[{}]/td/text()".format(i+2)))



def main():
    url = "https://jwc.scnu.edu.cn/default2.aspx"
    s, __VIEWSTATE = letsget(url)
    code = deal_code(s)
    content = login_post(url=url, s=s, code=code,  __VIEWSTATE=__VIEWSTATE)
    get_score(s=s, content=content)


if __name__ == '__main__':
    main()
