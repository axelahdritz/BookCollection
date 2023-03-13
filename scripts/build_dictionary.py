import json

with open('/Users/axelahdritz/coding_projects/BookCollection/dictionaries/swe/lower/dev.jsonl', 'r', encoding='utf-8') as f:
    json_list = list(f)

text = []
for json_str in json_list:
    json_dic = json.loads(json_str)
    token_lst = json_dic['tokens']
    t = ' '.join(token_lst)
    text.append(t)

with open('/Users/axelahdritz/coding_projects/BookCollection/dictionaries/swe/lower/test.jsonl', 'r', encoding='utf-8') as f:
    json_list = list(f)

for json_str in json_list:
    json_dic = json.loads(json_str)
    token_lst = json_dic['tokens']
    t = ' '.join(token_lst)
    text.append(t)

with open('/Users/axelahdritz/coding_projects/BookCollection/dictionaries/swe/lower/train.jsonl', 'r', encoding='utf-8') as f:
    json_list = list(f)

for json_str in json_list:
    json_dic = json.loads(json_str)
    token_lst = json_dic['tokens']
    t = ' '.join(token_lst)
    text.append(t)

final = ' '.join(text)

with open('dictionaries/swe/full.txt', 'w', encoding='utf-8') as f:
    f.write(final)