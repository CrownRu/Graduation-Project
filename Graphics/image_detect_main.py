import psycopg2
import time
from image_week_func import image_week_function as week_function
from image_day_func import image_day_function as day_function
from image_month_func import image_month_function as month_function
from image_year_func import image_year_function as year_function

###############################
#該檔案為及時更新圖表檔案的偵測檔案，當db有資料變動會自動更新圖表，生成的function來自以下4個檔案
#1. image_day_func.py
#2. image_week_func.py
#3. image_month_func.py
#4. image_year_func.py
###############################
connection = psycopg2.connect(
    host="140.127.220.89",
    port="5432",
    database="postgres",
    user="postgres",
    password="CrownRu"
)

newest_user=-1
#####
detect_first= connection.cursor()
txt_query_null = "select count(*) from \"txt\" where \"txt_score\" is null"
fb_query_null = "select count(*) from \"facebook\" where \"fb_post_scores\" is null"
ins_query_null = "select count(*) from \"instagram\" where \"ins_post_scores\" is null"
diary_query_null = "select count(*) from \"diary\" where \"diary_score\" is null"

txt_query = "select count(*) from \"txt\" "
fb_query = "select count(*) from \"facebook\" "
ins_query = "select count(*) from \"instagram\"  "
diary_query = "select count(*) from \"diary\"  "
detect_first.execute(txt_query)
txt_first_number=detect_first.fetchone()[0]
print("txt first:"+str(txt_first_number))

detect_first.execute(fb_query)
fb_first_number=detect_first.fetchone()[0]
print("fb first:"+str(fb_first_number))

detect_first.execute(ins_query)
ins_first_number=detect_first.fetchone()[0]
print("ins first:"+str(ins_first_number))

detect_first.execute(diary_query)
diary_first_number=detect_first.fetchone()[0]
print("diary first:"+str(diary_first_number))

detect_first.close()

flag=False
while(1):
    detect = connection.cursor()
    detect.execute(txt_query)
    txt_now_number=detect.fetchone()[0]
    print("txt now:"+str(txt_now_number))
    if txt_now_number>txt_first_number:
        print("txt增加")
        print("等5秒")
        time.sleep(5)
        # null_detect=connection.cursor()
        # null_detect.execute(txt_query_null)
        # null_detect_number=null_detect.fetchone()[0]
        # if null_detect_number >=1:
        #     print("有空值等5秒")
        #     time.sleep(5)
        # null_detect.close()

        cursor= connection.cursor()
        newest_user_query = "SELECT t.user_number FROM \"txt\" t order by t.txt_number DESC LIMIT 1;"
        cursor.execute(newest_user_query)
        newest_user = cursor.fetchone()[0]
        cursor.close()

        week_function(newest_user)
        day_function(newest_user)
        month_function(newest_user)
        year_function(newest_user)
        txt_first_number=txt_now_number
        continue
    
    ###
    
    detect.execute(ins_query)
    ins_now_number=detect.fetchone()[0]
    print("ins now:"+str(ins_now_number))
    if ins_now_number>ins_first_number:
        print("ins增加")
        if flag==False:
            print("等120秒")
            time.sleep(120)
        flag=True
        # null_detect=connection.cursor()
        # null_detect.execute(ins_query_null)
        # null_detect_number=null_detect.fetchone()[0]
        # if null_detect_number >=1:
        #     print("有空值等5秒")
        #     time.sleep(5)
        # null_detect.close()

        cursor= connection.cursor()
        newest_user_query = "SELECT i.user_number FROM \"instagram\" i order by i.ins_post_number DESC LIMIT 1;"
        cursor.execute(newest_user_query)
        newest_user = cursor.fetchone()[0]
        cursor.close()

        week_function(newest_user)
        day_function(newest_user)
        month_function(newest_user)
        year_function(newest_user)
        ins_first_number=ins_now_number
        continue
    
    ###
    
    detect.execute(fb_query)
    fb_now_number=detect.fetchone()[0]
    print("fb now:"+str(fb_now_number))
    if fb_now_number>fb_first_number:
        print("fb增加")
        if flag==False:
            print("等120秒")
            time.sleep(120)
        flag=True
        # null_detect=connection.cursor()
        # null_detect.execute(fb_query_null)
        # null_detect_number=null_detect.fetchone()[0]
        # if null_detect_number >=1:
        #     print("有空值等5秒")
        #     time.sleep(5)
        # null_detect.close()

        cursor= connection.cursor()
        newest_user_query = "SELECT f.user_number FROM \"facebook\" f order by f.fb_post_number DESC LIMIT 1;"
        cursor.execute(newest_user_query)
        newest_user = cursor.fetchone()[0]
        cursor.close()

        week_function(newest_user)
        day_function(newest_user)
        month_function(newest_user)
        year_function(newest_user)
        fb_first_number=fb_now_number
        continue
    
    ###
    
    detect.execute(diary_query)
    diary_now_number=detect.fetchone()[0]
    print("diary now:"+str(diary_now_number))
    if diary_now_number>diary_first_number:
        print("diary增加")
        print("等5秒")
        time.sleep(5)
        # null_detect=connection.cursor()
        # null_detect.execute(diary_query_null)
        # null_detect_number=null_detect.fetchone()[0]
        # if null_detect_number >=1:
        #     print("有空值等5秒")
        #     time.sleep(5)
        # null_detect.close()

        cursor= connection.cursor()
        newest_user_query = "SELECT d.user_number FROM \"diary\" d order by d.diary_number DESC LIMIT 1;"
        cursor.execute(newest_user_query)
        newest_user = cursor.fetchone()[0]
        cursor.close()

        week_function(newest_user)
        day_function(newest_user)
        month_function(newest_user)
        year_function(newest_user)
        diary_first_number=diary_now_number
        continue
    detect.close()
    print("----------------------")
    time.sleep(3)
