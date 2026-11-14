from collections import Counter


class BPETokenizer:
    def __init__(self, num_merges=300):
        self.num_merges = num_merges
        self.merges = []
        self.vocab = set()

    def _get_pairs(self, word):
        return zip(word[:-1], word[1:])

    def pre_tokenize(self, text):
        # 半角字符连成一体，仅在“前一个字符是空格、当前字符是英文字母”处断开；
        # 非 ASCII 字符（汉字、全角标点等）仍各自独立，其余一律不切。
        # 该步骤先于 BPE 合并，返回值即 BPE 的初始单元序列。
        units = []
        buf = []
        for i, ch in enumerate(text):
            if not ch.isascii():
                if buf:
                    units.append(''.join(buf))
                    buf = []
                units.append(ch)
                continue
            if ch.isalpha() and i > 0 and text[i - 1] == ' ':
                if buf:
                    units.append(''.join(buf))
                    buf = []
            buf.append(ch)
        if buf:
            units.append(''.join(buf))
        return units

    def train(self, texts):
        words = []
        for text in texts:
            text = text.replace('\n', '')
            if text:
                words.append(self.pre_tokenize(text))
        for w in words:
            self.vocab.update(w)

        for _ in range(self.num_merges):
            pair_counts = Counter()
            for w in words:
                for pair in self._get_pairs(w):
                    pair_counts[pair] += 1
            if not pair_counts or pair_counts.most_common(1)[0][1] < 2:
                break
            a, b = pair_counts.most_common(1)[0][0]
            merged = a + b
            self.merges.append((a, b, merged))
            self.vocab.add(merged)
            words = [self._apply_merge(w, a, b, merged) for w in words]

    def _apply_merge(self, word, a, b, merged):
        new_w = []
        i = 0
        while i < len(word):
            if i < len(word) - 1 and word[i] == a and word[i + 1] == b:
                new_w.append(merged)
                i += 2
            else:
                new_w.append(word[i])
                i += 1
        return new_w

    def encode(self, text):
        text = text.replace('\n', '')
        word = self.pre_tokenize(text)
        for a, b, merged in self.merges:
            word = self._apply_merge(word, a, b, merged)
        return word
