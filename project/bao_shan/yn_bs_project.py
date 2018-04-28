# -*- coding:utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import re
import requests
from scrapy.http import Request, FormRequest
from scrapy_crawler.data.project_model import ProjectModel
from scrapy_crawler.base import base_spider
from scrapy_crawler.data.url_model import UrlModel
from w3lib.html import remove_tags
from lxml import etree
from scrapy_crawler.utils import config
'''
auther_= iman
'''
class projectSpider(base_spider.Spider):
    name = 'yn_bs_project'
    source = '保山市公共资源交易中心'
    ch_area = '云南省'
    ch_city = '保山市'
    ch_region = '保山市'
    en_area = 'yunnan'
    en_city = 'baoshan'
    en_region = 'baoshan'
    url = 'http://www.bszwzx.gov.cn/jyxx/jsgcZbjggs'
    type = 0
    headers = {
        'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
        'Referer': 'http://www.bszwzx.gov.cn/jyxx/jsgcZbjggs'
    }

    def start_requests(self):
        return [Request(url=self.url,
                        callback=self.parse_project,
                        errback=self.errback_httpbin
                        )]

    def parse_project(self, response):
        UrlModel().update_url_status((self.name, self.source, response.url, self.ch_area, self.ch_city, self.ch_region,
                                      self.en_area, self.en_city, self.en_region, response.status, self.type))
        if self.redis_util.get_url(self.name) is not None:
            # 只爬取前几页
            all_page = config.PAGE_NUM
        else:
            all_page = 8
            self.redis_util.insert_db(self.name, response.url)

        # all_page = 60
        for i in range(1, all_page+1):
            data = {
                "currentPage": i,
                "area": "005",
                'industriesTypeCode': '',
                'scrollValue': 0,
                'bulletinNam': '',
                'secondArea': ''
                 }
            res = requests.post(self.url, data=data, headers=self.headers)
            con = etree.HTML(res.text)
            tr_list = con.xpath("//div[@class='news']/table/tr")
            tr_list.pop(0)
            for tr in tr_list:
                detail_url = 'http://www.bszwzx.gov.cn' + tr.xpath("./td[2]/a/@href")[0]
                pro_name = tr.xpath("./td[2]/a/@title")[0]
                pro_date = tr.xpath("./td[3]/text()")[0]
                if self.redis_util.get_detail_url(self.name, detail_url, **{'dbnum': self.type}):
                    continue
                yield self.make_requests_from_url(detail_url, pro_date, pro_name)

    def make_requests_from_url(self, url, pro_date, pro_name):
        return FormRequest(url=url, callback=self.parse_info, meta={'pro_date': pro_date, 'pro_name': pro_name})

    def parse_info(self, response):
        global pro_name, com_name, ar_name, money, registration_num
        pro_name = ''
        com_name = ''
        ar_name = ''
        money = ''
        original_url = response.url
        registration_num = ''
        pro_date = response.meta['pro_date']
        pro_name = response.meta['pro_name']
        web_data = response.body
        # 项目编号
        if re.match(".*?标段编号\：(.*?)标段", web_data, re.DOTALL):
            registration_num = remove_tags(re.match(".*?标段编号\：(.*?)标段", web_data, re.DOTALL).group(1)).strip().replace("\n", "").replace("\r", "").replace("\t", "").replace("&nbsp;", "").replace("：", "")
        else:
            registration_num = ''
        # 中标单位
        if re.match(".*?中标人\：(.*?公司)", web_data, re.DOTALL):
            com_name = remove_tags(re.match(".*?中标人\：(.*?公司)", web_data, re.DOTALL).group(1)).strip().replace("\n", "").replace("\r", "").replace("\t", "").replace("&nbsp;", "").replace("/", "").replace("：", "")
            if "院" in com_name:
                com_name = com_name.split("院")[0] + "院"
            if "局" in com_name:
                com_name = com_name.split("局")[0] + "局"
            if "中心" in com_name:
                com_name = com_name.split("中心")[0] + "中心"
            if '"' in com_name:
                com_name = com_name.split('"')[-1]
            if "中标" in com_name or "招标" in com_name:
                com_name = ""

        elif re.match(".*?第一中标侯选人\：(.*?公司)", web_data, re.DOTALL):
            com_name = remove_tags(re.match(".*?第一中标侯选人\：(.*?公司)", web_data, re.DOTALL).group(1)).strip().replace("\n", "").replace("\r", "").replace("\t", "").replace("&nbsp;", "").replace("/", "").replace("：", "")
            if "公司" in com_name:
                com_name = com_name.split("公司")[0] + "公司"
            if "院" in com_name:
                com_name = com_name.split("院")[0] + "院"
            if "局" in com_name:
                com_name = com_name.split("局")[0] + "局"
            if "中心" in com_name:
                com_name = com_name.split("中心")[0] + "中心"
            if '"' in com_name:
                com_name = com_name.split('"')[-1]
            if "中标" in com_name or "招标" in com_name:
                com_name = ""
        elif re.match(".*?中标单位\：(.*?公司)", web_data, re.DOTALL):
            com_name = remove_tags(re.match(".*?中标单位\：(.*?公司)", web_data, re.DOTALL).group(1)).strip().replace("\n", "").replace("\r", "").replace("\t", "").replace("&nbsp;", "").replace("/", "").replace("：", "")
            if "公司" in com_name:
                com_name = com_name.split("公司")[0] + "公司"
            if "院" in com_name:
                com_name = com_name.split("院")[0] + "院"
            if "局" in com_name:
                com_name = com_name.split("局")[0] + "局"
            if "中心" in com_name:
                com_name = com_name.split("中心")[0] + "中心"
            if '"' in com_name:
                com_name = com_name.split('"')[-1]
            if "中标" in com_name or "招标" in com_name:
                com_name = ""
        elif re.match(".*?中标候选人\：(.*?公司)", web_data, re.DOTALL):
            com_name = remove_tags(re.match(".*?中标候选人\：(.*?公司)", web_data, re.DOTALL).group(1)).strip().replace("\n", "").replace("\r", "").replace("\t", "").replace("&nbsp;", "").replace("/", "").replace("：", "")
            if "公司" in com_name:
                com_name = com_name.split("公司")[0] + "公司"
            if "院" in com_name:
                com_name = com_name.split("院")[0] + "院"
            if "局" in com_name:
                com_name = com_name.split("局")[0] + "局"
            if "中心" in com_name:
                com_name = com_name.split("中心")[0] + "中心"
            if '"' in com_name:
                com_name = com_name.split('"')[-1]
            if "中标" in com_name or "招标" in com_name:
                com_name = ""
        elif response.xpath("//div[@class='detail_contect']/table/tr[8]/td/table/tr[2]/td[2]").extract():
            com_name = remove_tags(response.xpath("//div[@class='detail_contect']/table/tr[8]/td/table/tr[2]/td[2]").extract_first())
            if "公司" in com_name:
                com_name = com_name
            elif response.xpath("//div[@class='detail_contect']/table/tr[8]/td/table/tr[2]/td[1]").extract():
                com_name = remove_tags(response.xpath("//div[@class='detail_contect']/table/tr[8]/td/table/tr[2]/td[1]").extract_first())
            else:
                com_name = ""
        elif response.xpath("//table[@class='MsoNormalTable']/tbody/tr[2]/td[3]/p[@class='MsoNormal']/span[1]").extract():
            com_name = remove_tags(response.xpath("//table[@class='MsoNormalTable']/tbody/tr[2]/td[3]/p[@class='MsoNormal']/span[1]").extract_first())
        elif re.match(".*?第一中标候选人为\：(.*?公司)", web_data, re.DOTALL):
            com_name = remove_tags(re.match(".*?.*?第一中标候选人为\：(.*?公司)", web_data, re.DOTALL).group(1)).strip().replace("\n", "").replace("\r", "").replace("\t", "").replace("&nbsp;", "").replace("/", "").replace("：", "")
            if "院" in com_name:
                com_name = com_name.split("院")[0] + "院"
            if "局" in com_name:
                com_name = com_name.split("局")[0] + "局"
            if "中心" in com_name:
                com_name = com_name.split("中心")[0] + "中心"
            if '"' in com_name:
                com_name = com_name.split('"')[-1]
            if "中标" in com_name or "招标" in com_name:
                com_name = ""
        elif re.match(".*?第一中标候选人(.*?公司)", web_data, re.DOTALL):
            com_name = remove_tags(re.match(".*?第一中标候选人(.*?公司)", web_data, re.DOTALL).group(1)).strip().replace("\n", "").replace("\r", "").replace("\t", "").replace("&nbsp;", "").replace("/", "").replace("：", "")
            if "院" in com_name:
                com_name = com_name.split("院")[0] + "院"
            if "局" in com_name:
                com_name = com_name.split("局")[0] + "局"
            if "中心" in com_name:
                com_name = com_name.split("中心")[0] + "中心"
            if '"' in com_name:
                com_name = com_name.split('"')[-1]
            if "中标" in com_name or "招标" in com_name:
                com_name = ""
        elif re.match(".*?中标单位(.*?公司)", web_data, re.DOTALL):
            com_name = remove_tags(re.match(".*?中标单位(.*?公司)", web_data, re.DOTALL).group(1)).strip().replace("\n", "").replace("\r", "").replace("\t", "").replace("&nbsp;", "").replace("/", "").replace("：", "")
            if "公司" in com_name:
                com_name = com_name.split("公司")[0] + "公司"
            if "院" in com_name:
                com_name = com_name.split("院")[0] + "院"
            if "局" in com_name:
                com_name = com_name.split("局")[0] + "局"
            if "中心" in com_name:
                com_name = com_name.split("中心")[0] + "中心"
            if '"' in com_name:
                com_name = com_name.split('"')[-1]
            if "中标" in com_name or "招标" in com_name:
                com_name = ""
        elif re.match(".*?中标人名称(.*?公司)", web_data, re.DOTALL):
            com_name = remove_tags(re.match(".*?中标人名称(.*?公司)", web_data, re.DOTALL).group(1)).strip().replace("\n", "").replace("\r", "").replace("\t", "").replace("&nbsp;", "").replace("/", "").replace("：", "")
            if "公司" in com_name:
                com_name = com_name.split("公司")[0] + "公司"
            if "院" in com_name:
                com_name = com_name.split("院")[0] + "院"
            if "局" in com_name:
                com_name = com_name.split("局")[0] + "局"
            if "中心" in com_name:
                com_name = com_name.split("中心")[0] + "中心"
            if '"' in com_name:
                com_name = com_name.split('"')[-1]
            if "中标" in com_name or "招标" in com_name:
                com_name = ""
        elif re.match(".*?拟中标人(.*?公司)", web_data, re.DOTALL):
            com_name = remove_tags(re.match(".*?拟中标人(.*?公司)", web_data, re.DOTALL).group(1)).strip().replace("\n", "").replace("\r", "").replace("\t", "").replace("&nbsp;", "").replace("/", "").replace("：", "")
            if "公司" in com_name:
                com_name = com_name.split("公司")[0] + "公司"
            if "院" in com_name:
                com_name = com_name.split("院")[0] + "院"
            if "局" in com_name:
                com_name = com_name.split("局")[0] + "局"
            if "中心" in com_name:
                com_name = com_name.split("中心")[0] + "中心"
            if '"' in com_name:
                com_name = com_name.split('"')[-1]
            if "中标" in com_name or "招标" in com_name:
                com_name = ""
        elif re.match(".*?第一中标候选单位\：(.*?公司)", web_data, re.DOTALL):
            com_name = remove_tags(re.match(".*?第一中标候选单位\：(.*?公司)", web_data, re.DOTALL).group(1)).strip().replace("\n", "").replace("\r", "").replace("\t", "").replace("&nbsp;", "").replace("/", "").replace("：", "")
            if "公司" in com_name:
                com_name = com_name.split("公司")[0] + "公司"
            if "院" in com_name:
                com_name = com_name.split("院")[0] + "院"
            if "局" in com_name:
                com_name = com_name.split("局")[0] + "局"
            if "中心" in com_name:
                com_name = com_name.split("中心")[0] + "中心"
            if '"' in com_name:
                com_name = com_name.split('"')[-1]
            if "中标" in com_name or "招标" in com_name:
                com_name = ""
        else:
            com_name = ''
        # 中标价格
        if re.match(".*?中标价\：(.*?)元", web_data, re.DOTALL):
            try:
                money = remove_tags(re.match(".*?中标价\：(.*?)元", web_data, re.DOTALL).group(1)).strip().replace("\n", "").replace("\r", "").replace("\t", "").replace("&nbsp;", "").replace("：", "")
                if "万" in money:
                    money = money.replace("万", "")
                    money = float(money)
                else:
                    money = float(money) / 10000
            except Exception:
                money = 0
        else:
            money = 0
        # 工期
        if re.match(".*?中标工期\：(.*?)天", web_data, re.DOTALL):
            duration = remove_tags(re.match(".*?中标工期\：(.*?)天", web_data, re.DOTALL).group(1)).strip().replace("\n", "").replace("\r", "").replace("\t", "").replace("&nbsp;", "").replace("：", "")
            if "日" in duration:
                duration = duration.split("日")[0]
            if len(duration) > 5:
                duration = str(0)
        else:
            duration = str(0)
        # 建造师或者项目负责人
        if re.match(".*?项目经理\：(.*?)备注", web_data, re.DOTALL):
            ar_name = remove_tags(re.match(".*?项目经理\：(.*?)备注", web_data, re.DOTALL).group(1)).strip().replace("\n", "").replace("\r", "").replace("\t", "").replace("&nbsp;", "").replace("：", "")
            if "招标" in ar_name:
                ar_name = ar_name.split("招标")[0]
            if "，" in ar_name:
                ar_name = ar_name.split("，")[0]
            if len(ar_name) > 3:
                ar_name = ""
        elif re.match(".*?建造师名称(.*?)等", web_data, re.DOTALL):
            ar_name = remove_tags(re.match(".*?建造师名称(.*?)等", web_data, re.DOTALL).group(1)).strip().replace("\n", "").replace("\r", "").replace("\t", "").replace("&nbsp;", "").replace("：", "")
            if "招标" in ar_name:
                ar_name = ar_name.split("招标")[0]
            if "，" in ar_name:
                ar_name = ar_name.split("，")[0]
            if len(ar_name) > 3:
                ar_name = ""
        else:
            ar_name = ""
        money = str(money)
        ProjectModel().insert_project(self.name, com_name, ar_name, pro_name, pro_date, money,
                                      self.source, original_url, duration,
                                      registration_num, self.ch_area, self.ch_city,
                                      self.ch_region, self.en_area, self.en_city,
                                      self.en_region, self.crawler_id, self.spider_id,
                                      self.headers['User-agent'])
        # print '项目编号：' + registration_num + '\t' + '项目名称：' + pro_name + '\t' + '发布日期：' + pro_date + '\t' + '中标人名称：' + com_name,'\t' + '负责人：' + ar_name, '\t' + money

