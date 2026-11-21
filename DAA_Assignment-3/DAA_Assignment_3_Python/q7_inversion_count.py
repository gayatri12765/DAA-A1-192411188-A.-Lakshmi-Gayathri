from daa_algorithms import count_inversions
if __name__=='__main__':
    data=[2,4,1,3,5]
    ordered,count=count_inversions(data)
    print('Sorted array:',ordered)
    print('Strict inversion count:',count)
