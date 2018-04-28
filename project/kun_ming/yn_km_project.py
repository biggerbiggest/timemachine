# -*- coding:utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import re, time, json
import requests
from scrapy.http import Request, FormRequest
from bs4 import BeautifulSoup
from selenium import webdriver
from scrapy_crawler.data.project_model import ProjectModel
from scrapy_crawler.base import base_spider
from scrapy_crawler.data.url_model import UrlModel
from scrapy_crawler.utils import config

'''
author = iman
'''

class projectSpider(base_spider.Spider):
    name = 'yn_km_project'
    source = '昆明市公共资源交易中心'
    ch_area = '云南省'
    ch_city = '昆明市'
    ch_region = '昆明市'
    en_area = 'yunnan'
    en_city = 'kunming'
    en_region = 'kunming'
    url = 'https://www.kmggzy.com/Jyweb/PBJGGSList.aspx?Type=交易信息&SubType=1&SubType2=11'
    type = 0
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
        'Ajax-method': 'GetPageJYXTXXFB',
        'Connection': 'keep-alive',
        'Content-Length': '194',
        'Content-Type': 'text/plain; charset=UTF-8',
        'Cookie': 'ASP.NET_SessionId=xdoj1k24jseqj1l4dnutjdf2',
        'Host': 'www.kmggzy.com',
        'Origin': 'https://www.kmggzy.com',
        'Referer': 'https://www.kmggzy.com/Jyweb/PBJGGSList.aspx?Type=%e4%ba%a4%e6%98%93%e4%bf%a1%e6%81%af&SubType=1&SubType2=11',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36',
    }

    def start_requests(self):
        return [Request(
            url=self.url,
            callback=self.parse_project,
            errback=self.errback_httpbin,
        )]

    def parse_project(self, response):
        # 更新网页状态
        UrlModel().update_url_status((self.name, self.source, self.url, self.ch_area, self.ch_city, self.ch_region,
                                      self.en_area, self.en_city, self.en_region, response.status, self.type))
        # self.redis_util.insert_db(self.name, self.url)
        # if self.redis_util.get_url(self.name) is not None:
        #     # 只爬取前几页
        #     all_page = config.PAGE_NUM
        # else:
        #     all_page = 832
        all_page = 832
        self.redis_util.insert_db(self.name, response.url)
        for i in range(all_page):
            j = int(time.time()*1000)
            data = '[' + str(i*15) + ',15,"FBKSSJ DESC","GCBDMC","","SubSystemName={2} AND Area in ({0}, 11,12,13,14,15,16,17,18,19,20) AND (XXLB = 11)","[{\\"pvalue\\":\\"1\\"},{\\"pvalue\\":\\"0\\"},{\\"pvalue\\":\\"JSGC\\"}]"]' + str(j)
            url = 'https://www.kmggzy.com/TrueLoreAjax/TrueLore.Web.WebUI.WebAjaxService,TrueLore.Web.WebUI.ashx'
            res = requests.post(url, data=data, headers=self.headers)
            s = res.content
            pro_name_list = re.findall('XMMC:"(.*?)",', s)
            pro_date_list = re.findall('FBKSSJ:"(.*?)",', s)
            registration_num_list = re.findall('BDGCBH:"(.*?)",', s)
            guid_list = re.findall('XXFBGuid:"(.*?)",', s)
            for (guid, pro_name, pro_date, registration_num) in zip(guid_list, pro_name_list, pro_date_list, registration_num_list):
                detail_url = 'https://www.kmggzy.com/Jyweb/ZBJGGSNewView2.aspx?isBG=0&guid=' + guid +'&subType2=11&subType=1&type=交易信息&area=1&zbtype=0'
                if self.redis_util.get_detail_url(self.name, detail_url, **{'dbnum': self.type}):
                    continue
                yield self.parse_info(detail_url, guid, pro_name, pro_date, registration_num)

    def parse_info(self, detail_url, guid, pro_name, pro_date, registration_num):
        global ar_name, com_name
        ar_name = ''
        com_name = ''
        pro_name = pro_name
        pro_date = pro_date
        registration_num = registration_num
        duration = ''
        money = str(0)
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
            'Ajax-method': 'GetZBJGGSHXRNewByGuid',
            'Connection': 'keep-alive',
            'Content-Length': '53',
            'Content-Type': 'text/plain; charset=UTF-8',
            'Cookie': 'ASP.NET_SessionId=xdoj1k24jseqj1l4dnutjdf2',
            'Host': 'www.kmggzy.com',
            'Origin': 'https://www.kmggzy.com',
            'Referer': 'https://www.kmggzy.com/Jyweb/ZBJGGSNewView2.aspx?isBG=0&guid=71be0490-2e7c-4ce1-8663-4a71cf95112c&subType2=11&subType=1&type=%E4%BA%A4%E6%98%93%E4%BF%A1%E6%81%AF&area=1&zbtype=0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36',
            }
        a = int(time.time() * 1000)
        p_data = '["' + guid + '"]' + str(a)
        url = 'https://www.kmggzy.com/TrueLoreAjax/TrueLore.Web.WebUI.WebAjaxService,TrueLore.Web.WebUI.ashx'
        original_url = detail_url
        print detail_url
        res = requests.post(url, data=p_data, headers=headers)
        if re.findall(',1:"(.*?)",', res.content):
            com_name = re.findall(',1:"(.*?)",', res.content)[1]
            ar_name = re.findall(',3:"(.*?)",', res.content)[1]

        ProjectModel().insert_project(self.name, com_name, ar_name, pro_name, pro_date, money, self.source, original_url,
                                      duration, registration_num, self.ch_area, self.ch_city, self.ch_region, self.en_area,
                                      self.en_city, self.en_region, self.crawler_id, self.spider_id, self.headers['User-Agent'])
        # print '项目编号：' + registration_num + '项目名称：' + pro_name + '\t' + '发布日期：' + pro_date + '\t' + '中标公司：' + com_name, original_url












