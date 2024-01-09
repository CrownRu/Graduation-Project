################
#Dataset filter#
################

with open('neg.txt', 'r', encoding='utf-8') as file:
    lines = file.readlines()
    unique_words = list(set(lines))

with open('neg.txt', 'w') as file:
    file.writelines(unique_words)