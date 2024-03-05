# 读取疫情关键词、朋友圈的txt
with open(r'F:\比赛\大创\词云\疫情关键词.txt','r',encoding='utf-8') as f:
    filter=f.readlines()
with open(r'F:\比赛\大创\词云\上财小太阳朋友圈.txt','r',encoding='utf-8') as f:
    a=f.read()   #所有的放入一个字符串中
pyqs=a.split('2022年')  # b为列表，列表元素为一条pyq（含内容和评论）

# 筛选与疫情有关朋友圈并写入新txt
result=[]
for pyq in pyqs:
    temp=[s.strip() in pyq for s in filter]
    result.append(any(temp))
f=open('F:\比赛\大创\词云\疫情有关朋友圈.txt','a',encoding='utf-8')
for i in range(0,len(pyqs)):
    if result[i]:
        f.write(pyqs[i])
f.close()

input()

