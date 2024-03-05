import requests
import pandas as pd
from lxml import etree
import re
import pdfkit
from pathlib import Path
# 证监会政策
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
}

# 获取规定时间内所有目标政策的基本信息
def get_pages(startDate,endDate,root_dir):
    excel_path=root_dir+'\\证监会政策汇编.xlsx'  
    if Path(excel_path).exists():
        df_obtained=pd.read_excel(excel_path)
        urls_obtained=df_obtained['网站链接'].values
    else:
        df_obtained=pd.DataFrame({'编号':[],'政策来源':[],'发文标题':[],'发布日期':[],'网站链接':[],'REITS相关主要内容':[]})
        urls_obtained=[]
    df=pd.DataFrame({'编号':[],'政策来源':[],'发文标题':[],'发布日期':[],'网站链接':[],'REITS相关主要内容':[]})
    # 先计算规定时间内有多少页
    page_url = 'http://www.csrc.gov.cn/guestweb4/s?searchWord=REITs&column=%25E5%2585%25A8%25E9%2583%25A8&pageSize=10&pageNum=0&siteCode=bm56000001&sonSiteCode=&checkHandle=1&searchSource=0&govWorkBean=%257B%257D&sonSiteCode=&areaSearchFlag=-1&secondSearchWords=&topical=&docName=&label=&countKey=0&uc=0&left_right_index=0&searchBoxSettingsIndex=&manualWord=REITs&orderBy=1&startTime='+startDate+'&endTime='+endDate+'&timeStamp=0&strFileType=&wordPlace=0'
    page_text = requests.get(page_url, headers=headers).text
    num = int(re.findall('相关结果<span>(\d+)</span>个',page_text)[0])//10+1
    # 遍历所有目标页
    for i in range(num):
        if i==0:
            pass
        else:
            page_url = 'http://www.csrc.gov.cn/guestweb4/s?searchWord=REITs&column=%25E5%2585%25A8%25E9%2583%25A8&pageSize=10&pageNum='+str(i)+'&siteCode=bm56000001&sonSiteCode=&checkHandle=1&searchSource=0&govWorkBean=%257B%257D&sonSiteCode=&areaSearchFlag=-1&secondSearchWords=&topical=&docName=&label=&countKey=0&uc=0&left_right_index=0&searchBoxSettingsIndex=&manualWord=REITs&orderBy=1&startTime='+startDate+'&endTime='+endDate+'&timeStamp=0&strFileType=&wordPlace=0'
            page_text = requests.get(page_url, headers=headers).text
        tree=etree.HTML(page_text)
        urls = tree.xpath('//div[@class="bigTit clearfix"]/a[@data="证监会要闻"]/@href')+\
        tree.xpath('//div[@class="bigTit clearfix"]/a[@data="首页轮播图"]/@href')
        for url in urls:
            if url not in urls_obtained:
                new_data = get_policy(url)
                df.loc[df.shape[0]]=new_data
        print('第'+str(i+1)+'页信息获取完毕')
    df= pd.concat([df_obtained, df], ignore_index=True)
    df.to_excel(excel_path,encoding='utf-8',index=False) 
    print(excel_path,"保存成功")
    
# 获取某一条政策基本信息
def get_policy(policy_url): 
    text = requests.get(policy_url, headers=headers).content.decode('utf-8')
    tree=etree.HTML(text)
    title=tree.xpath('/html/body/div[4]/div/h2/text()')[0]
    temp=tree.xpath('//div[@class="info"]/p[@class="fl"]/text()')[0]
    date=re.findall('日期：(\d{4}-\d{2}-\d{2})',temp)[0]
    source=re.findall('来源：(.*)$',temp)[0]
    data={'编号':'','政策来源':source,'发文标题':title,'发布日期':date,'网站链接':policy_url,'REITS相关主要内容':''}
    return data

# 按发布日期排序得到编号，用编号命名下载pdf
def get_pdfs(root_dir):
    excel_path=root_dir+'\\证监会政策汇编.xlsx'
    df=pd.read_excel(excel_path)
    df.sort_values('发布日期',inplace=True)
    df.reset_index(drop=True,inplace=True)  
    df['编号']=["csrcp_{:04d}".format(i + 1) for i in range(len(df))]
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
    startDate = '2014-01-01'
    endDate = '2023-08-08'
    root_dir = 'C-REITs政策汇编\\证监会政策'
    get_pages(startDate,endDate,root_dir)   # 得到xlsx
    get_pdfs(root_dir)  # 得到pdfs