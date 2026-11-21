from daa_algorithms import karatsuba
if __name__=='__main__':
    x=12345678901234567890; y=98765432109876543210
    product,leaves=karatsuba(x,y,cutoff_digits=2)
    print('Karatsuba product:',product)
    print('Recursive leaf multiplications:',leaves)
    print('Matches Python integer multiplication:',product==x*y)
