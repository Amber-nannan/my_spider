import jieba
from jieba import analyse
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import random

#将存储的文本分词
def cut_text(store_path):
    f=open(store_path,'r',encoding='UTF-8')
    text=f.read() #从文件读取所有字符并将它们作为字符串返回
    cutted_words=jieba.cut(text)#返回的是一个生成器
    return cutted_words

def store_cut_text(textstore_path,cut_store_path):
        cutted_words=cut_text(textstore_path)
        f=open(cut_store_path,"w",encoding="utf-8")
        for w in cutted_words:
            f.write(w+"\n")
        f.close()

#剔除停用词
def del_stopwords(stopwords_path,cut_store_path):
    stopwords_list = [line.strip() for line in open(stopwords_path, 'r', encoding='utf-8').readlines()]  # 将停用词表转换成列表
    words_str = ''
    #下面把不在停用词表中的词语添加到这个字符串中，并用空白符分隔开;
    # 必须给个符号分隔开分词结果形成字符串，否则不能生成词云
    f=open(cut_store_path,"r",encoding='utf-8')
    w=f.readline()
    words_dir={}
    while w!="":
        if w.strip() not in stopwords_list:
            if w not in words_dir.keys():
                words_dir[w]=1
            else:
                words_dir[w]+=1
            words_str+=w
            words_str+=' '
        w=f.readline()
    set_lst=sorted(words_dir.items(),key= lambda item:item[1],reverse=True)    #按字典的值排序，返回一个二元元组的列表，元组第一个元素是关键字，第二个是值
    return words_str

#打印关键字
def keywords_delstop(s,n):#提取字符串s中tf*idf排名前n的n个关键词
    tfidf =analyse.extract_tags # 引入TF-IDF关键词抽取接口
    keywords=tfidf(s,n,withWeight=True)

    print("小太阳朋友圈的十大关键词是：")
    i=1
    while i<11:
        print(str(i) + "、" + keywords[i-1][0] )
        i+=1
    construct_lst=[]#根据tf*idf值构建新的字符串，使得tf*idf值大的词词频也大，以便生成词云图。因为词云会单纯依据词频来生成
    for keyword in keywords:
        num=round(keyword[1],2)*100  #根据tf-idf值确定词语在新字符串中的个数
        n=0
        while n<num:
            construct_lst.append(keyword[0])
            n+=1
    random.shuffle(construct_lst)#将原列表打乱
    construct_str=""
    for word in construct_lst:
        construct_str+=word
        construct_str+=" "
    return construct_str

#生成词云
def get_wordcloud(words_str,store_path):
    color_list=['firebrick','darkred','lightcoral','brown','red', 'peru','sienna','dimgrey','darkgrey']
    colormap=colors.ListedColormap(color_list)
    wc=WordCloud(font_path=r'.\res\simhei.ttf',  #指定字体路径
                 background_color='white',width=600,height=450,max_font_size=400,min_font_size=10,colormap=colormap)
    wc.generate(words_str)#生成词云
    wc.to_file(store_path)#将词云存储到指定路径
    plt.imshow(wc)#以图片形式显示词云
    plt.axis('off')#将图像坐标系关闭
    plt.show()

if __name__=='__main__': #F:\词云
    store_cut_text(r'F:\大众点评中评.txt',r'F:\大众点评中评切词后.txt')   #切词并存储切分的词语
    words_str=del_stopwords(r'F:\比赛\大创\词云\停用词.txt',r'F:\大众点评中评切词后.txt')  #删除停用词
    construct_str=keywords_delstop(words_str,180)   #使用tf-idf值排名前180的词语构造新字符串
    get_wordcloud(construct_str,r'F:\大众点评中评.jpg')  #用新字符串生成词云
