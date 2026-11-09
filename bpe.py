from collections import Counter


class BPETokenizer:
    def __init__(self, num_merges=300):
        self.num_merges = num_merges
        self.merges = []
        self.vocab = set()

    def _get_pairs(self, word):
        return zip(word[:-1], word[1:])

    def train(self, texts):
        words = []
        for text in texts:
            text = text.replace('\n', '')
            if text:
                words.append(list(text))
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
        word = list(text)
        for a, b, merged in self.merges:
            word = self._apply_merge(word, a, b, merged)
        return word
