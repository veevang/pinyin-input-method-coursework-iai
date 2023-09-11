import re
import json
import os


def generate_pinyin_character_table():
    """
    convert pinyin_character text file to a dictionary and save the characters in character.txt as a json file.
    :return:
    """
    # generate pinyin_character.json
    # every character should be in character.txt
    pinyin_character_dict = dict()
    with open("../data/pinyin_character.txt", "r") as txt_file, open("../data/character.txt", "r") as range_file:
        range_file_content = range_file.read()
        for row in txt_file:
            row_list = row.split()
            key = str(row_list[0])
            chars = row_list[1:]
            # chars in character.txt
            values = list()
            for char in chars:
                if char in range_file_content:
                    values.append(char)
                else:
                    continue
            pinyin_character_dict[key] = values
    with open("./pinyin_character.json", "w") as json_file:
        json.dump(pinyin_character_dict, json_file)


def generate_frequency_table(file_path, frequency_dict, mode):
    """
    convert the corpus into a frequency table.
    :param file_path:
    :param frequency_table_dict:
    :return:
    """
    with open(file_path, encoding='gbk') as file:
        text = file.read()

    # 要统计的频数分为：二字情况（二元语法）、单字情况
    if mode == "2":
        regular_expression = r'[\u4e00-\u9fa5]{2}'
        pattern = re.compile(regular_expression)
        matched_words = pattern.findall(text)
        for word in matched_words:
            if word in frequency_dict:
                frequency_dict[word] = frequency_dict[word] + 1
            else:
                frequency_dict[word] = 1
    elif mode == "1":
        regular_expression = r'[\u4e00-\u9fa5]'
        pattern = re.compile(regular_expression)
        matched_words = pattern.findall(text)
        for word in matched_words:
            if word in frequency_dict:
                frequency_dict[word] = frequency_dict[word] + 1
            else:
                frequency_dict[word] = 1
    elif mode == "^1":
        regular_expression = r'[^\u4e00-\u9fa5][\u4e00-\u9fa5]'
        pattern = re.compile(regular_expression)
        matched_words = pattern.findall(text)
        for word in matched_words:
            key = r'^' + word[1]
            if key in frequency_dict:
                frequency_dict[key] = frequency_dict[key] + 1
            else:
                frequency_dict[key] = 1


generate_pinyin_character_table()

# could be parallelized
count_dict_list = [dict() for _ in range(3)]
count_dict_name_list = ["two_char_word_count_table", "char_count_table", "beginning_char_count_table"]
mode_list = ["2", "1", "^1"]
for i in range(1, 13):
    file_path = f"../data/sina_news_gbk/2016-{str(i).rjust(2, '0')}.txt"
    if os.path.exists(file_path):
        print(f"start processing {i}")
        for count_dict, mode in zip(count_dict_list, mode_list):
            generate_frequency_table(file_path, count_dict, mode)
    else:
        continue

# log 所有的count
for count_dict, count_dict_name in zip(count_dict_list, count_dict_name_list):
    with open(f"./{count_dict_name}.json", "w") as file:
        json.dump(count_dict, file)

# 计算所有的 frequency
frequency_dict_name_list = ["two_char_word_frequency_table", "char_frequency_table", "beginning_char_frequency_table"]
frequency_dict_list = [dict() for _ in range(3)]

char_count_table = json.load(open(f"./char_count_table.json", "r"))
count_dict_list = []
# log 开头字频率和单字频率
for count_dict_name in count_dict_name_list:
    count_dict_list.append(json.load(open(f"./{count_dict_name}.json", "r")))

for frequency_dict, frequency_dict_name, count_dict, count_dict_name in zip(frequency_dict_list, frequency_dict_name_list, count_dict_list, count_dict_name_list):
    if count_dict_name == "char_count_table":
        denominator = sum(globals()["char_count_table"].values())
        for key in count_dict.keys():
            frequency_dict[key] = count_dict[key] / denominator
        with open(f"./{frequency_dict_name}.json", "w") as file:
            json.dump(frequency_dict, file)
    elif count_dict_name == "beginning_char_count_table":
        denominator = sum(count_dict.values())
        for key in count_dict.keys():
            frequency_dict[key] = count_dict[key] / denominator
        with open(f"./{frequency_dict_name}.json", "w") as file:
            json.dump(frequency_dict, file)
    elif count_dict_name == "two_char_word_count_table":
        for key in count_dict.keys():
            frequency_dict[key] = count_dict[key] / char_count_table[key[0]]
        with open(f"./{frequency_dict_name}.json", "w") as file:
            json.dump(frequency_dict, file)

frequency_dict_list = []
frequency_dict_name_list = ["two_char_word_frequency_table", "char_frequency_table", "beginning_char_frequency_table"]
merged_table = dict()
for frequency_dict_name in frequency_dict_name_list:
    merged_table = {**merged_table, **(json.load(open(f"./{frequency_dict_name}.json", "r")))}
json.dump(merged_table, open("./frequency_table.json", "w"))
