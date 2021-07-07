import pandas as pd

print("Reading...")
words_pinyin_origin = pd.read_csv("./data/2_words_pinyin.csv")

# ,word,pinyin_with_tone,pinyin_without_tone,duoyin_flag_with_tone,doyen_flag_without_tone,pinyin_dealed,sure_flag

print("Filtering...")
words_pinyin = words_pinyin_origin.loc[(words_pinyin_origin["pinyin_dealed"] != "ERROR")
                                       # & (words_pinyin_origin["word"].apply(len) >= 2)
                                       & (words_pinyin_origin["word"].apply(len) <= 6),
                                       ["word", "pinyin_dealed", "sure_flag"]]

del words_pinyin_origin

print("Selecting...")
words_pinyin_sure = words_pinyin.loc[words_pinyin["sure_flag"] == 1, ["word", "pinyin_dealed"]]
words_pinyin_ok = words_pinyin.loc[words_pinyin["sure_flag"] == 0, ["word", "pinyin_dealed"]]
words_pinyin_no = words_pinyin.loc[words_pinyin["sure_flag"] == -1, ["word", "pinyin_dealed"]]

print("Adding frequencies ...")
freq_df = pd.read_csv("./data/char_freq.csv")
freq_set = {k: v for k, v in zip(freq_df["char"], freq_df["freq"])}


def make_pyim_dict(pinyin_df, output_csv, output_pyim):
    pinyin_df["freq"] = pinyin_df["word"].apply(lambda x: sum([freq_set.get(c, 0) for c in x]))
    group = pinyin_df.groupby("pinyin_dealed")

    print("Aggregating words...")

    def agg_fun(df):
        return " ".join(df.sort_values(by="freq", ascending=False)["word"])

    word_series = group.apply(agg_fun)
    result_df = group.aggregate({"freq": "mean"})
    result_df["words"] = word_series
    result_df = result_df.reset_index()
    result_df["len"] = result_df["pinyin_dealed"].transform(lambda x: len(x.split("-")))

    print("Sorting...")
    result_df.sort_values(by=["len", "freq"], ascending=[True, False], inplace=True)
    result_df.reset_index(drop=True, inplace=True)
    print("Writing...")
    result_df.to_csv(output_csv)

    with open(output_pyim, mode="w+", encoding="UTF-8", newline="\n") as f:
        f.write(";; -*- coding: utf-8-unix; -*-\n")
        for k, v in zip(result_df["pinyin_dealed"], result_df["words"]):
            f.write("{} {}\n".format(k, v))
    print("Done.")


make_pyim_dict(pinyin_df=words_pinyin_sure, output_csv="./data/3_pinyin_merged_sure.csv", output_pyim="./data/pyim_sure.pyim")


