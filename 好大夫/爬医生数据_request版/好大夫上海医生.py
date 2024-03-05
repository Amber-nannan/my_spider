from lxml import etree
import requests
import pandas as pd
import re
headers={
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
}
#if __name__=='__main__':

# 医院首页
def get_hos_info(hos_url):
    hos_page = requests.get(url=hos_url,headers=headers).text
    # 计算有推荐专家页面有多少页，医生数/20
    doc_num=re.findall('(\d+)位医生',hos_page)[0] # 或者用//div[@class='title-desc']/span[2]
    page_num=int(doc_num)//20+1

    tree0=etree.HTML(hos_page)
    hos_name=tree0.xpath('//div[@class="info-title"]/h1/text()')[0] #医院名称
    hos_label1=tree0.xpath('//span[@class="hospital-label-item"][1]/text()')[0]  # 公立
    hos_label2=tree0.xpath('//span[@class="hospital-label-item"][2]/text()')[0]  # 三甲
    hos_label3=tree0.xpath('//span[@class="hospital-label-item"][3]/text()')[0]  # 综合医院
    #'是否公立':hos_label1,'医院等级':hos_label2,'医院类型':hos_label3,
    return page_num,hos_name,hos_label1,hos_label2,hos_label3

#专家推荐页面
def expert_recom_page(hos_url,hos_name,page_num):
     for i in range(1,page_num+1):  #48
        indicator = 1 if i==1 else 0 
        # 专家推荐页面请求
        url=hos_url.replace('.html','/tuijian.html')
        tuijian= url if i==1 else url+'?p='+str(i)
        tuijian_page=requests.get(url=tuijian,headers=headers).text
        # 专家推荐页面解析数据，姓名、职称、科室
        tree1=etree.HTML(tuijian_page)
        name=tree1.xpath('//li[@class="item"]//span[@class="name"]/text()')
        grade1=tree1.xpath('//li[@class="item"]//span[@class="grade"]')
        grade2=[i.xpath('.//text()') for i in grade1]  
        grade=[ i[0] if i else '' for i in grade2]  #这一步为使标签即使为空，也能取到空值，从而方便存到列表中
        hos_faculty=tree1.xpath('//li[@class="item"]//p[@class="hos-faculty"]/text()')
        temp=[i.strip() for i in hos_faculty]
        faculty=[i.replace(hos_name+'\xa0 ','') for i in temp]

        #继续解析，包括疗效、态度、在线问诊、预约挂号、病友推荐度
        effi1=tree1.xpath('//div[@class="percent"]/span[1]/text()')
        effi2=[i.strip('主观疗效：') for i in effi1]
        effi=[i.strip('满意') for i in effi2]
        atti1=tree1.xpath('//div[@class="percent"]/span[2]/text()')
        atti2=[i.strip('态度：') for i in atti1]
        atti=[i.strip('满意') for i in atti2]
        consult=tree1.xpath('//div[@class="service"]/span[1]/span/text()')
        register=tree1.xpath('//div[@class="service"]/span[2]/span/text()')
        recom =tree1.xpath('//div[@class="tuijian-redu"]//span[2]/span[1]/text()')
        # 专家推荐页里的info放在df1里
        df1=pd.DataFrame({'姓名':name,'职级':grade,'科室':faculty,'医院':hos_name,'主观疗效满意度':effi,\
                          '态度满意度':atti,'在线问诊':consult,'预约挂号':register,'病友推荐度':recom})
        
        # 解析得到医生页面链接，并调用函数获取更多指标
        doctor_urls=tree1.xpath('//div[@id="me-content"]/ul//a/@href') # 医生页面链接
        df2=get_doc_other_info(doctor_urls)
        df3=get_doc_consult_info(doctor_urls)
        # 将指标合并、存储
        temp=df1.join(df3)
        df=temp.join(df2)
        df.to_csv(r'F:\医生基本信息(测试版).csv',mode='a',index=False,header=indicator,encoding='utf-8')

#医生首页
def get_doc_other_info(doc_urls):
    # 总患者数、评论数量、问诊记录数量
    visits=[]
    visits_yes=[]
    articles=[]
    patients=[]
    patients_after_diag=[]
    comments=[]
    gifts=[]
    last_online=[]
    regist_time=[]
    for doc_url in doc_urls:
        doc_page=requests.get(url=doc_url,headers=headers).text
        tree2=etree.HTML(doc_page)
        # !!!记得统一格式
        try:
            visit=tree2.xpath('//ul[@class="item-body"]/li[1]/span[2]//text()')[0].strip()#总访问量
            visits.append(visit)
            temp=tree2.xpath('//ul[@class="item-body"]/li[2]/span[2]//text()')[0]#昨日访问
            visit_yes=re.findall('(\d+)次',temp)[0]
            visits_yes.append(visit_yes)
            article=tree2.xpath('//ul[@class="item-body"]/li[3]/span[2]//text()')[0].strip('篇')#总文章数
            articles.append(article)
            patient=tree2.xpath('//ul[@class="item-body"]/li[4]/span[2]//text()')[0].strip('位')#总患者数
            patients.append(patient)
            patient_after_diag=tree2.xpath('//ul[@class="item-body"]/li[5]/span[2]//text()')[0].strip('位')#诊后报道患者
            patients_after_diag.append(patient_after_diag)
            comment=tree2.xpath('//ul[@class="item-body"]/li[6]/span[2]//text()')[0].strip('个')#诊后评论数量
            comments.append(comment)
            gift=tree2.xpath('//ul[@class="item-body"]/li[7]/span[2]//text()')[0].strip('个')#心意礼物
            gifts.append(gift)
            last=tree2.xpath('//ul[@class="item-body"]/li[8]/span[2]//text()')[0]#上次在线
            last_online.append(last)
            regist=tree2.xpath('//ul[@class="item-body"]/li[9]/span[2]//text()')[0][:-6]  #开通时间 2017-09-25 09: 18 只保留日期
            regist_time.append(regist)
        except:								
                visits.append('')
                visits_yes.append('')
                articles.append('')
                patients.append('')
                patients_after_diag.append('')
                comments.append('')
                gifts.append('')
                last_online.append('')
                regist_time.append('')

    df2=pd.DataFrame({'总访问量':visits,'昨日访问':visits_yes,'总文章数':articles,'总患者数':patients,'诊后报道患者':patients_after_diag,\
                        '诊后评论数量':comments,'心意礼物':gifts,'上次在线时间':last_online,'开通时间':regist_time})
    return df2

#医生问诊页面
def get_doc_consult_info(doc_urls):
    consult_num=[]
    consult_satis=[]
    wait_time=[]
    for doc_url in doc_urls:
        consult_url=doc_url.replace('.html','/bingcheng.html?type=all')
        try:
            consult_page=requests.get(headers=headers,url=consult_url).text
            tree3=etree.HTML(consult_page)
            a=tree3.xpath('//div[@id="aside-container"]/div/p[1]/span[2]/text()')[0] # 总问诊量
            b=tree3.xpath('//div[@id="aside-container"]/div/p[2]/span[2]/text()')[0]# 问诊服务满意度
            c=tree3.xpath('//div[@id="aside-container"]/div/p[3]/span[2]/text()')[0] # 一般回复时长
            consult_num.append(a)
            consult_satis.append(b)
            wait_time.append(c)
        except:
            consult_num.append('')
            consult_satis.append('')
            wait_time.append('')
    df3=pd.DataFrame({'总问诊量':consult_num,'问诊服务满意度':consult_satis,'一般回复时长':wait_time})
    return df3


if __name__=='__main__':
    # 测试一下
    hos_url='https://www.haodf.com/hospital/471.html'
    hos_name='上海交通大学医学院附属仁济医院（东院）'
    page_num=1
    expert_recom_page(hos_url,hos_name,page_num)
    # 测试出来代码没问题，但跑得有点慢，所以写了另一个scrapy版本的代码