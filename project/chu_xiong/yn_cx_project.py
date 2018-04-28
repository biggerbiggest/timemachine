# -*- coding:utf-8 -*-
import sys, requests
reload(sys)
sys.setdefaultencoding('utf-8')
from scrapy.http import FormRequest
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
    name = 'yn_cx_project'
    source = '楚雄彝族自治州公共资源交易中心'
    ch_area = '云南省'
    ch_city = '楚雄州'
    en_area = 'yunnan'
    en_city = 'chuxiong'
    url = 'http://www.cxggzy.cn/jyxx/jsgcZbjggs'
    type = 0
    headers = {
        'User-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
    }

    def start_requests(self):
        return [FormRequest(url=self.url, callback=self.parse_project, errback=self.errback_httpbin)]

    def parse_project(self, response):

        # if self.redis_util.get_url(self.name) is not None:
        #     # 只爬取前几页
        #     all_page = config.PAGE_NUM
        # else:
        #     all_page = 71
        # self.redis_util.insert_db(self.name, response.url)
        # all_page = 54
        global ch_region, en_region, all_page
        all_page = 0
        ch_region = ''
        en_region = ''
        for v in ('州本级', '094', '095', '096', '097', '098', '099', '100', '101', '102', '103'):
            if v == '州本级':
                ch_region = '楚雄'
                en_region = 'chuxiong'
                all_page = 2
            elif v == '094':
                ch_region = '楚雄市'
                en_region = 'chuxiongshi'
                all_page = 3
            elif v == '095':
                ch_region = '双柏县'
                en_region = 'shuangbaixian'
                all_page = 2
            elif v == '096':
                ch_region = '牟定县'
                en_region = 'moudingxian'
                all_page = 1
            elif v == '097':
                ch_region = '南华县'
                en_region = 'nanhuaxian'
                all_page = 2

            elif v == '098':
                ch_region = '姚安县'
                en_region = 'yaoanxian'
                all_page = 1
            elif v == '099':
                ch_region = '大姚县'
                en_region = 'dayaoxian'
                all_page = 3

            elif v == '100':
                ch_region = '永仁县'
                en_region = 'yongrenxian'
                all_page = 1

            elif v == '101':
                ch_region = '元谋县'
                en_region = 'yuanmouxian'
                all_page = 2
            elif v == '102':
                ch_region = '武定县'
                en_region = 'wudingxian'
                all_page = 4
            elif v == '103':
                ch_region = '禄丰县'
                en_region = 'lufengxian'
                all_page = 2
            # UrlModel().update_url_status((self.name, self.source, self.url, self.ch_area, self.ch_city, ch_region,
            #                               self.en_area, self.en_city, en_region, response.status, self.type))

            for i in range(1, all_page+1):
                form_data = {
                    'currentPage': i,
                    'area': '014',
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
                    detail_url = 'http://www.cxggzy.cn' + tr.xpath("./td[2]/a/@href")[0]
                    pro_date = tr.xpath("./td[3]/text()")[0]
                    # if self.redis_util.get_detail_url(self.name, detail_url, **{'dbnum': self.type}):
                    #     continue
                    yield self.make_requests_from_url(detail_url, pro_date, ch_region, en_region)

    def make_requests_from_url(self, url, pro_date, ch_region, en_region,):
        return FormRequest(url, callback=self.parse_info, meta={'pro_date': pro_date, 'ch_region': ch_region, 'en_region': en_region})

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
                # 项目名称
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
        #                               ch_region, self.en_area, self.en_city,
        #                               en_region, self.crawler_id, self.spider_id,
        #                               self.headers['User-agent']
        #                               )
        print 'ch_region：%s' % ch_region, 'en_region：%s' % en_region,  response.url
        # print 'num：' + registration_num, '\t' + 'pname：%s' % pro_name, '\t', '\tpro_date：%s' % pro_date, '\t' + 'cname：' + com_name, '\t' + 'aname：' + ar_name, '\t' + 'money：'+ money, response.url
        # print 'cname：' + com_name, '\t' + 'aname：' + ar_name, '\t' + 'money：'+ money