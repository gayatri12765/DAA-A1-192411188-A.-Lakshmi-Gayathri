from daa_algorithms import conventional_matmul, strassen_matmul
if __name__=='__main__':
    A=[[1,2,3],[4,5,6]]
    B=[[7,8],[9,10],[11,12]]
    standard=conventional_matmul(A,B)
    fast=strassen_matmul(A,B,cutoff=1)
    print('Conventional:',standard)
    print('Strassen:',fast)
    print('Results match:',standard==fast)
