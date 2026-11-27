s='''# MarkovedRyan100C
To gennerate rubbish sentences.
## 分词方式
- 非 ASCII 字符（汉字、全角标点、emoji 等）逐字切分。
- 半角字符（空格、数字、字母、英文标点）连成一体，仅在前一字符是空格、当前字符是英文字母处切开。
- 聚合后的单元再交给 BPE 合并（默认 5 次）。
## 生成指定长度的文本文件
手动运行 `gen.py`，可把模型生成的语段直接首尾相接（不加分隔符）拼接成长文本：
```
python gen.py 500              # 500 字节
python gen.py 700b             # 700 字节
python gen.py 1K               # 1024 字节（按 1024 进制）
python gen.py 1.5kb            # 1536 字节
python gen.py 800 --chars      # 800 个字符
python gen.py 500 -o out.txt   # 指定输出路径
```
- 默认按 UTF-8 字节数计量，`--chars` 改为按 Unicode 字符数计量（此时长度只写数字）。
- 输出文件名省略时自动命名为 `output_<长度>.txt`（字符模式为 `output_<长度>_chars.txt`）。
- 达到或略超目标长度即停止，整段追加，不会从中间截断。
- 该功能仅供手动调用，不参与自动化工作流。
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