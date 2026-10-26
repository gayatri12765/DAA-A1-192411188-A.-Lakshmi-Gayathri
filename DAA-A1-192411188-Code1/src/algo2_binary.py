# RegNo: 192411188 | Name: Lakshmi Gayathri
def preprocess_sort(a):
    return sorted(a)

def binary_search_rec(a, key, lo=0, hi=None, c=0):
    if hi is None:
        hi = len(a) - 1
    if lo > hi:
        return -1, c
    mid = (lo + hi) // 2
    c += 1
    if a[mid] == key:
        return mid, c
    if key < a[mid]:
        return binary_search_rec(a, key, lo, mid - 1, c)
    return binary_search_rec(a, key, mid + 1, hi, c)
