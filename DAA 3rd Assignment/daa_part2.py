"""DAA Assignment 3 - Q3 (Karatsuba) and Q4 (Strassen) experiments. All numbers measured."""
import sys, random, time, statistics, tracemalloc, math
sys.setrecursionlimit(100000)
random.seed(7)

def timeit(f, reps=5, loops=1):
    ts = []
    for _ in range(reps):
        t = time.perf_counter()
        for _ in range(loops): f()
        ts.append((time.perf_counter() - t) / loops)
    return statistics.median(ts)

# ================= Q3 =================
def trim(a):
    while len(a) > 1 and a[-1] == 0: a.pop()
    return a
def add(a, b):
    n = max(len(a), len(b)); r = []; c = 0
    for i in range(n):
        s = c + (a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)
        r.append(s % 10); c = s // 10
    if c: r.append(c)
    return r
def sub(a, b):  # a >= b
    r = []; br = 0
    for i in range(len(a)):
        d = a[i] - br - (b[i] if i < len(b) else 0)
        if d < 0: d += 10; br = 1
        else: br = 0
        r.append(d)
    return trim(r)
def shift(a, k): return a if a == [0] else [0] * k + a
def school(a, b, cnt):
    r = [0] * (len(a) + len(b))
    for i, x in enumerate(a):
        c = 0
        for j, y in enumerate(b):
            cnt[0] += 1
            t = r[i + j] + x * y + c
            r[i + j] = t % 10; c = t // 10
        r[i + len(b)] += c
    return trim(r)
def kara(a, b, cnt, T=1):
    n = max(len(a), len(b))
    if n <= T:
        return school(a, b, cnt) if T > 1 else (cnt.__setitem__(0, cnt[0] + 1) or trim([a[0] * b[0] % 10, a[0] * b[0] // 10]))
    a = a + [0] * (n - len(a)); b = b + [0] * (n - len(b))
    m = n // 2
    a0, a1, b0, b1 = trim(a[:m]), trim(a[m:]), trim(b[:m]), trim(b[m:])
    z0 = kara(a0, b0, cnt, T); z2 = kara(a1, b1, cnt, T)
    z1 = sub(sub(kara(add(a0, a1), add(b0, b1), cnt, T), z2), z0)
    return trim(add(add(z0, shift(z1, m)), shift(z2, 2 * m)))
def rnd(n):
    return [random.randint(0, 9) for _ in range(n - 1)] + [random.randint(1, 9)]
def toint(a): return int("".join(map(str, reversed(a))))

print("=== Q3 Karatsuba vs schoolbook (base 10 digit lists) ===")
for _ in range(300):
    n = random.randint(1, 60); a, b = rnd(n), rnd(random.randint(1, 60))
    c = [0]; assert toint(kara(a, b, c)) == toint(a) * toint(b)
    c = [0]; assert toint(school(a, b, c)) == toint(a) * toint(b)
print("correctness: 300 random pairs OK (both algorithms equal Python int product)")
print("n | school mults | kara mults | 3^log2(n) | school ms | kara ms | ratio kara/school")
rows = {}
for n in [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]:
    a, b = rnd(n), rnd(n)
    c1 = [0]; school(a, b, c1); c2 = [0]; kara(a, b, c2)
    loops = max(1, 2000 // n); reps = 5 if n <= 256 else 3
    ts = timeit(lambda: school(a, b, [0]), reps, loops) * 1000
    tk = timeit(lambda: kara(a, b, [0]), reps, loops) * 1000
    rows[n] = (ts, tk)
    print(n, "|", c1[0], "|", c2[0], "|", round(3 ** math.log2(n)), "|", round(ts, 4), "|", round(tk, 4), "|", round(tk / ts, 2))
print("\nfine crossover scan (pure Karatsuba, base case 1 digit):")
for n in [256, 384, 512, 640, 768, 1024, 1536, 2048]:
    a, b = rnd(n), rnd(n)
    ts = timeit(lambda: school(a, b, [0]), 3, 1) * 1000
    tk = timeit(lambda: kara(a, b, [0]), 3, 1) * 1000
    c1 = [0]; c2 = [0]; school(a, b, c1); kara(a, b, c2)
    print(n, "| school ms", round(ts, 2), "| kara ms", round(tk, 2), "| school mults", c1[0], "| kara mults", c2[0])
print("\nhybrid Karatsuba (switch to schoolbook when n <= T), n=512 and 1024:")
for n in [512, 1024]:
    a, b = rnd(n), rnd(n)
    for T in [1, 8, 16, 32, 64, 128]:
        tk = timeit(lambda: kara(a, b, [0], T), 3, 1) * 1000
        c = [0]; kara(a, b, c, T)
        print(f"n={n} T={T:3d} time {tk:8.2f} ms  digit mults {c[0]}")
print("timing at small sizes (many loops) n=4..64:")
for n in [4, 8, 12, 16, 20, 24, 28, 32, 40, 48, 64, 96, 128, 192]:
    a, b = rnd(n), rnd(n)
    loops = max(5, 4000 // n)
    ts = timeit(lambda: school(a, b, [0]), 7, loops) * 1e6
    tk = timeit(lambda: kara(a, b, [0]), 7, loops) * 1e6
    print(f"n={n:4d} school {ts:10.1f} us  kara {tk:10.1f} us  kara/school {tk/ts:5.2f}")

# ================= Q4 =================
def madd(A, B, c): c["add"] += len(A) * len(A); return [[x + y for x, y in zip(r, s)] for r, s in zip(A, B)]
def msub(A, B, c): c["add"] += len(A) * len(A); return [[x - y for x, y in zip(r, s)] for r, s in zip(A, B)]
def conv(A, B, c):
    n = len(A); Bt = list(zip(*B)); c["mul"] += n ** 3; c["add"] += n * n * (n - 1)
    return [[sum(a * b for a, b in zip(r, col)) for col in Bt] for r in A]
def quad(A):
    h = len(A) // 2
    return ([r[:h] for r in A[:h]], [r[h:] for r in A[:h]], [r[:h] for r in A[h:]], [r[h:] for r in A[h:]])
def join(C11, C12, C21, C22):
    return [a + b for a, b in zip(C11, C12)] + [a + b for a, b in zip(C21, C22)]
def blockconv(A, B, c, cut=1):  # recursive 8-multiplication version
    n = len(A)
    if n <= cut: return conv(A, B, c)
    A11, A12, A21, A22 = quad(A); B11, B12, B21, B22 = quad(B)
    f = lambda X, Y: blockconv(X, Y, c, cut)
    return join(madd(f(A11, B11), f(A12, B21), c), madd(f(A11, B12), f(A12, B22), c),
                madd(f(A21, B11), f(A22, B21), c), madd(f(A21, B12), f(A22, B22), c))
def strassen(A, B, c, cut=1):
    n = len(A)
    if n <= cut: return conv(A, B, c)
    A11, A12, A21, A22 = quad(A); B11, B12, B21, B22 = quad(B)
    f = lambda X, Y: strassen(X, Y, c, cut)
    M1 = f(madd(A11, A22, c), madd(B11, B22, c)); M2 = f(madd(A21, A22, c), B11)
    M3 = f(A11, msub(B12, B22, c)); M4 = f(A22, msub(B21, B11, c))
    M5 = f(madd(A11, A12, c), B22); M6 = f(msub(A21, A11, c), madd(B11, B12, c))
    M7 = f(msub(A12, A22, c), madd(B21, B22, c))
    C11 = madd(msub(madd(M1, M4, c), M5, c), M7, c); C12 = madd(M3, M5, c)
    C21 = madd(M2, M4, c); C22 = madd(msub(madd(M1, M3, c), M2, c), M6, c)
    return join(C11, C12, C21, C22)
def pad(A, m): return [r + [0] * (m - len(r)) for r in A] + [[0] * m for _ in range(m - len(A))]
def strassen_any(A, B, c, cut=1):
    n = len(A); m = 1
    while m < n: m *= 2
    if m == n: return strassen(A, B, c, cut)
    C = strassen(pad(A, m), pad(B, m), c, cut)
    return [r[:n] for r in C[:n]]
def rmat(n): return [[random.randint(-9, 9) for _ in range(n)] for _ in range(n)]

print("\n=== Q4 Strassen (pure Python lists; all scalar ops counted) ===")
for _ in range(20):
    n = random.randint(1, 20); A, B = rmat(n), rmat(n); c = {"mul": 0, "add": 0}
    ref = conv(A, B, {"mul": 0, "add": 0})
    assert strassen_any(A, B, c, 1) == ref and blockconv(pad(A, 1 << (n - 1).bit_length()) if False else A, B, {"mul": 0, "add": 0}, 1) == ref if (n & (n - 1)) == 0 else strassen_any(A, B, c, 1) == ref
print("correctness: 20 random sizes 1..20 (including non powers of 2) match conventional product")
print("n | conv mul | strassen mul(cut=1) | 7^k | conv add | strassen add | conv ms | block8 ms | strassen(cut1) ms | strassen(cut16) ms | strassen(cut32) ms")
for n in [2, 4, 8, 16, 32, 64, 128]:
    A, B = rmat(n), rmat(n)
    c1 = {"mul": 0, "add": 0}; conv(A, B, c1)
    c2 = {"mul": 0, "add": 0}; strassen(A, B, c2, 1)
    reps = 5 if n <= 32 else 3
    loops = max(1, 600 // (n * n // 4 + 1))
    t0 = timeit(lambda: conv(A, B, {"mul": 0, "add": 0}), reps, loops) * 1000
    tb = timeit(lambda: blockconv(A, B, {"mul": 0, "add": 0}, 1), reps, loops) * 1000 if n <= 64 else float("nan")
    t1 = timeit(lambda: strassen(A, B, {"mul": 0, "add": 0}, 1), reps, loops) * 1000
    t16 = timeit(lambda: strassen(A, B, {"mul": 0, "add": 0}, 16), reps, loops) * 1000 if n > 16 else float("nan")
    t32 = timeit(lambda: strassen(A, B, {"mul": 0, "add": 0}, 32), reps, loops) * 1000 if n > 32 else float("nan")
    print(n, "|", c1["mul"], "|", c2["mul"], "|", 7 ** int(math.log2(n)), "|", c1["add"], "|", c2["add"], "|", round(t0, 3), "|", round(tb, 3), "|", round(t1, 3), "|", round(t16, 3), "|", round(t32, 3))
print("\nPadding cost (cut=1): n -> padded m")
for n in [100, 65, 33, 17, 5]:
    A, B = rmat(n), rmat(n); m = 1 << (n - 1).bit_length()
    c = {"mul": 0, "add": 0}; strassen_any(A, B, c, 1)
    t = timeit(lambda: strassen_any(A, B, {"mul": 0, "add": 0}, 1), 3, 1) * 1000
    tc = timeit(lambda: conv(A, B, {"mul": 0, "add": 0}), 3, 1) * 1000
    print(f"n={n} pad to {m}: strassen mul={c['mul']} (conventional n^3={n**3}, padded 7^k={7**int(math.log2(m))}) strassen {t:.1f} ms vs conv {tc:.1f} ms")

import numpy as np
def strassen_np(A, B, cut, c):
    n = A.shape[0]
    if n <= cut:
        c[0] += 1; return A @ B
    h = n // 2
    A11, A12, A21, A22 = A[:h, :h], A[:h, h:], A[h:, :h], A[h:, h:]
    B11, B12, B21, B22 = B[:h, :h], B[:h, h:], B[h:, :h], B[h:, h:]
    M1 = strassen_np(A11 + A22, B11 + B22, cut, c); M2 = strassen_np(A21 + A22, B11, cut, c)
    M3 = strassen_np(A11, B12 - B22, cut, c); M4 = strassen_np(A22, B21 - B11, cut, c)
    M5 = strassen_np(A11 + A12, B22, cut, c); M6 = strassen_np(A21 - A11, B11 + B12, cut, c)
    M7 = strassen_np(A12 - A22, B21 + B22, cut, c)
    C = np.empty_like(A)
    C[:h, :h] = M1 + M4 - M5 + M7; C[:h, h:] = M3 + M5; C[h:, :h] = M2 + M4; C[h:, h:] = M1 - M2 + M3 + M6
    return C
print("\nNumPy: BLAS A@B vs Strassen (leaf = BLAS, float64). time in ms; leaves = BLAS calls")
for n in [128, 256, 512, 1024, 2048]:
    A = np.random.rand(n, n); B = np.random.rand(n, n)
    tb = timeit(lambda: A @ B, 3, 1) * 1000
    out = []
    for cut in [64, 128, 256]:
        if cut >= n: continue
        c = [0]; C = strassen_np(A, B, cut, c)
        err = float(np.max(np.abs(C - A @ B)))
        t = timeit(lambda: strassen_np(A, B, cut, [0]), 3, 1) * 1000
        out.append(f"cut={cut}: {t:.1f} ms (leaves {c[0]}, max abs err {err:.1e})")
    print(f"n={n}: BLAS {tb:.1f} ms | " + " | ".join(out))
n = 1024; A = np.random.rand(n, n); B = np.random.rand(n, n)
tracemalloc.start(); _ = A @ B; p1 = tracemalloc.get_traced_memory()[1]; tracemalloc.stop()
tracemalloc.start(); _ = strassen_np(A, B, 128, [0]); p2 = tracemalloc.get_traced_memory()[1]; tracemalloc.stop()
print(f"peak extra memory n=1024: A@B {p1/2**20:.1f} MiB, Strassen(cut=128) {p2/2**20:.1f} MiB; one matrix = {n*n*8/2**20:.1f} MiB")
