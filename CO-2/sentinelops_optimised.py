"""Optimised SentinelOps alert-triage algorithms and test harness."""
import math
import random
import time


def sort_alerts(alerts):
    """Return alerts sorted by descending severity; ties keep arrival order."""
    # Python's sort is stable and uses Timsort.
    return sorted(alerts, key=lambda alert: alert[1], reverse=True)


def build_blocklist(blocklist):
    """Build a set once for efficient repeated membership checks."""
    return set(blocklist)


def is_blocked(blocklist_set, ip):
    """Return True exactly when ip is present in the blocklist set."""
    return ip in blocklist_set


def find_signature(log, pattern):
    """Return all starting indices of pattern in log using brute force."""
    n, m = len(log), len(pattern)
    if m == 0:
        # Every boundary is a valid empty-pattern occurrence.
        return list(range(n + 1))
    if m > n:
        return []

    hits = []
    for i in range(n - m + 1):
        j = 0
        while j < m and log[i + j] == pattern[j]:
            j += 1
        if j == m:
            hits.append(i)
    return hits


def closest_logins(events):
    """Return ((i, j), distance) for the closest pair, or (None, inf).

    Points are (x, y) coordinates in kilometres. The x-sorted scan
    checks each unordered pair at most once and prunes when the x-gap
    alone cannot beat the best squared distance.
    """
    if len(events) < 2:
        return None, math.inf

    ordered = sorted(enumerate(events), key=lambda item: item[1][0])
    best_sq = math.inf
    best_pair = None

    for pos in range(len(ordered) - 1):
        original_i, (xi, yi) = ordered[pos]
        for next_pos in range(pos + 1, len(ordered)):
            original_j, (xj, yj) = ordered[next_pos]
            dx = xj - xi
            if dx * dx >= best_sq:
                # Since points are x-sorted, later x-gaps are no smaller.
                break
            dy = yj - yi
            d_sq = dx * dx + dy * dy
            if d_sq < best_sq:
                best_sq = d_sq
                best_pair = (original_i, original_j)

    return best_pair, math.sqrt(best_sq)


def insertion_sort_with_count(alerts):
    """Stable descending insertion sort; return sorted copy and comparisons."""
    result = list(alerts)
    comparisons = 0
    for i in range(1, len(result)):
        key = result[i]
        j = i - 1
        while j >= 0:
            comparisons += 1
            if result[j][1] < key[1]:
                result[j + 1] = result[j]
                j -= 1
            else:
                break
        result[j + 1] = key
    return result, comparisons


def brute_force_distance_count(events):
    """Count pair distance calculations in the unoptimised all-pairs method."""
    count = 0
    best_sq = math.inf
    best_pair = None
    for i in range(len(events)):
        for j in range(len(events)):
            count += 1
            dx = events[i][0] - events[j][0]
            dy = events[i][1] - events[j][1]
            d_sq = dx * dx + dy * dy
            if i != j and d_sq < best_sq:
                best_sq, best_pair = d_sq, (i, j)
    return count, best_pair, math.sqrt(best_sq) if best_pair else math.inf


def pruned_distance_count(events):
    """Return closest pair and count of actual distance evaluations."""
    if len(events) < 2:
        return 0, None, math.inf
    ordered = sorted(enumerate(events), key=lambda item: item[1][0])
    best_sq, best_pair, count = math.inf, None, 0
    for pos in range(len(ordered) - 1):
        i, (xi, yi) = ordered[pos]
        for q in range(pos + 1, len(ordered)):
            j, (xj, yj) = ordered[q]
            dx = xj - xi
            if dx * dx >= best_sq:
                break
            dy = yj - yi
            d_sq = dx * dx + dy * dy
            count += 1
            if d_sq < best_sq:
                best_sq, best_pair = d_sq, (i, j)
    return count, best_pair, math.sqrt(best_sq) if best_pair else math.inf


def run_tests():
    alerts = [("A1", 3), ("A2", 9), ("A3", 5), ("A4", 9), ("A5", 1)]
    expected = [("A2", 9), ("A4", 9), ("A3", 5), ("A1", 3), ("A5", 1)]
    assert sort_alerts(alerts) == expected
    assert insertion_sort_with_count(alerts)[0] == expected

    blocked = build_blocklist(["10.0.0.5", "10.0.0.9", "172.16.4.2"])
    assert is_blocked(blocked, "10.0.0.9") is True
    assert is_blocked(blocked, "10.0.0.5") is True
    assert is_blocked(blocked, "8.8.8.8") is False
    assert is_blocked(build_blocklist([]), "1.2.3.4") is False

    assert find_signature("FAILFAIXFAIL", "FAIL") == [0, 8]
    assert find_signature("XXABC", "ABC") == [2]  # at very end
    assert find_signature("AB", "ABCD") == []
    assert find_signature("AAAA", "AA") == [0, 1, 2]
    assert find_signature("ABC", "") == [0, 1, 2, 3]

    events = [(2, 3), (12, 30), (40, 50), (5, 1), (12, 10), (3, 4)]
    pair, distance = closest_logins(events)
    assert pair == (0, 5)
    assert math.isclose(distance, math.sqrt(2))
    assert closest_logins([]) == (None, math.inf)
    assert closest_logins([(1, 2)]) == (None, math.inf)

    # Duplicate coordinates are a valid zero-distance pair.
    duplicate_pair, duplicate_distance = closest_logins([(0, 0), (5, 5), (0, 0)])
    assert duplicate_pair is not None and duplicate_distance == 0.0
    print("All correctness and boundary tests passed.")


def run_benchmarks():
    rng = random.Random(42)
    print("\\nClosest-pair distance computation counts")
    print("n, brute_force_count, pruned_count")
    for n in (1000, 2000, 4000, 8000):
        points = [(rng.random() * 10000, rng.random() * 10000) for _ in range(n)]
        brute_count, _, _ = brute_force_distance_count(points)
        pruned_count, _, _ = pruned_distance_count(points)
        print(f"{n}, {brute_count}, {pruned_count}")

    print("\\nInsertion-sort comparisons")
    print("n, nearly_sorted_comparisons, random_comparisons")
    for n in (1000, 2000, 4000, 8000):
        base = [(f"A{i}", n - i) for i in range(n)]
        nearly = base.copy()
        if n > 2:
            nearly[n // 2], nearly[n // 2 + 1] = nearly[n // 2 + 1], nearly[n // 2]
        random_data = base.copy()
        rng.shuffle(random_data)
        _, near_count = insertion_sort_with_count(nearly)
        _, random_count = insertion_sort_with_count(random_data)
        print(f"{n}, {near_count}, {random_count}")


if __name__ == "__main__":
    run_tests()
    run_benchmarks()
