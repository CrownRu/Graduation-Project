#################################################################
# 動態偵測資料庫並在DB name:txt(Line聊天紀錄)資料新增時給予心情分數 #
#################################################################

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
ws_driver = CkipWordSegmenter(model="bert-base", device=-1)
pos_driver = CkipPosTagger(model="bert-base", device=-1)
ner_driver = CkipNerChunker(model="bert-base", device=-1)
print("Initializing drivers ... all done")

def clean(sentence_ws, sentence_pos):
    short_with_pos = []
    short_sentence = []
    #contain_pos = set(['Nv', 'Da', 'A', 'VHC', 'VA', 'VB', 'VF', 'VK', 'Na']) 
    contain_pos = set(['Nc', 'VH', 'VE', 'VJ','VC','Ng','VCL','VA','VG','VK','VB','VHC','Ncd','A','VD','VL','Nv','Dfb','Neqb','VAC','VI','D','VF']) 
    for word_ws, word_pos in zip(sentence_ws, sentence_pos):
        # 去掉某些詞性
        is_contain_pos = word_pos in contain_pos
        # 組成串列
        if is_contain_pos:
            short_with_pos.append(f"{word_ws}({word_pos})")
            short_sentence.append(f"{word_ws}")
    return (" ".join(short_sentence), " ".join(short_with_pos))

def detection(text):
    ws = ws_driver(text)
    pos = pos_driver(ws)
    ner = ner_driver(text)
    
    for sentence, sentence_ws, sentence_pos, sentence_ner in zip(text, ws, pos, ner):
        (short, res) = clean(sentence_ws, sentence_pos)
    total_score = 0
    score = -1
    str_short = short.split(' ')
    for word in str_short:
        if not word.strip():
            continue
        else:
            s1=SnowNLP(word)
            total_score+=s1.sentiments
        score=total_score/len(str_short)
    print("\n平均分數 : ")
    print(score)
    return score
    
txt_detect_first = connection.cursor()
txt_detect_query = "select count(*) from txt where txt_score=-2"
txt_detect_first.execute(txt_detect_query)

txt_detect_first.close()
while(1):
    
    txt_detect = connection.cursor()
    txt_detect.execute(txt_detect_query)
    txt_now_number = txt_detect.fetchone()[0] # 每三秒讀取到的數量
    
    print("now:"+str(txt_now_number))
    if txt_now_number > 0:
        txt_for_rating_query = "select * from txt where txt_score is null"
        txt_detect.execute(txt_for_rating_query)
        result = txt_detect.fetchall()
        update_count = len(result)
        
        for i in range(update_count):
            txt_id = result[i][0]
            txt_content = result[i][1]
            list = [txt_content]
            # rate0 = detection(list)
            txt_score = round(detection(list), 2)
            update_score_query = "update txt set txt_score = " + str(txt_score) + " where txt_number = " + str(txt_id)
            txt_detect.execute(update_score_query)
            connection.commit()
        
    time.sleep(3)
    txt_detect.close()

