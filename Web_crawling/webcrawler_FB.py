import time
import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import psycopg2
import random

# FB爬蟲+存入資料庫
def reptile_FB(user_ID, page_url):
    ######## 資料庫連線 ########
    connection = psycopg2.connect(
        host="140.127.220.89",
        port="5432",
        database="postgres",
        user="postgres",
        password="CrownRu"
    )
    cursor= connection.cursor()

    #### 登入資訊 ####
    login_url = "https://facebook.com/"
    email = "CrownRu5566@gmail.com"
    password = "101213@RU"

    #### 網頁資訊 ####
    post_list = []

    #### 日期時間專區 ####
    now = datetime.datetime.today()
    now_year = now.year
    now_month = now.month
    now_day = now.day
    now_hour = now.hour
    now_minute = now.minute


    ######## 爬蟲開始 ########
    # 防止跳出通知
    chrome_options = webdriver.ChromeOptions()
    prefs = {
        "profile.default_content_setting_values.notifications": 2
    }
    chrome_options.add_experimental_option("prefs", prefs)
    # 自動下載Chromedriver
    driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options = chrome_options)

    #### 登入 ####
    driver.get(login_url)
    driver.find_element(By.ID, "email").send_keys(email)
    driver.find_element(By.ID, "pass").send_keys(password)
    driver.find_element(By.NAME, "login").click()
    time.sleep(3)

    #### 個人頁面 ####
    hasNextPage = True
    page_count = 1 #計算頁數
    
    while hasNextPage:
        # 進入個人頁面爬蟲
        driver.get(page_url)
        root = BeautifulSoup(driver.page_source, "html.parser")
        posts = root.find_all("article") #找到所有的貼文區塊

        # 處理每篇貼文
        for each_post in posts:
            not_share = each_post.find_all("footer") #過濾掉分享文章的貼文
            if not_share: 
                #### 找發文者 ####
                post_author = ""
                element_author= each_post.select_one('div:nth-of-type(1) header table tbody tr td:nth-of-type(2) header h3 strong:nth-of-type(1)')
                if element_author:
                    post_author = element_author.get_text() 
                
                #### 找貼文文字 ####
                post_article = ""
                element_article = each_post.select_one('div:nth-of-type(1)>div:nth-of-type(1)>div>span')
                if element_article:
                    post_article = element_article.get_text().replace("⋯⋯ 更多", "")
                else:
                    continue
                #### 找貼文時間 ####
                footer_section = each_post.find("footer")
                time_section = footer_section.find("abbr").text
                # 統一時間格式
                year = str(now_year)
                month = str(now_month)
                day = str(now_day)
                hour = str(now_hour)
                minute = str(now_minute)
                ## DATE ##
                try:
                    if "昨天" in time_section:
                        day = str(now_day - 1)
                    elif "年" not in time_section and "月" not in time_section and "日" in time_section: 
                        day = time_section[time_section.index("月")+1 : time_section.index("日")]
                    elif "年" not in time_section and "月" in time_section and "日" in time_section: 
                        month = time_section[0 : time_section.index("月")]
                        day = time_section[time_section.index("月")+1 : time_section.index("日")]
                    elif "年" in time_section and "月" in time_section and "日" in time_section: 
                        year = time_section[0 : time_section.index("年")]
                        month = time_section[time_section.index("年")+1 : time_section.index("月")]
                        day = time_section[time_section.index("月")+1 : time_section.index("日")]
                    #調整
                    if len(month) == 1:
                        month = "0" + month
                    if len(day) == 1:
                        day = "0" + day
                except:
                    year = str(random.randint(2010, 2022))
                    month = str(random.randint(1, 12))
                    day = str(random.randint(1, 28))
                ## TIME ##
                try:
                    if "小時" in time_section:
                        hour = str(now_hour - int(time_section[0 : time_section.index("小時")]))
                        if int(hour)<0:
                            hour=int(hour)
                            day=int(day)
                            hour=hour+24
                            day=day-1
                            hour=str(hour)
                            day=str(day)
                    else:
                        # Check AM/PM?
                        am_pm = time_section[time_section.index("午")-1 : time_section.index("午")+1]
                        if am_pm == "上午":
                            hour = time_section[time_section.index("午")+1 : time_section.index(":")]
                            if hour == "12": #檢查早上12點(凌晨0點)
                                hour = str(0)
                            if len(hour) == 1:
                                hour = "0" + hour
                        elif am_pm == "下午":
                            hour = str(int(time_section[time_section.index("午")+1 : time_section.index(":")]) + 12)
                            if hour == "24": #檢查下上12點(中午12點)
                                hour = str(12)
                        minute = time_section[time_section.index(":")+1 : len(time_section)]
                except:
                    hour = str(random.randint(10, 23))
                    minute = str(random.randint(1, 60))
                    
                # 整理日期、時間格式
                post_date = year + "-" + month + "-" + day
                post_time = hour + ":" + minute + ":00"
                
                #### 存入資料庫 ####
                post_list.append([post_author, post_date, post_time, post_article])
                each_SQL = [post_date , post_time, post_article, user_ID]
                cursor.execute("INSERT INTO \"facebook\" (\"fb_post_date\", \"fb_post_time\", \"fb_post_content\", \"user_number\") VALUES (%s, %s, %s, %s) ON CONFLICT (\"user_number\",\"fb_post_date\", \"fb_post_time\") DO NOTHING", each_SQL)
                connection.commit()
                print("success"+str(len(post_list)))
        #### 找到下一頁 ####
        time.sleep(3)
        if driver.find_element(By.LINK_TEXT, "查看更多動態"):
            page_url = driver.find_element(By.LINK_TEXT, "查看更多動態").get_attribute('href')
        else:
            hasNextPage = False
        page_count += 1 #頁數+1

    # 關閉瀏覽器
    driver.quit()
    ######## 爬蟲結束 ########

    connection.close()
    ######## 資料庫結束 ########


#############################################################################################

######## 讀取使用者清單 如有新增使用者 則執行爬蟲該使用者FB貼文 ########

#### 資料庫連線 ####
connection = psycopg2.connect(
        host="140.127.220.89",
        port="5432",
        database="postgres",
        user="postgres",
        password="CrownRu"
    )
#### 偵測新使用者 ####
message_count = 0
message_detect_first = connection.cursor()
message_detect_query = "select count(*) from \"user\""
message_detect_first.execute(message_detect_query)
message_first_number = message_detect_first.fetchone()[0]
message_count = message_first_number
print("first:" + str(message_first_number))
message_detect_first.close()
while(1):
    message_detect = connection.cursor()
    message_detect.execute(message_detect_query)
    message_now_number = message_detect.fetchone()[0]
    print("now:"+str(message_now_number))
    if message_now_number > message_count: # User增加
        print("資料增加")
        cursor = connection.cursor()
        user_number_and_inslink_query = "SELECT u.user_number,u.fb_link FROM \"user\" u order by u.user_number DESC LIMIT 1;"
        cursor.execute(user_number_and_inslink_query)
        user_rows = cursor.fetchall()
        for row in user_rows:
            print(row)
            current_usernumber = row[0]
            current_inslink = row[1]
            if current_inslink == "":
                continue
            if "mbasic." not in current_fblink:
                if "id=" in current_fblink:
                    current_fblink = "https://mbasic.facebook.com/" + current_fblink[current_fblink.find("id=")+3 : len(current_fblink)] + "?v=timeline"
                elif "facebook.com/" in current_fblink:
                    current_fblink = "https://mbasic.facebook.com/" + current_fblink[current_fblink.find("facebook.com/")+13 : current_fblink.find("?")] + "?v=timeline"
            reptile_FB(current_usernumber, current_fblink) 
    print("waiting...")
    time.sleep(3)
    message_detect.close()