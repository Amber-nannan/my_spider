from cnsenti import Sentiment
import re
import pandas as pd

with open(r'F:\比赛\大创\词云\上财小太阳朋友圈.txt','r',encoding='utf-8') as f:
    temp=f.read()
ttemp=temp.replace('\u200b','')
pyqs=re.findall('2022年(\d+月\d+日).*\n([\s\S]*?)\s\n\n',ttemp)# [\s\S]* 匹配任意字符（包括换行符）
#--------------不重要----------------------------------------------------------------------------
# num_dict={}
# for pyq in pyqs:
#     date,text=pyq
#     if date not in num_dict.keys():
#         num_dict[date]=1
#     else:
#         num_dict[date]+=1
# data=pd.DataFrame(num_dict,index=[0])
# data.to_excel(r'F:\比赛\大创\词云\num.xlsx')
#-------------不重要----------------------------------------------------------------------------

# 计算情感分析的得分
senti = Sentiment()
pyq_senti={}
for pyq in pyqs:
    date,text=pyq
    result=senti.sentiment_count(text)
    if result['sentences']==0:# 正则表达式匹配时有一点小瑕疵，导致极少量text是空值，若为空值跳过此次循环
        continue
    score=(result['pos']+(-1)*result['neg'])/result['sentences']
    if date not in pyq_senti.keys():
        pyq_senti[date]=score
    else:
        pyq_senti[date]+=score
    print(date)
data=pd.DataFrame(pyq_senti,index=[0])
data.to_excel(r'F:\比赛\大创\词云\情感分析结果.xlsx')
print(data)
