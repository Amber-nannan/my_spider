from cnsenti import Emotion
import re
import pandas as pd

# 打开文件 并简单处理
with open(r'F:\比赛\大创\词云\疫情有关朋友圈.txt','r',encoding='utf-8') as f:
    temp1=f.read()
ttemp2=temp1.replace('\u200b','')
pyqs_cov=re.findall('(\d+月\d+日).*\n([\s\S]*?)\s\n\n',ttemp2)# [\s\S]* 匹配任意字符（包括换行符）

# 计算情绪得分
emotion = Emotion()
cov_emotion={}
for pyq_cov in pyqs_cov:
    date,text=pyq_cov
    result= emotion.emotion_count(text)
    del result['words']
    del result['sentences']
    if date not in cov_emotion.keys():
        cov_emotion[date]=result
    else:
        emo=['好','乐','哀','怒','惧','恶','惊']
        for e in emo:
            cov_emotion[date][e]+=result[e]
    print(date)

data=pd.DataFrame(cov_emotion)
data.to_excel(r'F:\比赛\大创\词云\情绪分析结果.xlsx')
print(data)
# 画图
