"""DAA Assignment 3 - Q1 and Q2 experiments (all numbers are measured)."""
import sys, random, math
sys.setrecursionlimit(1000000)
random.seed(42)

# ---------------- Q1 Part A: Max/Min ----------------
def maxmin_dc(a, lo, hi, c):
    """returns (min, max); c[0] counts element comparisons"""
    if lo == hi:
        return a[lo], a[lo]
    if hi == lo + 1:
        c[0] += 1
        return (a[lo], a[hi]) if a[lo] < a[hi] else (a[hi], a[lo])
    mid = (lo + hi) // 2
    mn1, mx1 = maxmin_dc(a, lo, mid, c)
    mn2, mx2 = maxmin_dc(a, mid + 1, hi, c)
    c[0] += 2
    return (mn1 if mn1 < mn2 else mn2), (mx1 if mx1 > mx2 else mx2)

def maxmin_naive(a):
    c = 0
    mn = mx = a[0]
    for x in a[1:]:
        c += 1
        if x > mx: mx = x
        c += 1
        if x < mn: mn = x
    return mn, mx, c

def maxmin_pairs(a):
    """tournament / pairwise scan, for the discrepancy discussion"""
    n = len(a); c = 0
    if n % 2:
        mn = mx = a[0]; i = 1
    else:
        c += 1
        mn, mx = (a[0], a[1]) if a[0] < a[1] else (a[1], a[0]); i = 2
    while i < n:
        c += 1
        s, l = (a[i], a[i+1]) if a[i] < a[i+1] else (a[i+1], a[i])
        c += 2
        if s < mn: mn = s
        if l > mx: mx = l
        i += 2
    return mn, mx, c

print("=== Q1A  Max/Min ===")
print("n | D&C observed | 3n/2-2 | naive 2(n-1) | pairwise observed | ceil(3n/2)-2 | correct")
for n in [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 4096, 65536, 3, 5, 6, 10, 100, 1000, 5000, 12345]:
    ok = True; counts = set()
    for kind in ["random", "sorted", "reverse", "equal"]:
        if kind == "random": a = [random.randint(-10**6, 10**6) for _ in range(n)]
        elif kind == "sorted": a = list(range(n))
        elif kind == "reverse": a = list(range(n, 0, -1))
        else: a = [7] * n
        c = [0]
        mn, mx = maxmin_dc(a, 0, n - 1, c)
        counts.add(c[0])
        ok &= (mn == min(a) and mx == max(a))
    nv = maxmin_naive(a)[2] if n > 1 else 0
    pw = maxmin_pairs(a)[2]
    pred = 3 * n // 2 - 2 if n % 2 == 0 else None
    print(n, "|", sorted(counts), "|", pred, "|", 2 * (n - 1), "|", pw, "|", math.ceil(3 * n / 2) - 2, "|", ok)

# ---------------- Q1 Part B: Binary search ----------------
def bsearch(a, t):
    lo, hi, c = 0, len(a) - 1, 0
    while lo <= hi:
        mid = (lo + hi) // 2
        c += 1
        if a[mid] == t: return mid, c
        elif a[mid] < t: lo = mid + 1
        else: hi = mid - 1
    return -1, c

print("\n=== Q1B Binary search (counts = loop iterations = three-way comparisons) ===")
print("n | floor(log2 n)+1 | best succ | avg succ (all keys) | worst succ | worst unsucc | min unsucc | linear worst")
for n in [7, 15, 100, 1000, 1023, 1024, 10000, 65535, 65536, 100000, 1000000]:
    a = list(range(0, 2 * n, 2))  # even numbers
    cs = [bsearch(a, x)[1] for x in a] if n <= 100000 else [bsearch(a, a[random.randrange(n)])[1] for _ in range(200000)]
    us = [bsearch(a, x)[1] for x in range(-1, 2 * n, 2)] if n <= 100000 else [bsearch(a, 2 * random.randrange(n) + 1)[1] for _ in range(200000)]
    print(n, "|", int(math.log2(n)) + 1, "|", min(cs), "|", round(sum(cs) / len(cs), 3), "|", max(cs), "|", max(us), "|", min(us), "|", n)
    assert all(bsearch(a, x)[0] == i for i, x in enumerate(a)) if n <= 100000 else True
# Q2 ------------------------------------------------------------
def qs(a, st, d=1):
    n = len(a)
    if n <= 1:
        st["maxd"] = max(st["maxd"], d); return a
    p = a[0]
    less = [x for x in a[1:] if x < p]
    gr = [x for x in a[1:] if x >= p]
    st["cmp"] += n - 1
    if d <= 3: st["parts"].append((d, n, len(less), len(gr)))
    st["bal"] += min(len(less), len(gr)) / max(1, n - 1) if n > 2 else 0
    return qs(less, st, d + 1) + [p] + qs(gr, st, d + 1)

def balanced(lo, hi):
    if lo > hi: return []
    mid = (lo + hi) // 2
    return [mid] + balanced(lo, mid - 1) + balanced(mid + 1, hi)

def msort(a, st, d=1):
    n = len(a)
    if n <= 1:
        st["maxd"] = max(st["maxd"], d); return a
    m = n // 2
    L = msort(a[:m], st, d + 1); R = msort(a[m:], st, d + 1)
    out = []; i = j = 0
    while i < len(L) and j < len(R):
        st["cmp"] += 1
        if L[i] <= R[j]: out.append(L[i]); i += 1
        else: out.append(R[j]); j += 1
    return out + L[i:] + R[j:]

print("\n=== Q2 Quick Sort (pivot = first element) vs Merge Sort ===")
for n in [1023, 2047, 4095]:
    for kind in ["balanced-constructed", "random", "sorted", "reverse"]:
        if kind.startswith("bal"): a = balanced(1, n)
        elif kind == "random": a = random.sample(range(1, n + 1), n)
        elif kind == "sorted": a = list(range(1, n + 1))
        else: a = list(range(n, 0, -1))
        st = {"cmp": 0, "maxd": 0, "parts": [], "bal": 0}
        r = qs(a, st)
        assert r == sorted(a)
        ms = {"cmp": 0, "maxd": 0}
        assert msort(a, ms) == sorted(a)
        print(f"n={n} {kind:21s} QS cmp={st['cmp']:>9} depth={st['maxd']:>5} first splits={[(p[1],p[2],p[3]) for p in st['parts'][:3]]} | MS cmp={ms['cmp']:>6} depth={ms['maxd']}")
print("n(n-1)/2 for 1023,2047,4095:", [n * (n - 1) // 2 for n in (1023, 2047, 4095)])
print("n log2 n  for 1023,2047,4095:", [round(n * math.log2(n)) for n in (1023, 2047, 4095)])
# depth statistics over 200 random inputs, n=4095
ds = []; cs = []
for _ in range(200):
    a = random.sample(range(4095), 4095); st = {"cmp": 0, "maxd": 0, "parts": [], "bal": 0}; qs(a, st); ds.append(st["maxd"]); cs.append(st["cmp"])
print("random n=4095 x200: depth min/avg/max =", min(ds), round(sum(ds) / 200, 1), max(ds), " cmp min/avg/max =", min(cs), round(sum(cs) / 200), max(cs))
