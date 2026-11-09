import random
from bpe import BPETokenizer


class model:
    def __init__(self, num_merges=5):
        self.hashset=set()
        self.bpe = BPETokenizer(num_merges=num_merges)

    def train(self, datas: list[str]):
        datas = [i.replace('\n', '') for i in datas]
        for i in datas:
            self.hashset.add(i)
        self.bpe.train(datas)
        tokenized = [self.bpe.encode(d) for d in datas]

        ct = 2
        self.forward = {'\n': 1}
        self.backward = {1: '\n'}
        for line in tokenized:
            for tok in line:
                if tok not in self.forward:
                    self.forward[tok] = ct
                    self.backward[ct] = tok
                    ct += 1
        self.l = ct

        self.p = {}
        self.p1 = [[0 for _ in range(ct)] for _ in range(ct)]
        for line in tokenized:
            seq = [0, 0] + [self.forward[t] for t in line] + [1]
            for i in range(len(seq) - 2):
                a, b, c = seq[i], seq[i + 1], seq[i + 2]
                state = (a, b)
                if state not in self.p:
                    self.p[state] = [0] * self.l
                self.p[state][c] += 1
                self.p1[b][c] += 1

    def run(self):
        tries = 0
        while True:
            s = self._generate(200)
            tries += 1
            if s not in self.hashset or tries >= 200:
                self.hashset.add(s)
                print('- '+s)
                return s + '\n'
    def _generate(self, maxlen):
        s = ""
        state = (0, 0)
        while len(s) < maxlen:
            if state in self.p:
                counts = self.p[state]
            else:
                counts = self.p1[state[1]]
            nxt = random.choices(range(self.l), counts)[0]
            if nxt == 1:
                break
            tok = self.backward[nxt]
            print(tok, end="")
            s += tok
            state = (state[1], nxt)
        print()
        return s
