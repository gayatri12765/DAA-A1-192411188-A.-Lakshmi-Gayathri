import csv, time, math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from config import *
from dataset_generator import generate, make_queries
from algo1_linear import linear_search
from algo2_binary import preprocess_sort, binary_search_rec
from algo3_hash import HashTable

def measure(fn, queries):
    comps, t0 = [], time.perf_counter()
    for k in queries:
        comps.append(fn(k)[1])
    return (time.perf_counter() - t0) / len(queries), comps

header()
rows = []
for n in SIZES:
    data = generate(n)
    q = make_queries(data, 100)
    t = time.perf_counter(); s = preprocess_sort(data); p_sort = time.perf_counter() - t
    t = time.perf_counter(); h = HashTable(n).build(data); p_hash = time.perf_counter() - t
    algos = [
        ("Linear", 0.0, lambda k: linear_search(data, k)),
        ("Binary", p_sort, lambda k: binary_search_rec(s, k)),
        ("Hash", p_hash, lambda k: h.search(k)),
    ]
    for name, prep, fn in algos:
        avg_t, comps = measure(fn, q)
        rows.append(dict(n=n, algorithm=name, preprocess_s=round(prep, 6),
                         avg_search_us=round(avg_t * 1e6, 3),
                         avg_comparisons=round(sum(comps[2:]) / len(comps[2:]), 2),
                         comps_regno_found=comps[0], comps_regno1_notfound=comps[1]))
    print(f"n={n} done")

with open("../results/results.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)

print(f"\n{'n':>9} {'Algorithm':<8} {'Prep(s)':>10} {'Avg us':>12} {'AvgComps':>10} {'Found':>8} {'NotFound':>9}")
for r in rows:
    print(f"{r['n']:>9} {r['algorithm']:<8} {r['preprocess_s']:>10} {r['avg_search_us']:>12} {r['avg_comparisons']:>10} {r['comps_regno_found']:>8} {r['comps_regno1_notfound']:>9}")

def col(a, k):
    return [r[k] for r in rows if r["algorithm"] == a]

algs = ["Linear", "Binary", "Hash"]
for key, title, fname in [("avg_search_us", "Avg search time (microseconds)", "time.png"),
                          ("avg_comparisons", "Avg comparisons (found keys)", "comparisons.png"),
                          ("preprocess_s", "Preprocessing time (s)", "preprocess.png")]:
    plt.figure()
    for a in algs:
        plt.plot(SIZES, col(a, key), marker="o", label=a)
    plt.xscale("log"); plt.yscale("log")
    plt.xlabel("Input size n"); plt.ylabel(title); plt.title(f"{title} vs n | Reg No {REG_NO}")
    plt.grid(True, which="both", alpha=.3); plt.legend()
    plt.savefig(f"../results/graphs/{fname}", dpi=150, bbox_inches="tight"); plt.close()

plt.figure()
theory = {"Linear": [n / 2 for n in SIZES], "Binary": [math.log2(n) - 1 for n in SIZES], "Hash": [1.5 for _ in SIZES]}
for a in algs:
    plt.plot(SIZES, col(a, "avg_comparisons"), marker="o", label=f"{a} (measured)")
    plt.plot(SIZES, theory[a], linestyle="--", label=f"{a} (theory)")
plt.xscale("log"); plt.yscale("log")
plt.xlabel("Input size n"); plt.ylabel("Comparisons"); plt.title(f"Theory vs experiment | Reg No {REG_NO}")
plt.grid(True, which="both", alpha=.3); plt.legend(fontsize=7)
plt.savefig("../results/graphs/theory_vs_experiment.png", dpi=150, bbox_inches="tight"); plt.close()
print("\nSaved results/results.csv and results/graphs/*.png")
