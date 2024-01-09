#################
#情緒分析模型訓練#
#################

from snownlp import sentiment
sentiment.train('neg.txt','pos.txt')
sentiment.save('emo.marshal')