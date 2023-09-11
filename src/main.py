# main
import argparse
import json
import numpy as np

frequency_table_header = ["character", "previous character", "frequency"]


class Node:
    def __init__(self, char, parent_index, accumulated_indicator):
        self.char = char
        self.parent_index = parent_index
        self.accumulated_indicator = accumulated_indicator
        return

    def __repr__(self):
        return self.char


def split_pinyin(input_str):
    pinyin_list = input_str.split()
    return pinyin_list


def smoothed_probability(target_char, frequency_table, *, previous_char=None, weight=0.95):
    """
    To get the smoothed probability of the target character on condition that the previous character is given,
    or to get the probability of the target character on condition that the previous one isn't given.
    :param frequency_table:
    :param target_char:
    :param previous_char:
    :param weight:
    :return:
    """

    # get data from char frequency table

    if previous_char is not None:
        # calculate conditional probability
        word = previous_char + target_char
    else:
        word = "^" + target_char

    if word in frequency_table:
        p_word = frequency_table[word]
    else:
        p_word = 0

    if target_char in frequency_table:
        p_char = frequency_table[target_char]
    else:
        p_char = 0

    return weight * p_word + (1 - weight) * p_char


# the core function of the assignment
def pinyin_to_sentence(pinyin_list, frequency_table, weight):
    """
    This function converts a pinyin_list to a Chinese sentence according to the selected method.
    :param pinyin_list: a list of pinyin's.
    :return: a string of the corresponding Chinese sentence of the input pinyin's.
    """
    n = len(pinyin_list)
    # 找到所有拼音对应的字，并建立成一张viterbi算法图的形式。
    with open("./pinyin_character.json", "r") as pinyin_character_file:
        pinyin_character_dict = json.load(pinyin_character_file)

    # possible_char[i][j] i represents the position, j represent different chars in the position.
    possible_char = [[] for _ in range(n)]
    for i in range(len(pinyin_list)):
        char_list_i = pinyin_character_dict[pinyin_list[i]]
        for char in char_list_i:
            possible_char[i].append(Node(char, np.infty, np.infty))
    # 图建构完成

    # 然后开始寻找最小路径，求min(-sum(log(P(w_i, w_i-1))))
    # 先处理i == 0的情况。
    # 需要注意，在第0个字时，需要计算非条件概率P(w_0)。
    for j in range(len(possible_char[0])):
        possible_char[0][j].accumulated_indicator = - np.log(
            smoothed_probability(possible_char[0][j].char, frequency_table, weight=weight))
        possible_char[0][j].parent_index = np.infty

    # 再处理i != 0的情况
    for i in range(1, n):
        for j in range(len(possible_char[i])):  # for each possible char in i-th position. target
            for k in range(len(possible_char[
                                   i - 1])):  # consider every possible parent to minimize the accumulated_indicator. previous
                accumulated_indicator_k = possible_char[i - 1][k].accumulated_indicator - np.log(
                    smoothed_probability(possible_char[i][j].char, frequency_table,
                                         previous_char=possible_char[i - 1][k].char, weight=weight))
                if accumulated_indicator_k < possible_char[i][j].accumulated_indicator:
                    possible_char[i][j].accumulated_indicator = accumulated_indicator_k
                    possible_char[i][j].parent_index = k

    # 考虑最后一个位置的字符的accumulated_indicator最小。
    accumulated_indicator_list = [possible_char[n - 1][j].accumulated_indicator for j in
                                  range(len(possible_char[n - 1]))]
    min_elem_index = accumulated_indicator_list.index(min(accumulated_indicator_list))

    # 从尾到头记录这些字符。
    parent_index = min_elem_index
    output_sentence = ""

    for i in range(n - 1, 0, -1):
        output_sentence = output_sentence + possible_char[i][parent_index].char
        # update parent_index
        parent_index = possible_char[i][parent_index].parent_index

    output_sentence = output_sentence + possible_char[0][parent_index].char

    output_sentence = output_sentence[::-1]

    return output_sentence


if __name__ == "__main__":

    # arg
    weight = 0.95

    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', type=str, help='Input file name')
    parser.add_argument('output_file', type=str, help='Output file name')
    args = parser.parse_args()
    input_file_name = args.input_file
    output_file_name = args.output_file

    pinyin_li = list()
    frequency_table = json.load(open("./frequency_table.json", "r"))
    with open(input_file_name, 'r') as input_file, open(output_file_name, 'w', encoding="utf-8") as output_file:
        # online, which is the scenario in reality
        for pinyin_line in input_file:
            pinyin_li = split_pinyin(pinyin_line)
            sentence = pinyin_to_sentence(pinyin_li, frequency_table, weight=weight)
            output_file.write(sentence + "\n")
