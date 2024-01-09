############################
#比較模型與其他模型判斷正確性#
############################

import openpyxl
from snownlp import SnowNLP
import numpy as np 
from scipy import stats

workbook = openpyxl.load_workbook('opinion_data.xlsx')
sheet = workbook.active

test_words = []
ref_value = []
for row in sheet.iter_rows(min_row=2, values_only=True):
    test_words.append(row[0])
    value = round((row[1]+1)/2,2)
    ref_value.append(value) 
    
#print(test_words)
#print(ref_value)
test_value=[]
for word in test_words:
    s=SnowNLP(word)
    print(word)
    print(s.sentiments)
    test_value.append(round(s.sentiments,2))
#print(test_value)

ref_value_array = np.array(ref_value)
test_value_array = np.array(test_value)

t_statistic, p_value = stats.ttest_ind(ref_value_array, test_value_array)

print("t-statistic:", t_statistic)
print("p-value:", p_value)

alpha = 0.05

if p_value < alpha:
    print("拒絕虛無假設，有差異。")
else:
    print("未拒絕虛無假設，無差異。")
