# -*- coding:utf-8 -*-
# 之前已经实现了函数封装登录正方的方法，现在尝试一下类

import os
import time
import requests
from lxml import etree
from urllib.parse import quote  # 用于转换带有中文的URL


# 正方登录类
class ZFLogin(object):
    def __init__(self):

        self.name = input("请输入您的学号")  # 设置账号
        self.password = input("请输入您的密码")  # 密码
        self.url = "https://jwc.scnu.edu.cn/default2.aspx"

        self.s = requests.session()
        html = self.s.get(self.url).content
        html_obj = etree.HTML(html)

        # 获取用于登录的特殊参数 __VIEWSTATE
        self.login__VIEWSTATE = html_obj.xpath("//input[@name='__VIEWSTATE']/@value")[0]

    # 处理验证码
    def deal_code(self):
        img_url = "https://jwc.scnu.edu.cn/CheckCode.aspx"
        img = self.s.get(img_url, stream=True).content
        # 获取保存路径
        dir = os.getcwd() + "\\"
        print("保存验证码到:" + dir + "code.jpg")
        try:
            with open(dir + "code.jpg", "wb") as jpg:
                jpg.write(img)
        except Exception as e:
            print(e)
        code = input("请输入验证码：")
        print("————————————————————")
        return code

    # 登录函数
    def login_post(self, login_times=3):
        # 构建请求头
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
            "__VIEWSTATE": self.login__VIEWSTATE,
            "txtUserName": self.name,  # 用户名
            "Textbox1": "",
            "TextBox2": self.password,  # 密码
            "txtSecretCode": self.deal_code(),  # 调用处理验证码的函数
            'RadioButtonList1': '学生',
            'Button1': '',
            'lbLanguage': '',
            'hidPdrs': '',
            'hidsc': ''
        }

        response = self.s.post(self.url, headers=headers, data=data)
        if response.status_code == 200 and etree.HTML(response.content).xpath("//title/text()")[0][-3:] != "请登录":
            # requests.codes.ok
            print("登录成功")
            return response.content
        else:
            print("第{}次登录失败，状态码为{}".format(4-login_times, response.status_code))
            if login_times > 1:
                login_times -= 1
                print("-------1秒后再次尝试登录--------")
                time.sleep(1)
                print('--------------------------登录中--------------------------')
                return self.login_post(login_times=login_times)

    # 获取成绩
    def get_score(self):
        content = self.login_post()  # 获得登录成功后返回的页面
        # 获取链接
        score_url = "https://jwc.scnu.edu.cn/" + etree.HTML(content).xpath("//ul[@class='nav']/li[5]/ul/li[4]/a/@href")[0]
        # 构建请求头，查看浏览器访问时候的头，复制下来
        headers1 = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Connection": "keep-alive",
            "Host": "jwc.scnu.edu.cn",
            "Origin": "https://jwc.scnu.edu.cn",
            "Referer": "https://jwc.scnu.edu.cn/xs_main.aspx?xh={}".format(self.name)
        }
        score_content = self.s.get(score_url, headers=headers1).content  # 进入查询成绩的页面
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
            "Referer": quote(score_url, safe="/:?=", encoding="gb2312")
        }

        score_statistic = etree.HTML(self.s.post(score_url, headers=headers2, data=data).content)
        print(score_statistic.xpath("//table[@class='datelist']/tr[1]/td//text()"))
        # 各科成绩，打印
        number = len(score_statistic.xpath("//table[@class='datelist']/tr/td[1]/text()"))  # 统计有多少门课
        for i in range(number):
            print(score_statistic.xpath("//table[@class='datelist']/tr[{}]/td/text()".format(i + 2)))


