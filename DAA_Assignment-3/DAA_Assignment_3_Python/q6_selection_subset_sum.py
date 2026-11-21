from daa_algorithms import quickselect, median_of_medians, subset_sum_mitm
if __name__=='__main__':
    values=[9,1,7,3,8,2,6,4,5]
    k=5
    print('QuickSelect:',quickselect(values,k,pivot='random'))
    print('Median of Medians:',median_of_medians(values,k))
    weights=[3,34,4,12,5,2]
    target=9
    indices=subset_sum_mitm(weights,target)
    print('Subset Sum witness indices:',indices)
    print('Witness values:',[weights[i] for i in indices] if indices is not None else None)
