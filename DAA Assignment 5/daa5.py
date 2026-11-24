import itertools, random, time, math, sys
sys.setrecursionlimit(10000)

# ================= B1: Graph colouring (instrumented backtracking) =================
def colour(n, edges, m, order="input"):
    adj = [set() for _ in range(n)]
    for u, v in edges:
        adj[u].add(v); adj[v].add(u)
    deg = [len(a) for a in adj]
    col = [-1] * n
    st = dict(nodes=0, attempts=0, rejected=0, backtracks=0, maxdepth=0)

    def pick():
        un = [v for v in range(n) if col[v] < 0]
        if order == "input":
            return un[0]
        legal = lambda v: m - len({col[u] for u in adj[v] if col[u] >= 0})
        return min(un, key=lambda v: (legal(v), -deg[v], v))   # fewest legal colours, then max degree

    def solve(d):
        st["nodes"] += 1
        st["maxdepth"] = max(st["maxdepth"], d)
        if d == n:
            return True
        v = pick()
        for c in range(m):
            st["attempts"] += 1
            if any(col[u] == c for u in adj[v]):      # feasibility test
                st["rejected"] += 1
                continue
            col[v] = c                                 # assign
            if solve(d + 1):
                return True
            col[v] = -1                                # undo
            st["backtracks"] += 1
        return False

    ok = solve(0)
    return ok, (col[:] if ok else None), st

def valid(n, edges, col, m):
    return all(0 <= c < m for c in col) and all(col[u] != col[v] for u, v in edges)

def cycle(n): return [(i, (i + 1) % n) for i in range(n)]
def complete(vs): return [(a, b) for a, b in itertools.combinations(vs, 2)]
def rnd(n, p, seed):
    r = random.Random(seed)
    return [(a, b) for a, b in itertools.combinations(range(n), 2) if r.random() < p]
PETERSEN = [(i, (i+1) % 5) for i in range(5)] + [(i, i+5) for i in range(5)] + [(5+i, 5+(i+2) % 5) for i in range(5)]

print("=== B1.1 TESTS (version 1) ===")
tests = [("C5, m=3 (colourable)", 5, cycle(5), 3),
         ("K4, m=3 (not colourable)", 4, complete(range(4)), 3),
         ("K3, m=2 (odd cycle, not 2-colourable)", 3, complete(range(3)), 2),
         ("boundary: 1 vertex, m=1", 1, [], 1),
         ("boundary: 0 vertices, m=1", 0, [], 1),
         ("boundary: 1 vertex, m=0", 1, [], 0),
         ("boundary: 4 isolated vertices, m=1", 4, [], 1)]
for name, n, e, m in tests:
    ok, c, st = colour(n, e, m)
    print(f"{name:42s} -> {ok!s:5s} colouring={c} valid={valid(n,e,c,m) if ok else '-'} {st}")

print("\n=== B1.4 VERSION 1 (input order) vs VERSION 2 (fewest-legal-colours, then max degree) ===")
tail = [(i, i+1) for i in range(11)] + complete([12, 13, 14, 15])
graphs = [("Petersen, m=3", 10, PETERSEN, 3),
          ("Random n=20 p=.30 s=1, m=3", 20, rnd(20, .30, 1), 3),
          ("Random n=22 p=.25 s=2, m=3", 22, rnd(22, .25, 2), 3),
          ("Random n=25 p=.20 s=3, m=3", 25, rnd(25, .20, 3), 3),
          ("Path12 + K4 at end, m=3", 16, tail, 3)]
for name, n, e, m in graphs:
    print(name)
    for v in ("input", "dsatur"):
        ok, c, st = colour(n, e, m, v)
        print(f"   {v:7s} colourable={ok!s:5s} nodes={st['nodes']:6d} attempts={st['attempts']:6d} rejected={st['rejected']:6d} backtracks={st['backtracks']:6d} maxdepth={st['maxdepth']}")

print("\n=== B2 ADVERSARIAL (n=16, m=3, version 1) ===")
A = cycle(16)                       # bipartite: easy
B = tail                            # sparse prefix path + K4 hidden at end
for nm, g in (("Graph A  C16", A), ("Graph B  Path12+K4(last)", B)):
    ok, c, st = colour(16, g, 3)
    print(f"{nm:26s} colourable={ok!s:5s} nodes={st['nodes']:7d} backtracks={st['backtracks']:7d} rejected={st['rejected']:7d} attempts={st['attempts']:7d}")
ok, c, st = colour(16, B, 3, "dsatur")
print(f"Graph B with version 2     colourable={ok!s:5s} nodes={st['nodes']:7d} backtracks={st['backtracks']:7d} rejected={st['rejected']:7d} attempts={st['attempts']:7d}")

# ================= B3: Set cover =================
def exact_cover(U, sets):
    full = (1 << U) - 1
    masks = [sum(1 << z for z in s) for s in sets]
    combos = 0
    for k in range(1, len(sets) + 1):
        for comb in itertools.combinations(range(len(sets)), k):
            combos += 1
            cov = 0
            for i in comb: cov |= masks[i]
            if cov == full: return k, comb, combos
    return None, None, combos

def greedy_cover(U, sets):
    unc, chosen, evals = set(range(U)), [], 0
    while unc:
        best, bg = None, 0
        for i, s in enumerate(sets):
            evals += 1
            g = len(unc & set(s))
            if g > bg: bg, best = g, i
        if best is None: return None, chosen, evals
        chosen.append(best); unc -= set(sets[best])
    return len(chosen), chosen, evals

def rand_inst(U, S, p, seed):
    r = random.Random(seed)
    sets = [{z for z in range(U) if r.random() < p} for _ in range(S)]
    for z in range(U):
        if not any(z in s for s in sets): r.choice(sets).add(z)
    return [sorted(s) for s in sets]

print("\n=== B3.1 SMALL INSTANCES ===")
for i, (U, S, p, sd) in enumerate([(10, 8, .3, 11), (12, 9, .25, 5), (14, 10, .2, 9), (12, 10, .25, 21)], 1):
    sets = rand_inst(U, S, p, sd)
    ke, ce, cb = exact_cover(U, sets); kg, cg, ev = greedy_cover(U, sets)
    print(f"Instance {i}: U={U} sets={S} exact={ke} {ce} greedy={kg} {cg} same={ke==kg}")

print("\n=== B3.2 COUNTEREXAMPLE ===")
U = 6
sets = [[0, 2, 4], [1, 3, 5], [0, 1, 2, 3]]   # S0={Z1,Z3,Z5}, S1={Z2,Z4,Z6}, S2={Z1..Z4}
ke, ce, cb = exact_cover(U, sets); kg, cg, ev = greedy_cover(U, sets)
print("exact", ke, ce, "combos", cb, "| greedy", kg, cg, "evals", ev)

print("\n=== B3.3 SCALABILITY ===")
print("zones centres | exact combos checked | greedy evals | exact | greedy | exact_time(s) greedy_time(s)")
for U, S, sd in [(10, 8, 1), (14, 12, 2), (18, 16, 3), (22, 20, 4), (26, 24, 5), (30, 28, 6), (34, 32, 7)]:
    sets = rand_inst(U, S, .18, sd)
    t = time.time(); ke, ce, cb = exact_cover(U, sets); te = time.time() - t
    t = time.time(); kg, cg, ev = greedy_cover(U, sets); tg = time.time() - t
    print(f"{U:5d} {S:7d} | {cb:20d} | {ev:12d} | {ke:5d} | {kg:6d} | {te:9.3f} {tg:9.5f}")
    if te > 40: break

# ================= B4: Bin packing (First-Fit Decreasing) =================
def ffd(items, C):
    bins, cmp_ = [], 0
    for w in sorted(items, reverse=True):
        for b in bins:
            cmp_ += 1
            if b[0] >= w:
                b[0] -= w; b[1].append(w); break
        else:
            bins.append([C - w, [w]])
    return bins, cmp_

def opt_bins(items, C):
    items = sorted(items, reverse=True); best = [len(items)]
    def dfs(i, bins):
        if len(bins) >= best[0]: return
        if i == len(items): best[0] = len(bins); return
        w, seen = items[i], set()
        for j in range(len(bins)):
            if bins[j] + w <= C and bins[j] not in seen:
                seen.add(bins[j]); bins[j] += w; dfs(i + 1, bins); bins[j] -= w
        bins.append(w); dfs(i + 1, bins); bins.pop()
    dfs(0, []); return best[0]

print("\n=== B4.1 ALLOCATION (C=100) ===")
items = [70, 60, 50, 40, 30, 30, 20, 10]
bins, c = ffd(items, 100)
print("servers used:", len(bins))
for i, (rem, ws) in enumerate(bins, 1): print(f"  Server {i}: workloads={ws} load={100-rem} remaining={rem}")

print("\n=== B4.2 CHALLENGE ===")
r = random.Random(0); found = None
for _ in range(60000):
    n = r.randint(8, 11); its = [r.randint(20, 60) for _ in range(n)]
    b, _ = ffd(its, 100)
    if len(b) > math.ceil(sum(its) / 100):
        o = opt_bins(its, 100)
        if o < len(b): found = (its, len(b), o); break
print("counterexample (C=100):", found)
if found:
    for i, (rem, ws) in enumerate(ffd(found[0], 100)[0], 1): print(f"  FFD server {i}: {ws} remaining={rem}")

print("\n=== B4.3 EVIDENCE: FFD on large inputs (C=100, sizes uniform 1..60) ===")
print("workloads | FFD bins | lower bound ceil(sum/C) | gap | comparisons | time(s)")
for n in (1000, 5000, 20000):
    its = [random.Random(n).randint(1, 60) for _ in range(n)]
    its = [random.Random(n + i).randint(1, 60) for i in range(n)]
    t = time.time(); b, cm = ffd(its, 100); tt = time.time() - t
    lb = math.ceil(sum(its) / 100)
    print(f"{n:9d} | {len(b):8d} | {lb:23d} | {len(b)-lb:3d} | {cm:11d} | {tt:.3f}")
