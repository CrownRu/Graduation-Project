########################################################
# 動態偵測資料庫並在DB name:facebook資料新增時給予心情分數 #
########################################################

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
    
fb_detect_first = connection.cursor()
fb_detect_query = "select count(*) from facebook where fb_post_scores is null"
fb_detect_first.execute(fb_detect_query)

fb_detect_first.close()
while(1):
    

    fb_detect = connection.cursor()
    fb_detect.execute(fb_detect_query)
    fb_now_number = fb_detect.fetchone()[0] # 每三秒讀取到的數量
    
    print("now:"+str(fb_now_number))
    if fb_now_number > 0:
        fb_for_rating_query = "select * from facebook where fb_post_scores = -2"
        fb_detect.execute(fb_for_rating_query)
        result = fb_detect.fetchall()
        update_count = len(result)
        
        for i in range(update_count):
            fb_id = result[i][0]
            fb_content = result[i][1]
            if fb_content != '':
                list = fb_content
                fb_score = round(detection(list), 2)
                update_score_query = "update facebook set fb_post_scores = " + str(fb_score) + " where fb_post_number = " + str(fb_id)
                fb_detect.execute(update_score_query)
                connection.commit()
            else:
                fb_score = -1
                update_score_query = "update facebook set fb_post_scores = " + str(fb_score) + " where fb_post_number = " + str(fb_id)
                fb_detect.execute(update_score_query)
                connection.commit()
                continue
    
        
    time.sleep(3)
    fb_detect.close()

