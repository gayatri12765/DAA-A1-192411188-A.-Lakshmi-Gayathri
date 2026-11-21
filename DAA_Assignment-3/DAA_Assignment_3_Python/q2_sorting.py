from daa_algorithms import merge_sort, quick_sort
if __name__=='__main__':
    data=[9,2,7,3,8,1,5,4,6]
    print('Merge Sort:',merge_sort(data))
    print('Quick Sort:',quick_sort(data,pivot='last'))
