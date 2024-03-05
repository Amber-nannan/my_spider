import requests
import pandas as pd
from lxml import etree
import re
import pdfkit
from pathlib import Path
# 发改委政策
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
}
    
# 获取规定时间内所有目标政策的基本信息
def get_pages(startDate,endDate,root_dir):
    excel_path=root_dir+'\\发改委政策汇编.xlsx'  
    if Path(excel_path).exists():
        df_obtained=pd.read_excel(excel_path)
        urls_obtained=df_obtained['网站链接'].values
    else:
        df_obtained=pd.DataFrame({'编号':[],'政策来源':[],'发文单位':[],'发文字号':[],'发文标题':[],
          '成文日期':[],'发布日期':[],'网站链接':[],'REITS相关主要内容':[]})
        urls_obtained=[]
    df=pd.DataFrame({'编号':[],'政策来源':[],'发文单位':[],'发文字号':[],'发文标题':[],
          '成文日期':[],'发布日期':[],'网站链接':[],'REITS相关主要内容':[]})
    page_url='https://fwfx.ndrc.gov.cn/api/query?qt=REITs&tab=all&page=1&pageSize=20&siteCode=bm04000fgk&key=CAB549A94CF659904A7D6B0E8FC8A7E9&startDateStr='+startDate+'&endDateStr='+endDate+'&timeOption=2&sort=dateDesc'
    response= requests.get(url=page_url,headers=headers).json()
    #计算页数
    totalHits=response['data']['totalHits'] 
    num=int(totalHits)//20+1 
    for i in range(num):
        if i==0:
            pass
        else:
            page_url='https://fwfx.ndrc.gov.cn/api/query?qt=REITs&tab=all&page='+str(i+1)+'&pageSize=20&siteCode=bm04000fgk&key=CAB549A94CF659904A7D6B0E8FC8A7E9&startDateStr='+startDate+'&endDateStr='+endDate+'&timeOption=2&sort=dateDesc'
            response= requests.get(url=page_url,headers=headers).json()
        resultList = response['data']['resultList']
        for result in resultList:
            if result['url'] not in urls_obtained:
                new_data=get_policy(result['url'],result['title'])
                df.loc[df.shape[0]]=new_data
        print('第'+str(i+1)+'页信息获取完毕')
    df= pd.concat([df_obtained, df], ignore_index=True)
    df.to_excel(excel_path,encoding='utf-8',index=False)
    print(excel_path,"保存成功")

# 获取某一条政策基本信息
def get_policy(policy_url,title): 
    response=requests.get(policy_url, headers=headers)
    text = response.content.decode('utf-8')
    tree=etree.HTML(text)
    source=tree.xpath('//div[@class="ly laiyuantext"]/span/text()')[0].strip('来源：')
    release_time=tree.xpath('//div[@class="time"]/text()')[0].strip('发布时间：').replace('/','-')
    
    # 以下三项只出现在通知里
    try:
        doc_number= re.findall('(?:通知|意见)\((.*\d+号)\)',title)[0]    # 发文字号
    except:
        doc_number=''
    try: #匹配以<br><br>或<br /><br />开头，并以xxxx年xx月xx日截尾的字符串
        temp=re.findall('(?:<br><br>|<br \/><br \/>)(.*)(\d{4})年(\d+)月(\d+)日',text)[0]   # 成文日期
        year=temp[1]
        month=temp[2].zfill(2)
        day=temp[3].zfill(2)
        date_of_writing=f'{year}-{month}-{day}'
    except:
        date_of_writing=''
    try:    
        result=re.findall('>([\u4e00-\u9fa5&emsp;]+)<',temp[0])  # 发文单位
        result=[item.replace('&emsp;','') for item in result]
        iss_authority='、'.join(result)
    except:
        iss_authority=''

    data={'编号':'','政策来源':source,'发文单位':iss_authority,'发文字号':doc_number,'发文标题':title,
          '成文日期':date_of_writing,'发布日期':release_time,'网站链接':policy_url,'REITS相关主要内容':''}
    return data

# 按发布日期排序得到编号，用编号命名下载pdf
def get_pdfs(root_dir):
    excel_path=root_dir+'\\发改委政策汇编.xlsx'
    df=pd.read_excel(excel_path)
    df.sort_values('发布日期',inplace=True)
    df.reset_index(drop=True,inplace=True)  
    df['编号']=["ndrcp_{:04d}".format(i + 1) for i in range(len(df))]
    filenames=df['编号']
    urls=df['网站链接']
    df.to_excel(excel_path,encoding='utf-8',index=False)
    # 电脑第一次用pdfkit要运行下面两行
    # path_wkthmltopdf = r'C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe'
    # config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
    for i in range(len(filenames)):
        filepath = root_dir+'\\'+filenames[i]+'.pdf'
        if not Path(filepath).exists():  # 检查是新增的才执行
            pdfkit.from_url(urls[i], filepath)
            print(filepath,"已保存")
    print(root_dir+'中PDF更新完毕')

if __name__ == '__main__':
    startDate = '2017-01-01'
    endDate = '2023-08-08'
    root_dir = 'C-REITs政策汇编\\发改委政策'
    get_pages(startDate,endDate,root_dir)   # 得到xlsx
    get_pdfs(root_dir)  # 得到pdfs