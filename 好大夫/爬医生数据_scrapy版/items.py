# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class HaodfItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    grade = scrapy.Field()
    hos = scrapy.Field()
    hos_label1 = scrapy.Field()
    hos_label2 = scrapy.Field()
    hos_label3 = scrapy.Field()
    faculty = scrapy.Field()
    recom = scrapy.Field()

    effi = scrapy.Field()
    atti = scrapy.Field()
    consult = scrapy.Field()
    register = scrapy.Field()
    doc_url = scrapy.Field() # 不输出
    docId = scrapy.Field()

    cons_num = scrapy.Field()
    cons_satis = scrapy.Field()
    wait_time = scrapy.Field() 

    visits = scrapy.Field() 
    visits_yes = scrapy.Field()
    articles = scrapy.Field()
    patients = scrapy.Field()
    patients_after_diag = scrapy.Field()
    comments = scrapy.Field()
    gifts = scrapy.Field()
    last_online = scrapy.Field()
    regist_time = scrapy.Field()

    pass
