from webbrowser import get
from appium import webdriver
from selenium.webdriver.common.by import By
from appium.webdriver.extensions.android.nativekey import AndroidKey
import time
import re
desired_caps = {
    'platformName': 'Android',# 被测手机是安卓
    'deviceName': 'xxx',  #设备名
    'platformVersion': '10', # 手机安卓版本
    # 'appPackage': 'com.tencent.mm',  # apk包名
    # 'appActivity': 'com.tencent.mm.ui.LauncherUI',  # apk的launcherActivity
    'noReset': True,  # 不要重置App，每次运行脚本不用重复输入密码启动微信
    'unicodeKeyboard': True,  # 使用unicodeKeyboard的编码方式来发送字符串，输入中文时填True
    'resetKeyboard': True , # 执行完程序恢复原来输入法，将键盘给隐藏起来
    'automationName' : 'UiAutomator2'
}

driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)

# # 进入昵称为name的好友的朋友圈的点击逻辑
# def enter_pengyouquan(name):
#     time.sleep(1)
#     driver.find_element(By.ID, 'com.tencent.mm:id/j5t').click() #点击搜索图标
#     time.sleep(1)
#     driver.find_element(By.ID, 'com.tencent.mm:id/cd7').send_keys(name)  #输入搜索文字 
#     time.sleep(1)
#     driver.find_element(By.ID, 'com.tencent.mm:id/a27').click()  #点击第一个搜索结果
#     time.sleep(1)
#     driver.find_element(By.ID, 'com.tencent.mm:id/eo').click()  #点击聊天界面右上角三个小点
#     time.sleep(1)
#     driver.find_element(By.XPATH, '/hierarchy/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.view.ViewGroup/android.widget.FrameLayout[2]/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.FrameLayout[1]/android.widget.RelativeLayout/android.widget.LinearLayout/android.widget.RelativeLayout/android.widget.ListView/android.widget.LinearLayout[1]/android.widget.RelativeLayout[1]/android.widget.ImageView').click() #点击头像
#     time.sleep(1)
#     driver.find_element(By.ID, 'com.tencent.mm:id/o8').click() #点击朋友圈


#上拉方法
def swipe_up(distance, time):  #distance为滑动距离，time为滑动时间
    width = 720
    height = 1552  # width和height根据不同手机而定  window_size = driver.get_window_size()
    try:
        driver.swipe(1 / 2 * width, 9 / 10 * height, 1 / 2 * width, (9 / 10 - distance) * height, time)
    except:
        pass

def get_one_moment():
    comments_text=''
    time.sleep(0.4)
    try:#防止一条朋友圈内容过长，日期在页面中不显示
        date=driver.find_element(By.ID,'com.tencent.mm:id/ng').get_attribute('text')
    except:
        swipe_up(8 / 10, 500)
        try:
            date=driver.find_element(By.ID,'com.tencent.mm:id/ng').get_attribute('text')
        except:
            swipe_up(8 / 10, 500)
            date=driver.find_element(By.ID,'com.tencent.mm:id/ng').get_attribute('text')
    content=driver.find_element(By.ID,'com.tencent.mm:id/c2h').get_attribute('text')
    while True:
        try:
            num=0   #新评论数量，如果小于5就不再swipe_up，这样做为了提升效率（一般一页都可以显示多于5条的评论
            comments=driver.find_elements(By.ID,'com.tencent.mm:id/m5')
            for e in comments:
                if e.get_attribute('text') not in comments_text:
                    comments_text += e.get_attribute('text')+'\n'
                    num +=1
            if num>=5 :
                swipe_up(8 / 10, 500)
            else:
                break
        except:
            break
    one_moment=date+' '+content+'\n'+comments_text
    driver.find_element(By.ID,'com.tencent.mm:id/g0').click()#退出该界面
    return one_moment

def get_onepage_moments():
    moments=[]
    onepage_moments_1=driver.find_elements(By.ID,'com.tencent.mm:id/c22')  #图片 视频
    onepage_moments_2=driver.find_elements(By.ID,'com.tencent.mm:id/c2h')  #纯文字 链接
    for e1 in onepage_moments_1[1:]:   #第一个元素忽略，是为了防止触发顶部上滑
        try:
            e1.click()  #点击某一条朋友圈
            moments.append(get_one_moment())
            time.sleep(0.2)
        except:
            time.sleep(1)
    for e2 in onepage_moments_2[2:]:
        try:
            e2.click()
            moments.append(get_one_moment())
            time.sleep(0.2)
        except:
             time.sleep(1)
    return moments

# 获得多少页的pages
def get_pages(page_num):
    for i in range(page_num):
        time.sleep(0.5)
        moments=get_onepage_moments()
        store_PYQText(moments,r'F:\比赛\大创\词云\小太阳朋友圈2.0.txt')
        swipe_up(17 / 20, 1000)
    return True               


#将朋友圈文本存储到指定路径
def store_PYQText(PYQ_list,store_path):  
    f = open(store_path, 'a', encoding='utf-8')
    for text in PYQ_list:
        f.write(text + '\n')
    f.close()

# #获取的朋友圈文本中的表情会转为[捂脸]、[笑哭]这种形式，将其删除
# def remove_icondesc(list, storepath):
#     f = open(storepath, 'a', encoding='utf-8')
#     patten = re.compile('\w+(?![\u4e00-\u9fa5]*])')  #匹配除表情文本外的所有文本
#     for s in list:
#         splitted_sentences = re.findall(patten, s)
#         for p in splitted_sentences:
#             f.write(p + '\n')
#     f.close()

# time.sleep(5)

if get_pages(200):
    print('Done!')
#store_PYQText(PYQ_list,r'F:\词云\上财小太阳完整朋友圈.txt')  #存储原始朋友圈
#remove_icondesc(PYQ_list, r'F:\词云\上财小太阳已处理.txt')  #存储删除表情文本和符号之后的朋友圈，为生成词云做准备
driver.quit()
 