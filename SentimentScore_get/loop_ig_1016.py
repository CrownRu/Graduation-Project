#########################################################
# 動態偵測資料庫並在DB name:instagram資料新增時給予心情分數 #
#########################################################

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
    
ig_detect_first = connection.cursor()
ig_detect_query = "select count(*) from instagram where ins_post_scores=-2"
ig_detect_first.execute(ig_detect_query)

ig_detect_first.close()
while(1):
    
    ig_detect = connection.cursor()
    ig_detect.execute(ig_detect_query)
    ig_now_number = ig_detect.fetchone()[0] # 每三秒讀取到的數量
    
    print("now:"+str(ig_now_number))
    if ig_now_number > 0:
        ig_for_rating_query = "select * from instagram where ins_post_scores is null"
        ig_detect.execute(ig_for_rating_query)
        result = ig_detect.fetchall()
        update_count = len(result)
        
        for i in range(update_count):
            ig_id = result[i][0]
            ig_content = result[i][1]
            if ig_content != '':
                list = ig_content
                # rate0 = detection(list)
                ig_score = round(detection(list), 2)
                update_score_query = "update instagram set ins_post_scores = " + str(ig_score) + " where ins_post_number = " + str(ig_id)
                ig_detect.execute(update_score_query)
                connection.commit()
            else:
                ig_score = -1
                update_score_query = "update instagram set ins_post_scores = " + str(ig_score) + " where ins_post_number = " + str(ig_id)
                ig_detect.execute(update_score_query)
                connection.commit()
                continue
        
    time.sleep(3)
    ig_detect.close()

