import random
from config import *
from dataset_generator import generate
from algo1_linear import linear_search
from algo2_binary import preprocess_sort, binary_search_rec
from algo3_hash import HashTable

header()
ok_all = True
for n in SIZES:
    data = generate(n)
    s = preprocess_sort(data)
    h = HashTable(n).build(data)
    ref = set(data)
    rng = random.Random(SEED)
    keys = [REG_NO, REG_NO + 1, data[0], data[-1], s[n // 2]]
    keys += rng.sample(data, 20) + [rng.randrange(0, 10**10) for _ in range(20)]
    ok = True
    for k in keys:
        e = k in ref
        i1, _ = linear_search(data, k)
        i2, _ = binary_search_rec(s, k)
        f3, _ = h.search(k)
        r = ((i1 != -1) == e) and ((i2 != -1) == e) and (f3 == e)
        if e:
            r = r and data[i1] == k and s[i2] == k
        ok &= r
        if k in (REG_NO, REG_NO + 1):
            print(f"n={n:>8} key={k} expected={'FOUND' if e else 'NOT FOUND'} linear={i1 != -1} binary={i2 != -1} hash={f3} -> {'PASS' if r else 'FAIL'}")
    print(f"n={n:>8} all {len(keys)} test cases: {'PASS' if ok else 'FAIL'}")
    ok_all &= ok
print("OVERALL:", "PASS" if ok_all else "FAIL")
