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
    name = 'yn_lj_project'
    source = '云南省公共资源交易网'
    ch_area = '云南省'
    ch_city = '丽江市'
    en_area = 'yunnan'
    en_city = 'lijiang'
    url = 'https://www.ljggzyxx.cn/jyxx/jsgcZbjggs'
    type = 0
    headers = {
        'User-agent':'Mozilla/5.0(Macintosh;U;IntelMacOSX10_6_8;en-us)AppleWebKit/534.50(KHTML,likeGecko)Version/5.1Safari/534.50',
    }

    def start_requests(self):
        return [FormRequest(url=self.url, callback=self.parse_project, errback=self.errback_httpbin)]

    def parse_project(self, response):
        sys.exit(0)
        # 更新网址状态
        # UrlModel().update_url_status((self.name, self.source, self.url, self.ch_area, self.ch_city, self.ch_region,
        #                              self.en_area, self.en_city, self.en_region, response.status, self.type))
        # if self.redis_util.get_url(self.name) is not None:
        #     # 只爬取前几页
        #     all_page = config.PAGE_NUM
        # else:
        #     all_page = 71
        # all_page = 54
        global ch_region, en_region, all_page
        all_page = 0
        ch_region = ''
        en_region = ''
        for v in ('', '049', '050', '051', '052', '053'):
            if v == '':
                ch_region = '丽江市'
                en_region = 'lijiang'
                all_page = 37
            elif v == '049':
                ch_region = '古城区'
                en_region = 'guchengqu'
                all_page = 2
            elif v == '050':
                ch_region = '玉龙县'
                en_region = 'yulongxian'
                all_page = 7
            elif v == '051':
                ch_region = '永胜县'
                en_region = 'yongshengxian'
                all_page = 8
            elif v == '052':
                ch_region = '华坪县'
                en_region = 'huapingxian'
                all_page = 2
            elif v == '053':
                ch_region = '宁蒗县'
                en_region = 'nignlangxian'
                all_page = 5

            # UrlModel().update_url_status((self.name, self.source, self.url, self.ch_area, self.ch_city, ch_region,
            #                               self.en_area, self.en_city, en_region, response.status, self.type))
            # self.redis_util.insert_db(self.name, response.url)

            for i in range(1, all_page+1):
                form_data = {
                    'currentPage': i,
                    'area': '007',
                    'industriesTypeCode': '',
                    'scrollValue': '0',
                    'bulletinName': '',
                    'secondArea': v,
                }
                res = requests.post(self.url, data=form_data, headers=self.headers)
                con = etree.HTML(res.text)
                tr_list = con.xpath("//div[@class='news']/table/tr")
                tr_list.pop(0)
                for tr in tr_list:
                    detail_url = 'https://www.ljggzyxx.cn' + tr.xpath("./td[2]/a/@href")[0]
                    pro_date = tr.xpath("./td[3]/text()")[0]
                    # print detail_url, pro_date, ch_region, en_region
                    # if self.redis_util.get_detail_url(self.name, detail_url, **{'dbnum': self.type}):
                    #     continue
                    yield self.make_requests_from_url(detail_url, pro_date, ch_region, en_region)

    def make_requests_from_url(self, url, pro_date, ch_region, en_region,):
        return FormRequest(url, callback=self.parse_info, meta={'pro_date': pro_date, 'ch_region': ch_region, 'en_region': en_region})

    def parse_info(self, response):
        sys.exit(0)
        global registration_num, pro_name, com_name, ar_name, money
        money = ''
        registration_num = ''
        pro_name = ''
        com_name = ''
        ar_name = ''
        duration = ''
        original_url = response.url
        pro_date = response.meta['pro_date']
        ch_region = response.meta['ch_region']
        en_region = response.meta['en_region']
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
            # ProjectModel().insert_project(self.name, com_name, ar_name, pro_name, pro_date, money,
            #                               self.source, original_url, duration,
            #                               registration_num, self.ch_area, self.ch_city,
            #                               ch_region,
            #                               self.en_area, self.en_city,
            #                               en_region, self.crawler_id, self.spider_id,
            #                               self.headers['User-agent']
            #                               )
        elif soup.find('div', class_='news-layout'):
            p_list = soup.find('div', class_='news-layout').find_all('p')
            for p in p_list:
                if '公司' in p.text and '招标' not in p.text and '评审结果' not in p.text:
                    # print p.text
                    if '：' in p.text:
                        com_name = p.text.split('：')[1]
                        if '，' in com_name:
                            com_name = com_name.split('，')[0]
                        elif '；' in com_name:
                            com_name = com_name.split('；')[0]
                        elif '。' in com_name:
                            com_name = com_name.split('。')[0]
                if '中标价' in p.text:
                    # print p.text
                    if '工期' in p.text:
                        money = p.text.strip().split('中标价：')[1].split('元')[0]
                    elif '万元' in p.text:
                        money = p.text.strip().split(' ')[0]
                    print money
                    # money = p.text.split('中标价：')[1].split('万元')[0]
                # 项目负责人
                # if '项目经理：' in p.text:
                #     ar_name = p.text.split('：')[1].strip()
                # if '标段编号：' in p.text:
                #     registration_num = p.text.split('标段编号：')[1].strip()
                # if ar_name == '无' or ar_name == '/':
                #     ar_name = ''
                # money = str(money)
                # ProjectModel().insert_project(self.name, com_name, ar_name, pro_name, pro_date, money,
                #                               self.source, original_url, duration, registration_num, self.ch_area,
                #                               self.ch_city, ch_region, self.en_area, self.en_city, en_region,
                #                               self.crawler_id, self.spider_id, self.headers['User-agent']
                #                               )
                # print 'ch_region：%s' % ch_region, 'en_region：%s' % en_region,  response.url
                # print 'num：' + registration_num, '\t' + 'pname：%s' % pro_name, '\t' + 'ch_region：%s' % ch_region, 'en_region：%s' % en_region, '\tpro_date：%s' % pro_date, '\t' + 'cname：' + com_name