import scrapy
from haodf.items import HaodfItem
import re
class DocInfoSpider(scrapy.Spider):
    # 爬虫文件的名称：就是爬虫源文件的唯一标识
    name = 'doc_info'
    #起始的url列表：该列表中存放的url会被scrapy自动进行请求的发送
    with open(r'F:\专家推荐页面url.txt','r',encoding='utf-8') as f:
        start_urls = f.readlines()
    # start_urls =['https://www.haodf.com/hospital/471/tuijian.html?p=33']  #这一行用来测试

    # 医生主页
    def parse_doc_other_info(self,response):
        item=response.meta['item']       
        test=response.xpath('//ul[@class="item-body"]/li[1]/span[2]/text()')
        if test==[]:
            item['visits']=''
            item['visits_yes']=''
            item['articles']=''
            item['patients']=''
            item['patients_after_diag']=''
            item['comments']=''
            item['gifts']=''
            item['last_online']=''
            item['regist_time']=''
        else:
            temp2=response.xpath('//ul[@class="item-body"]')
            item['visits']=temp2.xpath('./li[1]/span[2]/text()')[0].extract().strip() 
            a=temp2.xpath('./li[2]/span[2]/text()')[0].extract()
            item['visits_yes']=re.findall('(\d+)次',a)[0]
            item['articles']=temp2.xpath('./li[3]/span[2]/text()')[0].extract().strip('篇')
            item['patients']=temp2.xpath('./li[4]/span[2]/text()')[0].extract().strip('位')
            item['patients_after_diag']=temp2.xpath('./li[5]/span[2]/text()')[0].extract().strip('位')
            item['comments']=temp2.xpath('./li[6]/span[2]/text()')[0].extract().strip('个')
            item['gifts']=temp2.xpath('./li[7]/span[2]/text()')[0].extract().strip('个')
            item['last_online']=temp2.xpath('./li[8]/span[2]/text()')[0].extract()
            item['regist_time']=temp2.xpath('./li[9]/span[2]/text()')[0].extract()[:-6]
        yield item

    # 医生问诊页
    def parse_doc_consult_info(self,response):      
        item=response.meta['item']
        temp3=response.xpath('//*[@id="aside-container"]/div')
        if temp3==[]:
            item['cons_num']=''
            item['cons_satis']=''
            item['wait_time']=''
        elif temp3.xpath('./p[1]//text()')==[]:  # 总问诊量
            item['cons_num']=''
            item['cons_satis']=temp3.xpath('./p[2]/span[2]/text()')[0].extract() # 问诊服务满意度
            item['wait_time']=temp3.xpath('./p[3]/span[2]/text()')[0].extract() # 一般回复时长            
            pass
        else:
            item['cons_num']=temp3.xpath('./p[1]/span[2]/text()')[0].extract() # 总问诊量
            item['cons_satis']=temp3.xpath('./p[2]/span[2]/text()')[0].extract() # 问诊服务满意度
            item['wait_time']=temp3.xpath('./p[3]/span[2]/text()')[0].extract() # 一般回复时长
        yield scrapy.Request(url=item['doc_url'],callback=self.parse_doc_other_info,meta={'item':item})

    # 专家推荐页
    def parse(self, response):
        # xpath返回的是列表，但是列表元素一定是Selector类型的对象，extract可以将Selector对象中data参数存储的字符串提取出来
        # 列表调用了extract之后，则表示将列表中每一个Selector对象中data对应的字符串提取了出来
        ttemp=response.xpath('//div[@class="info-wrap"]')
        hos=ttemp.xpath('./div[1]/h1/text()')[0].extract()
        hos_label1=ttemp.xpath('./div[3]/span[1]/text()')[0].extract()
        hos_label2=ttemp.xpath('./div[3]/span[2]/text()')[0].extract()
        try:
            hos_label3=ttemp.xpath('./div[3]/span[3]/text()')[0].extract() #有的没有label3
        except:
            hos_label3=''

        li_list=response.xpath('//*[@id="me-content"]/ul/li') # 20个li标签里有20位医生
        for li in li_list:
             # 实例化一个item对象
            item=HaodfItem()
            item['hos']=hos
            item['hos_label1']=hos_label1
            item['hos_label2']=hos_label2
            item['hos_label3']=hos_label3
            
            #依次解析姓名、职称、科室
            item['name']=li.xpath('.//span[@class="name"]/text()')[0].extract()
            try:
                item['grade']=li.xpath('.//span[@class="grade"]/text()')[0].extract() #有的没有grade
            except:
                item['grade']=''
    
            hos_faculty = li.xpath('.//p[@class="hos-faculty"]/text()')[0].extract().strip()
            item['faculty']=hos_faculty.replace(hos+'\xa0 ','')  #
            try:
                item['faculty']=re.findall(' ([\u4e00-\u9fa5]+)',hos_faculty)[0]  # 小缺陷 同一医生可能不止在一个医院/科室
            except:
                item['faculty']=hos_faculty
            #依次解析疗效、态度、在线问诊、预约挂号、医生页面链接
            effi1=li.xpath('./a/div[2]/div[@class="other-info"]/div[1]/span[1]/text()')[0].extract().strip('主观疗效：')
            item['effi']=effi1.strip('满意')
            atti1=li.xpath('./a/div[2]/div[@class="other-info"]/div[1]/span[2]/text()')[0].extract().strip('态度：')
            item['atti']=atti1.strip('满意')
            item['consult']=li.xpath('./a/div[2]/div[@class="other-info"]/div[2]/span[1]/span/text()')[0].extract()
            item['register']=li.xpath('./a/div[2]/div[@class="other-info"]/div[2]/span[2]/span/text()')[0].extract()
            item['recom']=li.xpath('./a/div[3]/span[2]/span[@class="score"]/text()')[0].extract()
            item['doc_url']=li.xpath('./a/@href')[0].extract() 
            item['docId']=re.findall('\d+',item['doc_url'])[0]
            consult_url=item['doc_url'].replace('.html','/bingcheng.html?type=all')
            yield scrapy.Request(url=consult_url,callback=self.parse_doc_consult_info,meta={'item':item})

