import requests
import re
import time
import random
#from parsel import Selector

def css_parser(css_url):
    css_cont = requests.get(css_url, headers=headers) # 访问css_url
    svg_url ="http:"+ re.findall('(//s3plus.meituan.net.*?svgtextcss.*?.svg)', css_cont.text)[0]
    css_list = re.findall('(ki\w+){background:.*?(-\d+).*?px.*?(-\d+).*?px;', '\n'.join(css_cont.text.split('}')))
    css_list = [(i[0], int(i[1]), int(i[2])) for i in css_list] #将字符串里的数字转为int类型
    # css_list内包含数据 如ej5qc{background:-392.0px -612.0px;}
    return svg_url,css_list

def svg_parser(svg_url):
    r = requests.get(svg_url, headers=headers)
    lines = re.findall('" y="(\d+)">(\w+)</text>', r.text, re.M) #这一句好像没有实际作用
    if not lines:
        lines = []
        z = re.findall('" textLength.*?(\w+)</textPath>', r.text, re.M)
        # z是具体行，例如：培刺绸狼经事微策皇龟乐遗鹿早贱君保路虹屡乘攀熄僚晃样望艺注府
        y = re.findall('id="\d+" d="\w+\s(\d+)\s\w+"', r.text, re.M)
        # y是例如id="1" d="M0 49 H600" 中的关键信息'49'（我们计算后需要与之比对）
        for a, b in zip(y, z):
            lines.append((a, b))
        # lines使计算的到的数值与具体行匹配
    width = re.findall("font-size:(\d+)px", r.text)[0]
    line_dict = []
    for i in lines:
        line_dict.append((int(i[0]), i[1])) # 主要变化是将'49'等转为int型
    return line_dict, int(width)

def font_parser(i,line_dict,width):  # i的结构如 ('ej5qc',-392,-612)
    for j in range(len(line_dict)):   #在79行里循环
        y = -i[2]+23
        if y == int(line_dict[j][0]):
            x = int(-i[1] / width)  #除以宽14得到x
            return line_dict[j][1][x]  # 返回的是一个汉字
    
def get_repl_dict(css_list,line_dict,width):
    replace_dic = {}
    for i in css_list: # i的结构如 ('ej5qc',-392,-612)
        replace_dic[i[0]]= font_parser(i,line_dict,width)
    return replace_dic # replace_dic 结构如{'yon75g':'好'}

def repl_svgmtis(source,replace_dic): # 传入全部评论页的源代码和替换字典
    for key,value in replace_dic.items():
        try:
            if key in source:
                old = '<svgmtsi class="'+key+'"></svgmtsi>'
                source = source.replace(old, value)
        except Exception as e:
            print(e)
    return source

def get_comment(source): 
    # response = Selector(text=source)
    # li_list = response.xpath('//div[@class="reviews-items"]/ul/li')
    # f=open(r'F:\大众点评评论.txt','a',encoding='utf-8')
    # for li in li_list:
    #     infof = li.xpath('.//div[@class="review-truncated-words"]/text()').extract()
    #     comment=infof[0].strip().replace("\n","")
    #     f.write(comment+'\n')
    # f.close()

    comment_list = re.findall('<div class="review-words Hide">(.*?)<div class="less-words">',source,re.S)
    f=open(r'F:\大众点评差评.txt','a',encoding='utf-8')
    for k in comment_list:
        pattern=re.compile('<.*?\>')
        kk=re.sub(pattern,'',k)#[^\u4e00-\u9fa5]+  
        kkk=re.sub('&#x.*;','',kk,re.S)
        comment=kkk.replace('\n','').strip()
        f.write(comment+'\n')
    f.close()

if __name__=="__main__":
    with open(r'F:\url_list.txt','r',encoding='utf-8') as f:
        url_list=f.readlines()  #要爬的网址列表
    new_list=[]
    for url in url_list:
        new_list.append(url.strip())
    for url in new_list:
        url+='/review_all/p5?queryType=reviewGrade&queryVal=bad'
        headers={
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
            'Cookie':'_lxsdk=184ac430236c8-047c2d5e66158b-977173c-144000-184ac430236bd; _lxsdk_cuid=184ac430236c8-047c2d5e66158b-977173c-144000-184ac430236bd; _hc.v=8fc83f60-2373-ac1b-9ea4-3b83ccf67a19.1669337384; WEBDFPID=3721238088y95204181v30240zyzzx57815zw77zuxw97958605u6240-1984712040627-1669352040208UMQKGIMfd79fef3d01d5e9aadc18ccd4d0c95071814; ua=hellochenst; ctu=9441ef90c3b39141b544ea94dd6f45596faa0994fcbcf34e47bba476f0c5b976; s_ViewType=10; cy=1; cye=shanghai; Hm_lvt_602b80cf8079ae6591966cc70a3940e7=1670379706,1670822054,1670864463,1671189905; _lx_utm=utm_source=bing&utm_medium=organic; fspop=test; qruuid=58c2e4bb-258f-4cbf-8d09-2a40054711b6; dplet=7477f16fa196f3c2f088c6e6982c0c5c; dper=882a1fd8ba42e1289d8393ca3163ab1dd06424b114f36996bca68e64adee1a0bf01a9c149bbda16edd05d6de73d76a877d3d3212d51525c6915a9cf579e24b9c; ll=7fd06e815b796be3df069dec7836c3df; Hm_lpvt_602b80cf8079ae6591966cc70a3940e7=1671190087; _lxsdk_s=1851aae3e00-c60-c78-685||362'
        }
        r = requests.get(url=url,headers=headers)
        a=re.findall('href="(//s3plus.meituan.net.*?svgtextcss.*?.css)', r.text)
        css_url = "http:" + re.findall('href="(//s3plus.meituan.net.*?svgtextcss.*?.css)', r.text)[0]
        time.sleep(random.randint(1,5))
        svg_url, css_list = css_parser(css_url) 
        time.sleep(random.randint(1,5))
        line_dict, width = svg_parser(svg_url)
        replace_dic = get_repl_dict(css_list,line_dict,width)
        new_source = repl_svgmtis(r.text,replace_dic)
        get_comment(new_source)
    

    
