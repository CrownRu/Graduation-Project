from PIL import Image
import psycopg2
from datetime import datetime
from datetime import timedelta
import random
import paramiko

#### 建造全部使用者一年內的房子 ####
def builder(days, date):
    # 主機資訊
    hostname = "140.127.220.89"
    port = 22  
    username = "a1093364"
    password = "CrownRu"
    remote_folder_path = "/var/www/html/image/house/"

    # 資料庫連線
    connection = psycopg2.connect(
        host="140.127.220.89",
        port="5432",
        database="postgres",
        user="postgres",
        password="CrownRu"
    )
    cursor= connection.cursor()
    usernumber_query = "SELECT u.user_number FROM \"user\" u order by u.user_number;"
    cursor.execute(usernumber_query)
    user_number_rows = cursor.fetchall()
    for row in user_number_rows:
        current_user_number = row[0]
        print("="*30 + "\nuserNumber:" + str(current_user_number))
        map_process_rslt = builder_each_user(current_user_number, days, date) # 製作全部使用者情緒小屋
        imagefilename = "user" + str(current_user_number) + "_" + date + "_house.png"
        map_process_rslt.save(imagefilename)
        # 將圖片存入主機
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, port, username, password)
        sftp = ssh.open_sftp()
        sftp.put(imagefilename, remote_folder_path + str(imagefilename))
        print(str(imagefilename)+" success upload")

    # 連線關閉
    if connection:
        cursor.close()
        connection.close()
        print("+" * 50)
        print("PostgreSQL connection is closed")

    sftp.close()
    ssh.close()

# 建造一個使用者一周的房子
def builder_each_user(user_number, days, date):
    # 初始資料
    now = datetime.strptime(date, '%Y-%m-%d')
    brick_data_list = [] # [事件, 顏色, 分數] 讀資料庫
    brick_img_list = [] # 磚塊圖清單
    color_list = ['#FFD1A4', '#FFE153', '#FF8000', '#5CADAD', '#FFDC35', '#00EC00', '#62cf3a', '#9393FF', '#9AFF02', '#844200'] #磚塊顏色

    ######## 讀取資料庫 ########
    connection = psycopg2.connect(
        host = "140.127.220.89",
        port = "5432",
        database = "postgres",
        user = "postgres",
        password = "CrownRu"
    )

    #### facebook ####
    cursor = connection.cursor() 
    diary_query = "SELECT fb_post_date, avg(fb_post_scores) FROM facebook WHERE fb_post_scores != -1 AND user_number ="+ str(user_number) +"GROUP BY fb_post_date ORDER BY fb_post_date DESC"
    cursor.execute(diary_query)
    fb_rows = cursor.fetchall()
    fb_sum = 0.0
    fb_count = 0
    for row in fb_rows:
        if datetime.strptime(str(row[0]), "%Y-%m-%d") >= (now - timedelta(days = days-1)):
            fb_sum += float(row[1])
            fb_count += 1
    if fb_count != 0:
        brick_data_list.append(['facebook', '#3a6ecf', fb_sum/fb_count])

    #### instagram ####
    cursor = connection.cursor() 
    ig_query = "SELECT ins_post_date, avg(ins_post_scores) FROM instagram WHERE ins_post_scores != -1 AND user_number ="+ str(user_number) +"GROUP BY ins_post_date ORDER BY ins_post_date DESC"
    cursor.execute(ig_query)
    ig_rows = cursor.fetchall()
    ig_sum = 0.0
    ig_count = 0
    for row in ig_rows:
        if datetime.strptime(str(row[0]), "%Y-%m-%d") >= (now - timedelta(days = days-1)):
            ig_sum += float(row[1])
            ig_count += 1
    if ig_count != 0:
        brick_data_list.append(['instagram', '#e84c58', ig_sum/ig_count])

    #### line ####
    cursor = connection.cursor()
    line_query = "SELECT txt_date, avg(txt_score) FROM txt WHERE txt_score != -1 AND user_number ="+ str(user_number) +"GROUP BY txt_date ORDER BY txt_date DESC"
    cursor.execute(line_query)
    line_rows = cursor.fetchall()
    line_sum = 0.0
    line_count = 0
    for row in line_rows:
        if datetime.strptime(str(row[0]), "%Y-%m-%d") >= (now - timedelta(days = days-1)):
            line_sum += float(row[1])
            line_count += 1
    if line_count != 0:
        brick_data_list.append(['line', '#06c152', line_sum/line_count])

    #### diary ####
    cursor = connection.cursor()
    diary_query = "SELECT diary_date, avg(diary_score) FROM diary WHERE diary_score != -1 AND user_number ="+ str(user_number) +" GROUP BY diary_date ORDER BY diary_date DESC"
    cursor.execute(diary_query)
    diary_rows = cursor.fetchall()
    for row in diary_rows:
        if datetime.strptime(str(row[0]), "%Y-%m-%d") <= (now - timedelta(days = days-1)): #<變>
            brick_data_list.append(['diary', color_list[random.randint(1, len(color_list)-1)], float(row[1])])

    print("DB_data success")
    ######## 資料庫結束 ########

     ######## 製作表情磚塊(400X400)  ########
    for each in brick_data_list:
        # 確認表情級別
        try:
            if each[2] < 0.2:
                img_expression = Image.open('expression-1.png').convert('RGBA').resize((400, 400))
            elif 0.2 < each[2] <= 0.4:
                img_expression = Image.open('expression-2.png').convert('RGBA').resize((400, 400))
            elif 0.4 < each[2] <= 0.6:
                img_expression = Image.open('expression-3.png').convert('RGBA').resize((400, 400))
            elif 0.6 < each[2] <= 0.8:
                img_expression = Image.open('expression-4.png').convert('RGBA').resize((400, 400))
            elif 0.8 < each[2] <= 1.0:
                img_expression = Image.open('expression-5.png').convert('RGBA').resize((400, 400))
            else:
                continue
        except:
            img_expression = Image.open('expression-1.png').convert('RGBA').resize((400, 400))
    
        # 確認資料來源(事件)決定顏色
        try:
            img_each_brick = Image.new( mode = 'RGBA', size = (400, 400), color = each[1])
        except:
            img_each_brick = Image.new( mode = 'RGBA', size = (400, 400), color = color_list[random.randint(1, len(color_list)-1)])
        
        img_brickline = Image.open('brickline.png').convert('RGBA').resize((400, 400))
        img_each_brick.paste(img_brickline, (0, 0), img_brickline) #貼上磚塊框線圖
        img_each_brick.paste(img_expression, (0, 0), img_expression) #貼上磚塊表情圖
        brick_img_list.append(img_each_brick)

    ######## 製作表情房子(2400X2400)  ########
    brick_location = [[400,1600], [1200,1600], [1600,1600], [400,1200], [1200,1200], [1600,1200], [400,800], [800,800], [1200,800], [1600,800]]
    img_house_name = 'house_1.png'
    # 建造房子
    img_house = Image.open(img_house_name).convert('RGBA').resize((2400, 2400))
    # 貼上磚塊
    random.shuffle(brick_img_list)
    for i in range(len(brick_img_list)):
        if i < 10:
            img_house.paste(brick_img_list[i], brick_location[i], brick_img_list[i])
    print("House_bulidering success")
    return img_house
    

##############################################################################################################
while 1:
    builder(1, "2023-12-11") #(days, date) 
