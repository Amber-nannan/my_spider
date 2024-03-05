from lxml import etree
import requests
import pandas as pd
import re
headers={
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
}
def get_info(hospitalId,page_num,com_type):
    # 输入参数为医院的id，以及评论的页数
    for i in range(0,page_num):
        url='https://www.haodf.com/nhospital/pc/keshi/pingjia/ajaxGetAssessList'
        data={
            'hospitalId':int(hospitalId),
            'diseaseId':0,
            'hospitalFacultyId':'',
            'commentType':com_type,  # 1是好评，2是差评
            'page':i+1
        }
        
        response = requests.post(url=url,data=data,headers=headers)
        comments_info=response.json()['data']['commentInfoList']

        if com_type==1:
            fp=open(r'F:\好大夫好评.txt','a',encoding='utf-8')
        else:
            fp=open(r'F:\好大夫差评.txt','a',encoding='utf-8')
        for com in comments_info:
            comment=com['commentDesc']
            fp.write(comment)
        fp.close()

if __name__=='__main__':
    with open(r'F:\评论医院索引（南京）.txt','r',encoding='utf-8') as f:
        hos_list=f.readlines()
    for k in hos_list:
        hospitalId=k.strip()
        hos_url='https://www.haodf.com/hospital/'+hospitalId +'/pingjia.html'
        page_text = requests.get(url=hos_url,headers=headers).text
        
        # 实例化一个etree对象
        tree=etree.HTML(page_text)
        # 计算一家医院的评论页数
        num_good = tree.xpath('//div[@class="left-cont"]//div[@class="good isCheck"]/text()')[0]
        num1=int(re.findall(' \d+',num_good)[0])//100  # 因为选取10%的评论，而每一页有10条评论
        num_bad = tree.xpath('//div[@class="left-cont"]//div[@class="bad"]/text()')[0]
        num2=int(re.findall(' \d+',num_bad)[0])//10    # 选取所有的评论，而每一页有10条评论
        get_info(hospitalId=hospitalId,page_num=num1,com_type=1)
        get_info(hospitalId=hospitalId,page_num=num2,com_type=2)
    