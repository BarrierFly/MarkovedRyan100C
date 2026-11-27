"""手动生成指定长度的文本文件。

用法示例：
    python gen.py 500            # 500 字节
    python gen.py 700b           # 700 字节
    python gen.py 1K             # 1 KiB = 1024 字节
    python gen.py 1.5kb          # 1.5 KiB = 1536 字节
    python gen.py 800 --chars    # 800 个字符
    python gen.py 500 -o out.txt # 指定输出路径

生成方式是不断调用模型，把得到的语段直接首尾相接（不加分隔符、不加前缀），
直到总长度达到或略超目标为止（整段追加，不会从中间截断）。
"""

import argparse
import os
import re
import sys

import markov

DATA_FILE = "Ryan100C_datas.txt"

_LENGTH_RE = re.compile(r"(\d+(?:\.\d+)?)(b|k|kb|kib)?")
_SUFFIX_FACTOR = {None: 1, "b": 1, "k": 1024, "kb": 1024, "kib": 1024}


def _script_dir():
    return os.path.dirname(os.path.abspath(__file__))


def parse_length(text):
    """把 '500'、'700b'、'1K'、'1.5kb' 解析成 (单位数, 归一化名称, 是否带单位后缀)。

    带 k/kb/kib 后缀时按 1024 进制换算；不带后缀时数值保持不变。
    """
    spec = text.strip().lower().replace(" ", "")
    m = _LENGTH_RE.fullmatch(spec)
    if not m:
        raise argparse.ArgumentTypeError(
            "无法识别的长度 %r，可用写法如 500、700b、1K、1.5kb" % text
        )
    number, suffix = m.group(1), m.group(2)
    value = int(float(number) * _SUFFIX_FACTOR[suffix])
    if value < 1:
        raise argparse.ArgumentTypeError("长度必须大于 0：%r" % text)
    name = number + (suffix or "")
    return value, name, suffix is not None


def measure(text, unit):
    return len(text) if unit == "chars" else len(text.encode("utf-8"))


def generate_text(model, target, unit, max_empty=1000):
    """反复生成语段并直接首尾相接，直到长度达到或略超 target。"""
    parts = []
    total = 0
    empty = 0
    while total < target:
        seg = model.run(echo=False)
        if seg.endswith("\n"):
            seg = seg[:-1]
        if not seg:
            empty += 1
            if empty >= max_empty:
                raise RuntimeError(
                    "连续 %d 次生成空语段，无法达到目标长度" % max_empty
                )
            continue
        empty = 0
        parts.append(seg)
        total += measure(seg, unit)
    return "".join(parts), len(parts)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="生成指定长度的马尔可夫文本文件（语段直接首尾相接）。"
    )
    parser.add_argument(
        "length",
        type=parse_length,
        help="目标长度，如 500、700b、1K、1.5kb；默认按 UTF-8 字节计",
    )
    parser.add_argument(
        "--chars",
        action="store_true",
        help="按 Unicode 字符数而不是 UTF-8 字节数计量",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="输出文件路径；省略时自动命名为 output_<长度>.txt",
    )
    args = parser.parse_args(argv)

    target, name, has_suffix = args.length
    if args.chars and has_suffix:
        parser.error("使用 --chars 时长度只写数字，不要带 b/K 等字节单位")
    unit = "chars" if args.chars else "bytes"

    output = args.output
    if not output:
        output = "output_%s%s.txt" % (name, "_chars" if args.chars else "")

    data_path = os.path.join(_script_dir(), DATA_FILE)
    if not os.path.exists(data_path):
        parser.error("找不到训练数据文件：%s" % data_path)

    model = markov.model()
    with open(data_path, encoding="utf-8") as f:
        model.train(f.readlines())

    text, seg_count = generate_text(model, target, unit)

    with open(output, "w", encoding="utf-8", newline="") as f:
        f.write(text)

    actual = measure(text, unit)
    unit_label = "字符" if unit == "chars" else "字节"
    print(
        "已写入 %s：%d %s（目标 %d %s，共拼接 %d 个语段）"
        % (output, actual, unit_label, target, unit_label, seg_count)
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
