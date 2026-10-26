# RegNo: 192411188 | Name: Lakshmi Gayathri
def linear_search(a, key):
    c = 0
    for i, v in enumerate(a):
        c += 1
        if v == key:
            return i, c
    return -1, c
