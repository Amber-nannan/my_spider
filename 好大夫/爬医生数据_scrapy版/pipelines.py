# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pandas as pd

class HaodfPipeline:

    # 该方法可以接受爬虫文件提交过来的item对象,每接收到一个item就会被调用一次
    def process_item(self, item, spider):
        temp_dict={'医生ID':item['docId'],'姓名':item['name'],'职级':item['grade'],'科室':item['faculty'],'医院':item['hos'],'是否公立':item['hos_label1'],\
                    '医院等级':item['hos_label2'],'医院类型':item['hos_label3'],\
                      '病友推荐度':item['recom'],'主观疗效满意度':item['effi'],'态度满意度':item['atti'],'在线问诊':item['consult'],\
           '预约挂号':item['register'],'总问诊量':item['cons_num'],'问诊服务满意度':item['cons_satis'],'一般回复时长':item['wait_time'],\
             '总访问量':item['visits'],'昨日访问':item['visits_yes'],'总文章数':item['articles'],'总患者数':item['patients'],'诊后报道患者':item['patients_after_diag'],\
                 '诊后评论数量':item['comments'],'心意礼物':item['gifts'],'上次在线时间':item['last_online'],'开通时间':item['regist_time']}
        
        df1=pd.DataFrame.from_dict(temp_dict,orient='index').T
        df1.to_csv(r'F:\医生基本信息(Scrapy版).csv',mode='a',header=False,index=False,encoding='utf-8')

        # with open(r'F:\医生基本信息(Scrapy版).csv',mode='a',encoding='utf-8') as fp:
        #     fp.write(df1)
        # return item
