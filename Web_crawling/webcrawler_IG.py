import time
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import psycopg2
import random

# IG爬蟲+存入資料庫
def reptile_IG(user_ID, user_url):
    print("=" * 50)
    print(user_ID)
    print(user_url)

    ######## 資料庫連線 ########
    connection = psycopg2.connect(
        host="140.127.220.89",
        port="5432",
        database="postgres",
        user="postgres",
        password="CrownRu"
    )
    cursor= connection.cursor() 

    ######## 登入資訊 ########
    account = "c1c2c3_c4c5c6_"
    password = "CrownRu"

    ######## 爬蟲開始 ########
    post_list = []
    link_list = []
    # 使用ChromeDriverManager自動下載Chromedriver
    driver = webdriver.Chrome(ChromeDriverManager().install())

    #### 進入登入頁面 ####
    login_url = "https://www.instagram.com/accounts/login/"
    driver.get(login_url)
    # 下滑使產生更多貼文區塊
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    time.sleep(1)
    # 填帳密並登入
    driver.find_element(By.NAME, "username").send_keys(account)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.XPATH, '//*[@id="loginForm"]/div/div[3]/button').click()
    time.sleep(5)

    #### 進入個人頁面找到每篇貼文連結 ####
    driver.get(user_url)
    time.sleep(10)
    # 下滑使產生更多貼文區塊
    for i in range(3):
        print("=" * 50)
        print(i+1)
        for j in range(2):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            print("SCROLL")
            time.sleep(1)
        time.sleep(1)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        # 找到個人頁面所有貼文
        soup_article = soup.find("article") 
        # 找到每篇貼文的連結
        soup_links = soup_article.find_all("a")
        
        for each in soup_links:
            each_link = "https://www.instagram.com/"+str(each.get('href'))
            if each_link not in link_list:
                link_list.append(each_link)
                print("success"+str(len(link_list)))
                print(each_link)

    #### 進入每篇貼文頁面 ####
    print("*" * 100)
    print("POST")
    for each_link in link_list:
        try:
            print(each_link)
            driver.get(each_link)
            time.sleep(0.5)
            each_post_soup = BeautifulSoup(driver.page_source, "html.parser")
            
            #找貼文內容
            article_section = str(each_post_soup.find("meta", property = "og:title").get("content"))
            post_article = article_section[article_section.index("Instagram: \"")+12: len(article_section)-1].replace("\n", "")

            #找貼文時間
            if(each_post_soup.find("time")):
                datetime_section = each_post_soup.find("time").get("datetime")
                post_date = datetime_section[0 : datetime_section.index("T")]
                post_time = datetime_section[datetime_section.index("T")+1 : datetime_section.index(".")]
            else:
                post_date = str(random.randint(2010, 2022)) +"-"+ str(random.randint(1, 12)) +"-"+ str(random.randint(1, 28))
                post_time = str(random.randint(10, 23)) +":"+ str(random.randint(1, 60)) +":"+ str(random.randint(1, 60))

            # 存入資料庫
            post_list.append([each_link, post_date, post_time, post_article])
            each_SQL = [post_date, post_time, post_article, user_ID]
        except:
            continue

        cursor.execute("INSERT INTO \"instagram\" (\"ins_post_date\", \"ins_post_time\", \"ins_post_content\", \"user_number\") VALUES (%s, %s, %s, %s) ON CONFLICT (\"user_number\", \"ins_post_date\", \"ins_post_time\") DO NOTHING", each_SQL)
        connection.commit()
        time.sleep(0.5)
        print(each_SQL)
        print("success"+str(len(post_list)))
        
    ######## 爬蟲結束 ########

    connection.close() 
    ######## 資料庫結束 ########

#############################################################################################

######## 讀取所有使用者 並執行爬蟲該使用者IG貼文 ########
while 1:
    connection = psycopg2.connect(
        host="140.127.220.89",
        port="5432",
        database="postgres",
        user="postgres",
        password="CrownRu"
    )
    cursor = connection.cursor()
    user_number_and_inslink_query = "SELECT u.user_number,u.ins_link FROM \"user\" u order by u.user_number;"
    cursor.execute(user_number_and_inslink_query)
    user_rows = cursor.fetchall()
    for row in user_rows:
        current_usernumber = row[0]
        current_inslink = row[1]
        print("user"+ str(current_usernumber))
        print("user"+ str(current_inslink))
        if "instagram" not in current_inslink:
            continue
        else:
            reptile_IG(current_usernumber, current_inslink) # 執行該使用者IG爬蟲

    cursor.close()
    connection.close()