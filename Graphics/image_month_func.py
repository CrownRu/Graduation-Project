import psycopg2
from psycopg2 import Error
import datetime
import re
from collections import defaultdict
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta
import paramiko

###############################
#draw_combined_map_plot這個function為將4個資料來源(fb、ins、diary、txt)整合到combined_map中
#再根據combined_map的日期區分資料並畫出圖表
###############################
def draw_combined_map_plot(map1, map2, map3, map4, specific_date, n):
    combined_map = defaultdict(list)

    for date, values in map1.items():
        combined_map[date].extend(values)

    for date, values in map2.items():
        combined_map[date].extend(values)

    for date, values in map3.items():
        combined_map[date].extend(values)
    
    for date, values in map4.items():
        combined_map[date].extend(values)
    #print(combined_map)
    combined_map = dict(sorted(combined_map.items()))
    plt.figure(figsize=(10, 6))

    if n == 1:
        if specific_date in combined_map:
            times, scores = zip(*combined_map[specific_date])
            plt.plot(times, scores, marker='o', linestyle='-', linewidth=7)
            plt.xlabel('Time')
            plt.ylabel('Score')
            plt.title(f'Flows on {specific_date}')

            plt.tight_layout()
        else:
            print(f"No data available for {specific_date}")

###############################
#該檔案為週圖表只會進入以下48行的區塊，圖表是以當日往前推30天當作來源依據
###############################
    elif n > 1:
        start_date = datetime.strptime(specific_date, "%Y-%m-%d") - timedelta(days=n - 1)
        end_date = datetime.strptime(specific_date, "%Y-%m-%d")
        daily_average_scores = defaultdict(list)

        for date, values in combined_map.items():
            current_date = datetime.strptime(date, "%Y-%m-%d")
            if start_date <= current_date <= end_date:
                for _, score in values:
                    date_key = current_date.strftime('%m-%d')
                    daily_average_scores[date_key].append(score)

        if daily_average_scores:
            average_scores = [sum(scores) / len(scores) for scores in daily_average_scores.values()]
            dates = list(daily_average_scores.keys())
            #print(dates)
            plt.plot(dates, average_scores, linestyle='-', linewidth=7, color='#8b4513')
            #plt.xlabel('Date')
            #plt.ylabel('Average Score')
            #plt.title(f'Average Flows from {dates[0]} to {dates[-1]}')
            plt.gca().spines['top'].set_visible(False)
            plt.gca().spines['right'].set_visible(False)
            plt.axhline(y=0.5, color='red', linestyle='--')
            plt.axhline(y=0.6, color='green', linestyle='--')
            plt.xticks(dates[::5])
            plt.xticks(fontsize=25)
            plt.yticks(fontsize=20)
            plt.tight_layout()
        else:
            print(f"No data available for the past {n} days from {specific_date}")

    plot_object = plt.gcf()
    plt.close() 

    return plot_object

###############################
#參數為user的編號，利用sql將user的4個資料來源(fb、ins、diary、txt)取出放進各自的map中
###############################
def map_process(usernumber):
    #Diary
    usernumber=str(usernumber)
    diary_map = {}
    try:
        connection = psycopg2.connect(
            host="140.127.220.89",
            port="5432",
            database="postgres",
            user="postgres",
            password="CrownRu"
        )

        cursor= connection.cursor()
        diary_query = "SELECT * FROM \"diary\" d  WHERE d.user_number = "+usernumber+" order by d.diary_date, d.diary_time;"

        cursor.execute(diary_query)
        diary_rows = cursor.fetchall()

        for row in range(len(diary_rows)):
            date = str(diary_rows[row][3])
            time = str(diary_rows[row][4])
            score = float(diary_rows[row][5])
            if score == -1.0:
                continue
            else:
                if date in diary_map:
                    diary_map[date].append((time,score))
                else:
                    diary_map[date] = [(time, score)]
        #print(diary_map)

    except Error as e:
        print(f"Error while connecting to PostgreSQL: {e}")

    finally:
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

    #Facebook
    fb_map = {}
    try:
        connection = psycopg2.connect(
            host="140.127.220.89",
            port="5432",
            database="postgres",
            user="postgres",
            password="CrownRu"
        )

        cursor= connection.cursor()
        facebook_query = "SELECT * FROM \"facebook\" f WHERE f.user_number =  "+usernumber+"  order by f.fb_post_date, f.fb_post_time ;"

        cursor.execute(facebook_query)
        facebook_rows = cursor.fetchall()

        
        for row in range(len(facebook_rows)):
            date = str(facebook_rows[row][2])
            time = str(facebook_rows[row][3])
            score = float(facebook_rows[row][5])
            if score == -1.0:
                continue
            else:
                if date in fb_map:
                    fb_map[date].append((time,score))
                else:
                    fb_map[date] = [(time, score)]
        #print(fb_map)

    except Error as e:
        print(f"Error while connecting to PostgreSQL: {e}")

    finally:
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

    #instagram
    ig_map = {}
    try:
        connection = psycopg2.connect(
            host="140.127.220.89",
            port="5432",
            database="postgres",
            user="postgres",
            password="CrownRu"
        )

        cursor= connection.cursor()
        instagram_query = "SELECT * FROM \"instagram\" i WHERE i.user_number =  "+usernumber+"  order by i.ins_post_date, i.ins_post_time;"

        cursor.execute(instagram_query)
        instagram_rows = cursor.fetchall()

        
        for row in range(len(instagram_rows)):
            date = str(instagram_rows[row][3])
            time = str(instagram_rows[row][4])
            score = float(instagram_rows[row][2])
            if score == -1.0:
                continue
            else:
                if date in ig_map:
                    ig_map[date].append((time,score))
                else:
                    ig_map[date] = [(time, score)]
        #print(ig_map)

    

    except Error as e:
        print(f"Error while connecting to PostgreSQL: {e}")

    finally:
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

    #txt
    txt_map = {}
    try:
        connection = psycopg2.connect(
            host="140.127.220.89",
            port="5432",
            database="postgres",
            user="postgres",
            password="CrownRu"
        )

        cursor= connection.cursor()
        txt_query = "SELECT * FROM \"txt\" t WHERE t.user_number =  "+usernumber+"  order by t.txt_date, t.txt_time;" 

        cursor.execute(txt_query)
        txt_rows = cursor.fetchall()
        
        for row in range(len(txt_rows)):
            date = str(txt_rows[row][2])
            time = str(txt_rows[row][3])
            score = float(txt_rows[row][4])
            if score == -1.0:
                continue
            else:
                if date in txt_map:
                    txt_map[date].append((time,score))
                else:
                    txt_map[date] = [(time, score)]
        #print(txt_map)

        
    except Error as e:
        print(f"Error while connecting to PostgreSQL: {e}")

    finally:
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")
    return fb_map, ig_map, diary_map, txt_map


###############################
#image_month_function為主要運作的主要function，將圖表生成的圖片生成並上傳到主機
###############################
def image_month_function(user_number):
    current_date = datetime.today()
    current_date = current_date.strftime("%Y-%m-%d")
    try:
        connection = psycopg2.connect(
            host="140.127.220.89",
            port="5432",
            database="postgres",
            user="postgres",
            password="CrownRu"
        )

        cursor= connection.cursor()
        #usernumber_query = "SELECT u.user_number FROM \"user\" u order by u.user_number;"
        #cursor.execute(usernumber_query)
        #user_number_rows = cursor.fetchall()
        #for row in user_number_rows:
            #current_user_number=row[0]
            #print(current_user_number)
        map_process_rslt=map_process(user_number)
        rslt_plot = draw_combined_map_plot(*map_process_rslt, current_date, 30)
        imagefilename="user"+str(user_number)+"_"+str(current_date)+"_month.png"
        rslt_plot.savefig(imagefilename)

        hostname = "140.127.220.89"
        port = 22  
        username = "a1093364"
        password = "CrownRu"
        local_image_path = imagefilename
        remote_folder_path = "/var/www/html/image/"

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, port, username, password)

        sftp = ssh.open_sftp()
        sftp.put(local_image_path, remote_folder_path + str(imagefilename))
        print(str(imagefilename)+" success upload")

        sql="insert into \"image_info\"(\"image_name\",\"user_number\",\"type\",\"image_date\") values(%s,%s,%s,%s) ON CONFLICT (\"image_name\",\"user_number\",\"type\",\"image_date\") DO NOTHING"
        cursor.execute(sql,(imagefilename,user_number,"month",current_date))
        connection.commit()

        print(str(imagefilename)+" success stored in db")
    except Error as e:
        print(f"Error while connecting to PostgreSQL: {e}")

    finally:
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")
    #rslt_plot = draw_combined_map_plot(fb_map, ig_map, diary_map, txt_map, current_date, 30)
    #imagefilename=str(current_date)+"_month.png"
    #rslt_plot.savefig(imagefilename)
    sftp.close()
    ssh.close()