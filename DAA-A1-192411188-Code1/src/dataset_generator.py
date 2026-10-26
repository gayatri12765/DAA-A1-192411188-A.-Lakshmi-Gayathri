import random
from config import REG_NO, SEED

def generate(n):
    rng = random.Random(SEED + n)
    lo = max(0, REG_NO - 5 * n)
    pool = rng.sample(range(lo, lo + 10 * n), n + 2)
    pool = [x for x in pool if x not in (REG_NO, REG_NO + 1)][: n - 1]
    pool.append(REG_NO)
    rng.shuffle(pool)
    return pool

def make_queries(data, q=100):
    rng = random.Random(SEED)
    return [REG_NO, REG_NO + 1] + rng.sample(data, q - 2)

if __name__ == "__main__":
    from config import header, SIZES
    header()
    for n in SIZES:
        d = generate(n)
        with open(f"../data/records_{n}.txt", "w") as f:
            f.write("\n".join(map(str, d[:1000])))
        print(f"n={n}: generated, unique={len(set(d))}, contains REG_NO={REG_NO in d}, contains REG_NO+1={REG_NO + 1 in d}")
