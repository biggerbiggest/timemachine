# -*- coding:utf-8 -*-
import sys, requests
reload(sys)
sys.setdefaultencoding('utf-8')
from scrapy.http import Request, FormRequest
from lxml import etree
from bs4 import BeautifulSoup
from scrapy_crawler.base import base_spider
from scrapy_crawler.data.project_model import ProjectModel
from scrapy_crawler.data.url_model import UrlModel
from scrapy_crawler.utils import config

'''
author=iman 
'''
class projectSpider(base_spider.Spider):
    name = 'yn_qj_project'
    source = '曲靖市公共资源交易网'
    ch_area = '云南省'
    ch_city = '曲靖市'
    ch_region = '曲靖市'
    en_area = 'yunnan'
    en_city = 'qujing'
    en_region = 'qujing'
    url = 'http://jyxt.qjggzyxx.gov.cn/jyxx/jsgcZbjggs'
    type = 0
    headers = {
        'User-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
        'Referer': 'http://jyxt.qjggzyxx.gov.cn/jyxx/jsgcZbgg',
    }

    def start_requests(self):
        return [FormRequest(url=self.url, callback=self.parse_project, errback=self.errback_httpbin)]

    def parse_project(self, response):
        # 更新网址状态
        UrlModel().update_url_status((self.name, self.source, self.url, self.ch_area, self.ch_city, self.ch_region,
                                     self.en_area, self.en_city, self.en_region, response.status, self.type))
        if self.redis_util.get_url(self.name) is not None:
            # 只爬取前几页
            all_page = config.PAGE_NUM
        else:
            all_page = 30
            self.redis_util.insert_db(self.name, response.url)
        # all_page = 30
        for i in range(1, all_page+1):
            form_data = {
                'currentPage': i,
                'area': '003',
                'industriesTypeCode': '',
                'scrollValue': '0',
                'bulletinName': '',
                'secondArea': '',
            }
            res = requests.post(self.url, data=form_data, headers=self.headers)
            con = etree.HTML(res.text)
            tr_list = con.xpath("//div[@class='news']/table/tr")
            tr_list.pop(0)
            for tr in tr_list:
                detail_url = 'http://jyxt.qjggzyxx.gov.cn' + tr.xpath("./td[2]/a/@href")[0]
                pro_date = tr.xpath("./td[3]/text()")[0]
                # print detail_url, pro_date
                if self.redis_util.get_detail_url(self.name, detail_url, **{'dbnum': self.type}):
                    continue
                yield self.make_requests_from_url(detail_url, pro_date)

    def make_requests_from_url(self, url, pro_date):
        return FormRequest(url, callback=self.parse_info, meta={'pro_date': pro_date})

    def parse_info(self, response):
        global registration_num, pro_name, com_name, ar_name, money, tr_list
        money = ''
        tr_list = []
        registration_num = ''
        pro_name = ''
        com_name = ''
        ar_name = ''
        duration = ''
        original_url = response.url
        pro_date = response.meta['pro_date']
        soup = BeautifulSoup(response.body, 'lxml')
        if soup.find('div', class_='con'):
            tr_list = soup.find('div', class_='con').find('table').find_all('tr')
        for tr in tr_list:
            tr_content = tr.text

            if '备注说明：' not in tr_content:
                # 编号
                if '标段编号：' in tr_content:
                    registration_num = tr_content.split('标段编号：')[1].strip()
                # 项目名
                if '标段名称：' in tr_content:
                    pro_name = tr_content.split('标段名称：')[1].strip()
                # 中标公司
                if '中标人：' in tr_content:
                    com_name = tr_content.split('中标人：')[1].strip()
                # 项目负责人
                if '项目经理：' in tr_content:
                    ar_name = tr_content.split('：')[1].strip()
                # 项目金额
                if '中标价：' in tr_content:
                    money = tr_content.split('中标价：')[1].strip()
                    if '万元' in money:
                        money = money.split('万元')[0]
        if ar_name == '无' or ar_name == '/':
            ar_name = ''
        ProjectModel().insert_project(self.name, com_name, ar_name, pro_name, pro_date, money,
                                      self.source, original_url, duration,
                                      registration_num, self.ch_area, self.ch_city,
                                      self.ch_region,
                                      self.en_area, self.en_city,
                                      self.en_region, self.crawler_id, self.spider_id,
                                      self.headers['User-agent']
                                      )
        # print 'num：' + registration_num, '\t' + 'pname：'+ pro_name, '\t' + 'date：' + pro_date, '\t' + 'cname：' + com_name, '\t' + 'aname：' + ar_name, '\t' + 'money：'+ money, response.url