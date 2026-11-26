"""DAA Assignment 3 - Q5, Q6, Q7 experiments. All numbers measured."""
import sys, random, time, statistics, math, tracemalloc
sys.setrecursionlimit(1000000)
random.seed(2026)

def timeit(f, reps=5, loops=1):
    ts = []
    for _ in range(reps):
        t = time.perf_counter()
        for _ in range(loops): f()
        ts.append((time.perf_counter() - t) / loops)
    return statistics.median(ts)

# ================= Q5 Closest pair =================
INF = float("inf")
def d2(p, q, c): c[0] += 1; return (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2
def brute(P, c):
    best = INF
    for i in range(len(P)):
        for j in range(i + 1, len(P)):
            v = d2(P[i], P[j], c)
            if v < best: best = v
    return best
def cp(Px, c):
    n = len(Px)
    if n <= 3: return brute(Px, c)
    mid = n // 2; midx = Px[mid][0]
    d = min(cp(Px[:mid], c), cp(Px[mid:], c))
    strip = sorted([p for p in Px if (p[0] - midx) ** 2 < d], key=lambda p: p[1])
    c[1] += len(strip)
    for i in range(len(strip)):
        for j in range(i + 1, len(strip)):
            if (strip[j][1] - strip[i][1]) ** 2 >= d: break
            v = d2(strip[i], strip[j], c)
            if v < d: d = v
    return d
def closest(P, c): return cp(sorted(P), c)

print("=== Q5 Closest pair: brute force vs divide and conquer ===")
for t in range(200):
    n = random.randint(2, 60); P = list({(random.randint(0, 50), random.randint(0, 50)) for _ in range(n)})
    if len(P) < 2: continue
    assert closest(P, [0, 0]) == brute(P, [0])
print("correctness: 200 random small datasets (with many ties) agree with brute force")
print("n | brute dist calcs n(n-1)/2 | D&C dist calcs | strip points examined | ratio | brute ms | D&C ms | result equal")
for n in [8, 16, 32, 64, 100, 128, 200, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536]:
    P = [(random.random() * 1e6, random.random() * 1e6) for _ in range(n)]
    c = [0, 0]; r = closest(P, c)
    td = timeit(lambda: closest(P, [0, 0]), 5 if n <= 2048 else 3, max(1, 2000 // n)) * 1000
    if n <= 4096:
        cb = [0]; rb = brute(P, cb)
        tb = timeit(lambda: brute(P, [0]), 5 if n <= 512 else 1, max(1, 2000 // n)) * 1000
        eq = (rb == r); bc = cb[0]
    else:
        tb = float("nan"); eq = "n/a"; bc = n * (n - 1) // 2
    print(n, "|", bc, "|", c[0], "|", c[1], "|", round(bc / c[0], 1), "|", round(tb, 3), "|", round(td, 3), "|", eq)
print("\nfine crossover scan (time in microseconds, median):")
for n in [8, 12, 16, 20, 24, 28, 32, 40, 48, 64, 96]:
    P = [(random.random() * 1e6, random.random() * 1e6) for _ in range(n)]
    tb = timeit(lambda: brute(P, [0]), 9, max(10, 5000 // n)) * 1e6
    td = timeit(lambda: closest(P, [0, 0]), 9, max(10, 5000 // n)) * 1e6
    cb = [0]; brute(P, cb); cd = [0, 0]; closest(P, cd)
    print(f"n={n:3d} brute {tb:9.1f} us ({cb[0]} calcs) | D&C {td:9.1f} us ({cd[0]} calcs)")
print("\nstructured datasets n=2048 (same points given to both):")
n = 2048
sets = {"uniform": [(random.random() * 1e6, random.random() * 1e6) for _ in range(n)],
        "clustered": [(random.gauss(5e5, 50), random.gauss(5e5, 50)) for _ in range(n)],
        "same x (vertical line)": [(1000.0, random.random() * 1e6) for _ in range(n)],
        "grid 46x45": [(float(i % 46), float(i // 46)) for i in range(n)]}
for name, P in sets.items():
    cd = [0, 0]; r = closest(P, cd); cb = [0]; rb = brute(P, cb)
    print(f"{name:24s} brute calcs {cb[0]} | D&C calcs {cd[0]} | strip pts {cd[1]} | equal {r == rb}")

# ================= Q6A Selection =================
def isort(a, c):
    a = a[:]
    for i in range(1, len(a)):
        k = a[i]; j = i - 1
        while j >= 0:
            c[0] += 1
            if a[j] > k: a[j + 1] = a[j]; j -= 1
            else: break
        a[j + 1] = k
    return a
def mom(a, k, c, rec=None):
    """k-th smallest (1-based) with median of medians (groups of 5); c[0] counts comparisons"""
    first = True
    while True:
        n = len(a)
        if n <= 5: return isort(a, c)[k - 1]
        meds = [isort(a[i:i + 5], c)[len(a[i:i + 5]) // 2 if len(a[i:i + 5]) % 2 else len(a[i:i + 5]) // 2 - 1] for i in range(0, n, 5)]
        p = mom(meds, (len(meds) + 1) // 2, c)
        lo = [x for x in a if x < p]; hi = [x for x in a if x > p]; c[0] += n
        if first and rec is not None: rec.append(max(len(lo), n - len(lo) - 1 if False else len(hi)) if False else max(len(lo), len(hi)) / n)
        first = False
        if k <= len(lo): a = lo
        elif k > n - len(hi): k -= n - len(hi); a = hi
        else: return p
def qselect(a, k, c, pivot="first"):
    while True:
        n = len(a)
        if n == 1: return a[0]
        p = a[0] if pivot == "first" else random.choice(a)
        lo = [x for x in a if x < p]; hi = [x for x in a if x > p]; c[0] += n
        if k <= len(lo): a = lo
        elif k > n - len(hi): k -= n - len(hi); a = hi
        else: return p

print("\n=== Q6A Selection: QuickSelect vs Median of Medians (distinct keys; count = element comparisons with pivot/sorting) ===")
for t in range(300):
    n = random.randint(1, 300); a = random.sample(range(1000), n); k = random.randint(1, n)
    assert mom(a, k, [0]) == sorted(a)[k - 1] == qselect(a, k, [0], "first") == qselect(a, k, [0], "random")
print("correctness: 300 random (array, k) agree with sorted(a)[k-1]")
print("n | input | k | QS first-pivot cmp | QS random avg/min/max over 300 runs | MoM cmp | MoM cmp/n | largest side fraction at top level")
for n in [1000, 2000, 4000, 8000, 16000]:
    for name in ["sorted", "random"]:
        a = list(range(1, n + 1)) if name == "sorted" else random.sample(range(1, n + 1), n)
        k = n if name == "sorted" else n // 2
        c1 = [0]; qselect(a, k, c1, "first")
        rs = []
        for _ in range(300):
            cr = [0]; qselect(a, k, cr, "random"); rs.append(cr[0])
        c2 = [0]; rec = []; mom(a, k, c2, rec)
        print(n, "|", name, "|", k, "|", c1[0], "|", round(sum(rs) / 300), "/", min(rs), "/", max(rs), "|", c2[0], "|", round(c2[0] / n, 2), "|", round(rec[0], 3))
print("n(n+1)/2 - 1 pattern: QS sorted k=n first pivot =", [n * (n + 1) // 2 - 1 for n in (1000, 2000, 4000, 8000, 16000)])
print("worst fraction of top-level partition for MoM over 2000 random arrays n=1000:", end=" ")
w = 0
for _ in range(2000):
    a = random.sample(range(1000), 1000); rec = []; mom(a, 500, [0], rec); w = max(w, rec[0])
print(round(w, 3), "(bound 7/10 + 6/n =", 0.706, ")")
# random pivot, adversarial-free: probability of a "bad" pivot (outside middle half) over many draws on n=1000
n = 1000; a = list(range(n)); bad = sum(1 for _ in range(100000) if not (n // 4 <= random.choice(a) < 3 * n // 4))
print("random pivot lands outside the middle half in", bad, "of 100000 draws (", bad / 1000, "%)")

# ================= Q6B Meet in the middle =================
def sums(items):
    s = [0]
    for x in items: s = s + [v + x for v in s]
    return s
def brute_subset(items, T):
    n = len(items); s = 0; g = 0; found = (T == 0); cnt = 1
    for i in range(1, 1 << n):
        b = (i & -i).bit_length() - 1; g ^= 1 << b
        s += items[b] if (g >> b) & 1 else -items[b]
        cnt += 1
        if s == T: found = True
    return found, cnt
def mitm(items, T, stats=None):
    n = len(items); L, R = items[:n // 2], items[n // 2:]
    SL = sorted(sums(L)); SR = sorted(sums(R))
    i, j, steps = 0, len(SR) - 1, 0; found = False
    while i < len(SL) and j >= 0:
        steps += 1; v = SL[i] + SR[j]
        if v == T: found = True; break
        if v < T: i += 1
        else: j -= 1
    if stats is not None: stats.update(gen=len(SL) + len(SR), steps=steps)
    return found

print("\n=== Q6B Meet in the middle subset sum (target unreachable = sum+1 -> worst case, full search) ===")
for t in range(300):
    n = random.randint(1, 14); items = [random.randint(1, 30) for _ in range(n)]; T = random.randint(0, sum(items) + 2)
    ref = brute_subset(items, T)[0] if n > 0 else T == 0
    assert mitm(items, T) == ref
print("correctness: 300 random instances agree with exhaustive search")
print("n | brute subsets 2^n | brute ms | MITM sums generated | MITM merge steps | MITM ms | MITM peak MiB (tracemalloc)")
for n in [10, 14, 18, 20, 22, 24, 26, 30, 34, 38, 40]:
    items = [random.randint(1, 10 ** 6) for _ in range(n)]; T = sum(items) + 1
    if n <= 24:
        t0 = time.perf_counter(); f, cnt = brute_subset(items, T); tb = (time.perf_counter() - t0) * 1000
    else: cnt = 2 ** n; tb = float("nan")
    st = {}
    tracemalloc.start(); t0 = time.perf_counter(); mitm(items, T, st); tm = (time.perf_counter() - t0) * 1000
    peak = tracemalloc.get_traced_memory()[1] / 2 ** 20; tracemalloc.stop()
    print(n, "|", cnt, "|", round(tb, 1), "|", st["gen"], "|", st["steps"], "|", round(tm, 1), "|", round(peak, 2))
print("exact: 2^40 =", 2 ** 40, "; 2*2^20 =", 2 * 2 ** 20)

# ================= Q7 Inversion counting =================
def inv_brute(a, c):
    n = len(a); k = 0
    for i in range(n):
        for j in range(i + 1, n):
            c[0] += 1
            if a[i] > a[j]: k += 1
    return k
def inv_dc(a, c):
    """returns (sorted list, inversions); c[0] counts comparisons between elements"""
    n = len(a)
    if n <= 1: return a, 0
    m = n // 2
    L, x = inv_dc(a[:m], c); R, y = inv_dc(a[m:], c)
    out = []; i = j = 0; z = 0
    while i < len(L) and j < len(R):
        c[0] += 1
        if L[i] <= R[j]: out.append(L[i]); i += 1
        else: out.append(R[j]); j += 1; z += len(L) - i
    out += L[i:]; out += R[j:]
    return out, x + y + z

print("\n=== Q7 Counting inversions: brute force vs D&C ===")
tests = {"empty": [], "single": [5], "two sorted": [1, 2], "two reversed": [2, 1], "sorted 10": list(range(10)),
         "reversed 10": list(range(10, 0, -1)), "all equal 8": [3] * 8, "duplicates": [2, 1, 2, 1, 2, 1],
         "textbook [2,4,1,3,5]": [2, 4, 1, 3, 5], "[8,4,2,1]": [8, 4, 2, 1]}
for k, a in tests.items():
    print(f"{k:22s} brute={inv_brute(a, [0]):3d}  D&C={inv_dc(a, [0])[1]:3d}")
for _ in range(1000):
    a = [random.randint(0, 20) for _ in range(random.randint(0, 40))]
    assert inv_brute(a, [0]) == inv_dc(a, [0])[1]
print("1000 random arrays (with duplicates, n<=40): D&C == brute force")
print("n | brute cmps n(n-1)/2 | D&C cmps | n log2 n | D&C cmps/(n log2 n) | brute ms | D&C ms | inversions equal")
for n in [10, 100, 500, 1000, 2000, 4000, 8000, 16000, 100000, 1000000]:
    a = random.sample(range(10 * n), n)
    c = [0]; _, inv = inv_dc(a, c)
    tdc = timeit(lambda: inv_dc(a, [0]), 3 if n <= 100000 else 1, 1) * 1000
    if n <= 8000:
        cb = [0]; ib = inv_brute(a, cb); tb = timeit(lambda: inv_brute(a, [0]), 1 if n >= 2000 else 3, 1) * 1000; eq = ib == inv; bc = cb[0]
    else: tb = float("nan"); eq = "n/a"; bc = n * (n - 1) // 2
    print(n, "|", bc, "|", c[0], "|", round(n * math.log2(n)), "|", round(c[0] / (n * math.log2(n)), 3), "|", round(tb, 2), "|", round(tdc, 2), "|", eq)
print("D&C best/worst-case inversions n=4096: sorted ->", inv_dc(list(range(4096)), [0])[1], " reversed ->", inv_dc(list(range(4096, 0, -1)), [0])[1], "(n(n-1)/2 =", 4096 * 4095 // 2, ")")
c1 = [0]; inv_dc(list(range(4096)), c1); c2 = [0]; inv_dc(list(range(4096, 0, -1)), c2)
print("D&C comparisons sorted:", c1[0], "reversed:", c2[0])
print("\nfine crossover n (time in microseconds):")
for n in [4, 8, 12, 16, 24, 32, 48, 64]:
    a = random.sample(range(10 * n), n)
    tb = timeit(lambda: inv_brute(a, [0]), 9, 2000 // n + 20) * 1e6; td = timeit(lambda: inv_dc(a, [0]), 9, 2000 // n + 20) * 1e6
    print(f"n={n:3d} brute {tb:8.1f} us  D&C {td:8.1f} us")
