import time
import datetime
import psycopg2
from datetime import datetime

############################
#新增每個USER的所有預設任務資料
############################
connection = psycopg2.connect(
        host="140.127.220.89",
        port="5432",
        database="postgres",
        user="postgres",
        password="CrownRu"
    )

current_date = datetime.today()
current_date = current_date.strftime("%Y-%m-%d")

cursor= connection.cursor()
usernumber_query = "SELECT u.user_number FROM \"user\" u order by u.user_number;"
cursor.execute(usernumber_query)
user_number_rows = cursor.fetchall()
for row in user_number_rows:
    current_user=row[0]
    sql="insert into \"daily_mission\"(\"user_number\",\"dm_login\",\"dm_daily_diary\",\"dm_diary\",\"dm_txt\",\"dm_report\",\"dm_facebook\",\"dm_instagram\",\"dm_date\") values(%s,%s,%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (\"user_number\",\"dm_date\") DO NOTHING"
    cursor.execute(sql,(current_user,False,0,False,0,False,False,False,current_date))
    connection.commit()

cursor.close()
connection.close()