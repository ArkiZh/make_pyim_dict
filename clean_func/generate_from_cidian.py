import re
from collections import OrderedDict

import pandas as pd

reg = re.compile("【([^【】·，…a-z0-9]+)】[0-9]?((（[^()]+）)|([(][^()]+[)]))?([1ɡαɑāáǎàōóǒòēéěèīíǐìūúǔùüǖǘǚǜa-z ∥·，•'’－\\-]+)", flags=re.IGNORECASE)
reg_line = re.compile("【[^【】]+】", flags=re.IGNORECASE)
words = []
chars = OrderedDict()
needs_review = []
with open("data/《现代汉语词典》第五版全本.txt", encoding="utf-8") as f:
    while True:
        line = f.readline()
        if line == "":
            break
        it = reg.match(line)
        if it:
            word, pinyin = it.groups()[0], it.groups()[-1]
            # 清理掉无用字符
            pinyin = re.sub("[ ∥·，•'’－\\-]", "", pinyin).lower()

            if re.fullmatch("[ɡαɑāáǎàōóǒòēéěèīíǐìūúǔùüǖǘǚǜa-z ∥·，•'’－\\-]+", line[(it.regs[-1][1] + 1):(it.regs[-1][1] + 3)]):
                if line[it.regs[-1][1]] in chars:
                    chars[line[it.regs[-1][1]]].append(line)
                else:
                    chars[line[it.regs[-1][1]]] = [line]
                print(pinyin, line)

            # 儿化音修改
            if word.endswith("儿") and pinyin.endswith("r"):
                if pinyin.endswith("r") and (not pinyin.endswith("er")):
                    words.append((word, pinyin[:-1] + "er"))
                else:
                    needs_review.append(line)
            else:
                words.append((word, pinyin))
        elif reg_line.match(line):
            needs_review.append(line)
            # print(line)

print("Words count:", len(words))
print("Need review count:", len(needs_review))

word_list = []
pinyin_list = []
pinyin_raw_list = []
result = OrderedDict()
for word, pinyin in words:
    # 拼音字符转字母
    if " " in word:
        print("Skip: ", word, pinyin)
        continue
    word_list.append(word)
    pinyin_raw_list.append(pinyin)
    pinyin = re.sub("[αɑāáǎà]", "a", pinyin)
    pinyin = re.sub("[ōóǒò]", "o", pinyin)
    pinyin = re.sub("[ēéěè]", "e", pinyin)
    pinyin = re.sub("[īíǐì]", "i", pinyin)
    pinyin = re.sub("[ūúǔù]", "u", pinyin)
    pinyin = re.sub("[üǖǘǚǜ]", "v", pinyin)
    pinyin = pinyin.replace("ɡ", "g")
    if "1" in pinyin:
        if pinyin.endswith("1"):
            print("CARE:", word, pinyin, line)
            pinyin = pinyin[:-1]
        else:
            pinyin = pinyin.replace("1", "l")
    pinyin_list.append(pinyin)
#     if pinyin not in result:
#         result[pinyin] = [word]
#     else:
#         result[pinyin].append(word)
#
# output_pyim = "./data/XianDaiHanYuCiDian.pyim"
# with open(output_pyim, mode="w+", encoding="UTF-8", newline="\n") as f:
#     f.write(";; -*- coding: utf-8-unix; -*-\n")
#     for k, v in result.items():
#         f.write("{} {}\n".format(k, " ".join(v)))

df_words = pd.DataFrame({"word": word_list, "pinyin": pinyin_list, "pinyin_raw": pinyin_raw_list})
df_words.to_csv("./data/pinyin_from_cidian.csv", index=False)
print("Done.")
