import csv, time, random
from config import *
from dataset_generator import generate
from algo1_linear import linear_search
from algo2_binary import preprocess_sort, binary_search_rec
from algo3_hash import HashTable

N, Q, QLIN = 1_000_000, 50_000, 200
header()
data = generate(N)
rng = random.Random(SEED)
found = [REG_NO] + rng.sample(data, Q // 2 - 1)
missing = [REG_NO + 1] + [rng.randrange(0, 10**10) for _ in range(Q // 2 - 1)]
queries = found + missing
rng.shuffle(queries)

t = time.perf_counter(); s = preprocess_sort(data); p_sort = time.perf_counter() - t
t = time.perf_counter(); h = HashTable(N).build(data); p_hash = time.perf_counter() - t

t = time.perf_counter(); cb = sum(binary_search_rec(s, k)[1] for k in queries); tb = time.perf_counter() - t
t = time.perf_counter(); ch = sum(h.search(k)[1] for k in queries); th = time.perf_counter() - t
t = time.perf_counter(); cl = sum(linear_search(data, k)[1] for k in queries[:QLIN]); tl = (time.perf_counter() - t) * Q / QLIN

rows = [
    ("Linear (extrapolated from %d searches)" % QLIN, 0.0, tl, cl / QLIN),
    ("Binary (sort once)", p_sort, tb, cb / Q),
    ("Hash (build once)", p_hash, th, ch / Q),
]
print(f"{N} records, {Q} searches | required rate: {Q/3600:.2f} searches/s")
print(f"{'Design':<42} {'Prep(s)':>9} {'50k total(s)':>13} {'Per search(us)':>15} {'Avg comps':>10} {'Prep+50k(s)':>12}")
for n_, p, tt, c in rows:
    print(f"{n_:<42} {p:>9.4f} {tt:>13.4f} {tt/Q*1e6:>15.3f} {c:>10.2f} {p+tt:>12.4f}")
with open("../results/task12.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["design", "preprocess_s", "total_50000_s", "per_search_us", "avg_comparisons", "prep_plus_total_s"])
    for n_, p, tt, c in rows:
        w.writerow([n_, round(p, 4), round(tt, 4), round(tt / Q * 1e6, 3), round(c, 2), round(p + tt, 4)])
