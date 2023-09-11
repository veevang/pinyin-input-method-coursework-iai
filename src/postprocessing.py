import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("refer", type=str, help="refer path.")
parser.add_argument("in_method_out", type=str, help="input method output path.")
args = parser.parse_args()
refer_path = args.refer
in_method_out_path = args.in_method_out

refer = open(refer_path, "r", encoding="utf-8")
in_method_out = open(in_method_out_path, "r", encoding="utf-8")

num_ceq = 0
num_cneq = 0
# char accuracy
while True:
    char1 = refer.read(1)
    char2 = in_method_out.read(1)
    # end of file
    if not char1 or not char2:
        break
    # 一定存在两个字符
    elif char1 == "\n" or char2 == "\n":
        continue
    # 一定存在两个汉字
    # 相等
    elif char1 == char2:
        num_ceq = num_ceq + 1
    # 不相等
    else:
        num_cneq = num_cneq + 1
print(f"char accuracy: {num_ceq / (num_ceq + num_cneq)}")


num_seq = 0
num_sneq = 0
# sentence accuracy
refer.close()
in_method_out.close()
refer = open(refer_path, "r", encoding="utf-8")
in_method_out = open(in_method_out_path, "r", encoding="utf-8")

while True:
    sen1 = refer.readline().strip()
    sen2 = in_method_out.readline().strip()
    # end of file
    if not sen1 or not sen2:
        break
    # 一定存在两句话
    # 相等
    elif sen1 == sen2:
        num_seq = num_seq + 1
    # 不相等
    else:
        num_sneq = num_sneq + 1
print(f"sentence accuracy: {num_seq / (num_seq + num_sneq)}")

if not os.path.exists("../log/"):
    os.mkdir("../log/")
accuracy_file = open("../log/accuracy.txt", "w+")
accuracy_file.write(f"char accuracy: {num_ceq / (num_ceq + num_cneq)}\n")
accuracy_file.write(f"sentence accuracy: {num_seq / (num_seq + num_sneq)}\n")
