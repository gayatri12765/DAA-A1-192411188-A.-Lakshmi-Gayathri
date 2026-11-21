from daa_algorithms import max_min_pairwise, binary_search
if __name__=='__main__':
    data=[12,4,19,7,7,2,15,10]
    print('Q1 max/min:',max_min_pairwise(data))
    ordered=sorted(data)
    print('Q1 binary search (target 10):',binary_search(ordered,10))
