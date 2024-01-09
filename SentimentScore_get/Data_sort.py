################
#Dataset filter#
################

import openpyxl


workbook = openpyxl.load_workbook('opinion_data.xlsx')
sheet = workbook.active

with open('pos.txt', 'w') as file_a, open('neg.txt', 'w') as file_b:

    for row in sheet.iter_rows(min_row=2, values_only=True):
        col3_value = row[2]  
        col5_value = row[4]  

        if col3_value > col5_value:
            word = row[0]  
            file_a.write(f"{word}\n")
        elif col5_value > col3_value:
            word = row[0]  
            file_b.write(f"{word}\n")


workbook.close()
