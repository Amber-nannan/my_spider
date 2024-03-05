import requests
import pandas as pd
from lxml import etree
import re
import pdfkit
from pathlib import Path

# 深交所政策
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
}

# 获取规定时间内所有目标政策的基本信息
def get_pages(startDate,endDate,root_dir):
    excel_path=root_dir+'\\深交所政策汇编.xlsx'
    if Path(excel_path).exists():
        df_obtained=pd.read_excel(excel_path)
        urls_obtained=df_obtained['网站链接'].values
    else:
        df_obtained=pd.DataFrame({'编号':[],'类型':[],'发文单位':[],'发文字号':[],'发文标题':[],'发布日期':[],'网站链接':[],'REITS相关主要内容':[]})
        urls_obtained=[]
    df=pd.DataFrame({'编号':[],'类型':[],'发文单位':[],'发文字号':[],'发文标题':[],'发布日期':[],'网站链接':[],'REITS相关主要内容':[]})
    rules_url = 'http://reits.szse.cn/lawrule/bussrules/latest/index.html'
    rules_text = requests.get(rules_url, headers=headers).content.decode('utf-8')
    guide_url='http://reits.szse.cn/lawrule/bussrules/supervise/index.html'
    guide_text = requests.get(guide_url, headers=headers).content.decode('utf-8')
    a = re.findall('var curHref = \'\.(.*html)',rules_text)
    b = re.findall('var curHref = \'\.(.*html)',guide_text)
    urls = ['http://reits.szse.cn/lawrule/bussrules/latest'+i for i in a]+\
        ['http://reits.szse.cn/lawrule/bussrules/supervise'+j for j in b]
    for url in urls:
        if url not in urls_obtained:
            new_data = get_policy(url)
            df.loc[df.shape[0]]=new_data
    df= pd.concat([df_obtained, df], ignore_index=True)
    df.to_excel(excel_path,encoding='utf-8',index=False)
    print(excel_path,"保存成功")
    
# 获取某一条政策基本信息
def get_policy(policy_url): 
    if 'latest' in policy_url:
        type='业务规则'
    else:
        type='业务指南'
    text = requests.get(policy_url, headers=headers).content.decode('utf-8')
    tree=etree.HTML(text)
    title=tree.xpath('//h2[@class="title"]/text()')[0]
    date=tree.xpath('//div[@class="time"]/span/text()')[0]
    source='深交所'
    doc_number=''.join(tree.xpath('//div[@class="des-content"]/p[@class="MsoNormal"][1]/span//text()'))
    data={'编号':'','类型':type,'发文单位':source,'发文字号':doc_number,'发文标题':title,'发布日期':date,'网站链接':policy_url,'REITS相关主要内容':''}
    return data

# 编号
def number(x):
    x.sort_values('发布日期',inplace=True)
    x.reset_index(drop=True,inplace=True)
    if all(x['类型']=='业务规则'):
        x['编号']=['EP_SZSE_rule_{:04d}'.format(i + 1) for i in range(len(x))]
    else:
        x['编号']=['EP_SZSE_guide_{:04d}'.format(i + 1) for i in range(len(x))]
    return x

# 用编号命名下载pdf
def get_pdfs(root_dir):
    excel_path=root_dir+'\\深交所政策汇编.xlsx'
    df=pd.read_excel(excel_path)
    df=df.groupby(df['类型']).apply(number)
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
    startDate = '2021-01-01'
    endDate = '2023-08-08'
    root_dir = 'C-REITs政策汇编\\交易所政策\\深交所政策'
    get_pages(startDate,endDate,root_dir)   # 得到xlsx
    get_pdfs(root_dir)  # 得到pdfs
    # 目前上交所、深交所文件太少，只有一页，无法观察页数规律，startDate和endDate用不上，需要后面完善