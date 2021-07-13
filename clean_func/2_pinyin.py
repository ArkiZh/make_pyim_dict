from pypinyin import pinyin, load_phrases_dict, Style, load_single_dict
import pandas as pd
import jieba
# https://pypinyin.readthedocs.io/zh_CN/master/usage.html


def to_pinyin(words_iter):
    words = []
    error_words = []
    duoyin_flags_with_tone = []
    pinyin_with_tone = []
    duoyin_flags_without_tone = []
    pinyin_without_tone = []
    pinyin_dealed = []
    sure_flags = []
    for i, word in enumerate(words_iter):
        word_pinyin_with_tone = []
        word_pinyin_without_tone = []
        has_duoyin_with_tone = False
        has_duoyin_without_tone = False
        word_pinyin_dealed = None
        word_error_flag = False
        sure_flag = 1
        for c in word:
            c_with_tone = pinyin(c, style=Style.TONE, heteronym=True, errors=lambda x: "ERROR")
            if c_with_tone[0] == "ERROR":
                word_error_flag = True
                continue
            if len(c_with_tone[0]) > 1:
                has_duoyin_with_tone = True
            word_pinyin_with_tone.extend(c_with_tone)

            c_without_tone = pinyin(c, style=Style.NORMAL, heteronym=True, errors=lambda x: "ERROR")
            if len(c_without_tone[0]) > 1:
                has_duoyin_without_tone = True
            word_pinyin_without_tone.extend(c_without_tone)

        if word_error_flag:
            print("ERROR: pinyin not found: {}".format(word))
            error_words.append(word)
            continue
        words.append(word)

        if not has_duoyin_without_tone:
            word_pinyin_dealed = "-".join([x[0] for x in word_pinyin_without_tone])
        else:
            # 匹配词库
            without_tone = pinyin(word, style=Style.NORMAL, heteronym=True)
            need_next = False
            for t in without_tone:
                if len(t) != 1:
                    need_next = True
            if not need_next:
                word_pinyin_dealed = "-".join([x[0] for x in word_pinyin_without_tone])
            # 匹配不上且长度大于4用jieba分词后匹配, 长度小于4还不唯一就不要了
            elif len(word) > 4:
                word_splits = jieba.cut(word, cut_all=False, HMM=True, use_paddle=False)
                tmp_pinyin = []
                skip = False
                for tmp_word in word_splits:
                    if len(tmp_word) >= 2:
                        tmp_word = pinyin(tmp_word, style=Style.NORMAL, heteronym=True)
                        for tmp1 in tmp_word:
                            if len(tmp1) > 1:
                                skip = True
                                break
                        if skip:
                            break
                        tmp_pinyin.extend(tmp_word)
                    else:
                        tmp_word = pinyin(tmp_word, style=Style.NORMAL, heteronym=True)
                        if len(tmp_word[0]) > 1:
                            skip = True
                            break
                        tmp_pinyin.extend(tmp_word)
                if not skip:
                    word_pinyin_dealed = "-".join([x[0] for x in word_pinyin_without_tone])

            if word_pinyin_dealed is None:
                if len(word) <= 4:
                    pinyin_not_sure = pinyin(word, style=Style.NORMAL, heteronym=False)
                    word_pinyin_dealed = "-".join([x[0] for x in pinyin_not_sure])
                    sure_flag = 0
                else:
                    sure_flag = -1
                    pinyin_not_sure = []
                    for tmp_word in jieba.cut(word, cut_all=False, HMM=True, use_paddle=False):
                        pinyin_not_sure.extend(pinyin(tmp_word, style=Style.NORMAL, heteronym=False))
                    word_pinyin_dealed = "-".join([x[0] for x in pinyin_not_sure])
                print("{:d} 多音不唯一词： [{}] -> {}".format(i, word, str(word_pinyin_dealed)))

        pinyin_with_tone.append(word_pinyin_with_tone)
        pinyin_without_tone.append(word_pinyin_without_tone)
        duoyin_flags_with_tone.append(has_duoyin_with_tone)
        duoyin_flags_without_tone.append(has_duoyin_without_tone)
        pinyin_dealed.append(word_pinyin_dealed)
        sure_flags.append(sure_flag)
    pinyin_info = pd.DataFrame({"word": words,
                                "pinyin_with_tone": pinyin_with_tone,
                                "pinyin_without_tone": pinyin_without_tone,
                                "duoyin_flag_with_tone": duoyin_flags_with_tone,
                                "duoyin_flag_without_tone": duoyin_flags_without_tone,
                                "pinyin_dealed": pinyin_dealed,
                                "sure_flag": sure_flags})
    return pinyin_info


words_info = pd.read_csv("./data/1_words_info.csv")
words_pinyin = to_pinyin(words_info["word"])

words_pinyin.to_csv("./data/2_words_pinyin.csv")

print("DONE.")
