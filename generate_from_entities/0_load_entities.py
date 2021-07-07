
# Get file from: https://ai.tencent.com/ailab/nlp/zh/embedding.html
file_path = "E:/tmp/Tencent_AILab_ChineseEmbedding.txt"
write_path = "data/0_words_raw.txt"

ff = open(write_path, mode="w+", encoding="UTF-8", newline="\n")

with open(file_path, mode="r", encoding="UTF-8") as f:
    num = 0
    while True:
        cur_line = f.readline()
        if cur_line == "":
            print("END OF FILE")
            break

        if " " in cur_line:
            ind0 = cur_line.index(" ")
            part0 = cur_line[:ind0]
            tmp = cur_line[ind0+1:]
            try:
                ind1 = tmp.index(" ")
                part1 = tmp[:ind1]
                try:
                    float(part1)
                    ff.write(part0 + "\n")
                except Exception as e:
                    print("Skip: not correct.", num, e, cur_line)
            except Exception as e:
                print("Skip: ", str(e), cur_line)
        else:
            print("This line is odd. {}, {}".format(num, cur_line))

        num+=1


ff.close()
