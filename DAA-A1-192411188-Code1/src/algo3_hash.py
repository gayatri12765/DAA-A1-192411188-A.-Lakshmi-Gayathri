# RegNo: 192411188 | Name: Lakshmi Gayathri
class HashTable:
    def __init__(self, n):
        self.m = 2 * n + 1
        self.t = [[] for _ in range(self.m)]

    def insert(self, key):
        self.t[key % self.m].append(key)

    def build(self, a):
        for k in a:
            self.insert(k)
        return self

    def search(self, key):
        c = 0
        for v in self.t[key % self.m]:
            c += 1
            if v == key:
                return True, c
        return False, c
