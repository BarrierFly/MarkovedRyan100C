s='''# MarkovedRyan100C
To gennerate rubbish sentences.
## 分词方式
- 非 ASCII 字符（汉字、全角标点、emoji 等）逐字切分。
- 半角字符（空格、数字、字母、英文标点）连成一体，仅在前一字符是空格、当前字符是英文字母处切开。
- 聚合后的单元再交给 BPE 合并（默认 5 次）。
## Rubbish Of The Day
- '''
import sys
sys.path.append('.')
print(sys.path)
import markov
Ryan100C=markov.model()
with open("Ryan100C_datas.txt",encoding='utf-8') as f:
    Ryan100C.train(f.readlines())
s+='- '.join([Ryan100C.run() for i in range(100)])
print(s)
with open("./README.md","w",encoding="utf-8") as f:
    f.write(s)