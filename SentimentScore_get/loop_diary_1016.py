######################################################
# 動態偵測資料庫並在DB name:diary資料新增時給予心情分數 #
######################################################

import psycopg2
from ckip_transformers.nlp import CkipWordSegmenter, CkipPosTagger, CkipNerChunker
from snownlp import SnowNLP
import time

#連接資料庫
connection = psycopg2.connect(
    host="140.127.220.89",
    port="5432",
    database="postgres",
    user="postgres",
    password="CrownRu"
)

#每3秒偵測資料庫並在讀取到分數為空時分析資料並給予分數
def detection(text):
    s=SnowNLP(text)
    total_score=0
    for sentence in s.sentences:
        print(sentence,end=' ')
        s1=SnowNLP(sentence)
        print(s1.sentiments)
        total_score+=s1.sentiments
    if len(s.sentences) > 0:
        score=total_score/len(s.sentences)
    else:
        score=-1
    print("\n平均分數 : ")
    print(score)
    return score
    
diary_detect_first = connection.cursor()
diary_detect_query = "select count(*) from diary where diary_score is null"
diary_detect_first.execute(diary_detect_query)

diary_detect_first.close()
while(1):
    
    diary_detect = connection.cursor()
    diary_detect.execute(diary_detect_query)
    diary_now_number = diary_detect.fetchone()[0] # 每三秒讀取到的數量
    
    print("now:"+str(diary_now_number))
    if diary_now_number > 0:
        diary_for_rating_query = "select * from diary where diary_score is null"
        diary_detect.execute(diary_for_rating_query)
        result = diary_detect.fetchall()
        update_count = len(result)
        
        for i in range(update_count):
            diary_id = result[i][2]
            diary_content = result[i][0]
            list = diary_content
            diary_score = round(detection(list), 2)
            update_score_query = "update diary set diary_score = " + str(diary_score) + " where diary_number = " + str(diary_id)
            diary_detect.execute(update_score_query)
            connection.commit()
        
    time.sleep(3)
    diary_detect.close()

