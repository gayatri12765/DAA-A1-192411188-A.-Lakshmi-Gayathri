"""Reference implementations for DAA Assignment 3 (CO3)."""
from __future__ import annotations
import random
from typing import Sequence, Optional

# Q1: pairwise extrema and binary search

def max_min_pairwise(values: Sequence[int]):
    """Return (minimum, maximum, comparisons) using pairwise tournaments."""
    n=len(values)
    if n==0: raise ValueError('values must not be empty')
    if n==1: return values[0],values[0],0
    comparisons=0
    if n%2:
        lo=hi=values[0]; start=1
    else:
        comparisons=1
        if values[0] < values[1]: lo,hi=values[0],values[1]
        else: lo,hi=values[1],values[0]
        start=2
    for i in range(start,n,2):
        a,b=values[i],values[i+1]; comparisons+=1
        if a<b: small,large=a,b
        else: small,large=b,a
        comparisons+=2
        if small<lo: lo=small
        if large>hi: hi=large
    return lo,hi,comparisons

def binary_search(values: Sequence[int], target: int):
    """Return (index or None, midpoint comparisons); values must be sorted."""
    lo,hi=0,len(values)-1; count=0
    while lo<=hi:
        mid=lo+(hi-lo)//2; count+=1
        if values[mid]==target: return mid,count
        if values[mid]<target: lo=mid+1
        else: hi=mid-1
    return None,count

# Q2: Merge Sort and Quick Sort with instrumentation

def merge_sort(values: Sequence[int]):
    a=list(values); aux=[0]*len(a)
    def sort(lo,hi):
        if hi-lo<=1:return
        mid=(lo+hi)//2; sort(lo,mid); sort(mid,hi)
        i,j,k=lo,mid,lo
        while i<mid and j<hi:
            if a[i]<=a[j]: aux[k]=a[i]; i+=1
            else: aux[k]=a[j]; j+=1
            k+=1
        while i<mid: aux[k]=a[i]; i+=1; k+=1
        while j<hi: aux[k]=a[j]; j+=1; k+=1
        a[lo:hi]=aux[lo:hi]
    sort(0,len(a)); return a

def quick_sort(values: Sequence[int], pivot: str='last', seed: int=0):
    """Return (sorted list, comparison count, max recursion depth, partition sizes).
    Pivot choices: 'last', 'middle', or 'random'. Lomuto partition; duplicates supported.
    """
    a=list(values); rng=random.Random(seed); comparisons=0; maxdepth=0; trace=[]
    def sort(lo,hi,depth):
        nonlocal comparisons,maxdepth
        if lo>=hi:return
        maxdepth=max(maxdepth,depth)
        if pivot=='random': pi=rng.randrange(lo,hi+1)
        elif pivot=='middle': pi=(lo+hi)//2
        elif pivot=='last': pi=hi
        else: raise ValueError("pivot must be 'last', 'middle', or 'random'")
        a[pi],a[hi]=a[hi],a[pi]; x=a[hi]; i=lo
        for j in range(lo,hi):
            comparisons+=1
            if a[j]<=x: a[i],a[j]=a[j],a[i]; i+=1
        a[i],a[hi]=a[hi],a[i]
        trace.append((i-lo,hi-i))
        sort(lo,i-1,depth+1); sort(i+1,hi,depth+1)
    sort(0,len(a)-1,1)
    return a,comparisons,maxdepth,trace

# Q3: Karatsuba integer multiplication

def karatsuba(x: int,y: int,cutoff_digits: int=32):
    """Return (product, recursive leaf multiplication count)."""
    if cutoff_digits<1: raise ValueError('cutoff_digits must be positive')
    sign=-1 if (x<0) != (y<0) else 1; x,y=abs(x),abs(y); leaves=0
    cutoff_bits=max(1,int(cutoff_digits*3.32192809489))
    def mul(a,b):
        nonlocal leaves
        if a==0 or b==0: return 0
        if max(a.bit_length(),b.bit_length())<=cutoff_bits:
            leaves+=1; return a*b
        m=max(a.bit_length(),b.bit_length())//2; base=1<<m
        ah,al=divmod(a,base); bh,bl=divmod(b,base)
        z0=mul(al,bl); z2=mul(ah,bh); z1=mul(ah+al,bh+bl)-z2-z0
        return (z2<<(2*m))+(z1<<m)+z0
    return sign*mul(x,y),leaves

# Q4: conventional and Strassen matrix multiplication

def conventional_matmul(A,B):
    if not A or not B or len(A[0])!=len(B): raise ValueError('incompatible matrix dimensions')
    m,k,n=len(A),len(B),len(B[0])
    return [[sum(A[i][t]*B[t][j] for t in range(k)) for j in range(n)] for i in range(m)]

def strassen_matmul(A,B,cutoff: int=32):
    """Multiply rectangular integer matrices; zero-pad to a square, crop result."""
    if not A or not B or len(A[0])!=len(B): raise ValueError('incompatible matrix dimensions')
    if cutoff<1: raise ValueError('cutoff must be positive')
    m,k,n=len(A),len(B),len(B[0]); size=1
    while size<max(m,k,n): size*=2
    def pad(M,rows,cols): return [list(M[i][:cols])+[0]*(size-cols) if i<rows else [0]*size for i in range(size)]
    X,Y=pad(A,m,k),pad(B,k,n)
    def add(U,V): return [[U[i][j]+V[i][j] for j in range(len(U))] for i in range(len(U))]
    def sub(U,V): return [[U[i][j]-V[i][j] for j in range(len(U))] for i in range(len(U))]
    def rec(U,V):
        s=len(U)
        if s<=cutoff: return conventional_matmul(U,V)
        h=s//2
        def block(M,r,c): return [row[c:c+h] for row in M[r:r+h]]
        a11,a12,a21,a22=block(U,0,0),block(U,0,h),block(U,h,0),block(U,h,h)
        b11,b12,b21,b22=block(V,0,0),block(V,0,h),block(V,h,0),block(V,h,h)
        p1=rec(add(a11,a22),add(b11,b22)); p2=rec(add(a21,a22),b11)
        p3=rec(a11,sub(b12,b22)); p4=rec(a22,sub(b21,b11))
        p5=rec(add(a11,a12),b22); p6=rec(sub(a21,a11),add(b11,b12))
        p7=rec(sub(a12,a22),add(b21,b22))
        c11=add(sub(add(p1,p4),p5),p7); c12=add(p3,p5)
        c21=add(p2,p4); c22=add(add(sub(p1,p2),p3),p6)
        out=[[0]*s for _ in range(s)]
        for i in range(h):
            out[i][:h]=c11[i]; out[i][h:]=c12[i]
            out[i+h][:h]=c21[i]; out[i+h][h:]=c22[i]
        return out
    C=rec(X,Y)
    return [row[:n] for row in C[:m]]

# Q5: planar closest pair, O(n log n)

def closest_pair(points):
    """Return ((point_i, point_j), distance, distance_evaluations)."""
    if len(points)<2: return None,float('inf'),0
    px=sorted((float(x),float(y),i) for i,(x,y) in enumerate(points))
    py=sorted(px,key=lambda q:(q[1],q[0],q[2])); checks=0
    def dist2(a,b): return (a[0]-b[0])**2+(a[1]-b[1])**2
    def brute(xs):
        nonlocal checks
        best=float('inf'); pair=None
        for i in range(len(xs)):
            for j in range(i+1,len(xs)):
                checks+=1; d=dist2(xs[i],xs[j])
                if d<best: best,pair=d,(xs[i],xs[j])
        return best,pair
    def solve(xs,ys):
        n=len(xs)
        if n<=3:return brute(xs)
        mid=n//2; left,right=xs[:mid],xs[mid:]; splitx=right[0][0]
        left_ids={q[2] for q in left}
        ly=[q for q in ys if q[2] in left_ids]; ry=[q for q in ys if q[2] not in left_ids]
        dl,pl=solve(left,ly); dr,pr=solve(right,ry)
        best,pair=(dl,pl) if dl<=dr else (dr,pr)
        strip=[q for q in ys if (q[0]-splitx)**2<best]
        for i,a in enumerate(strip):
            for b in strip[i+1:i+8]:
                if (b[1]-a[1])**2>=best: break
                checks+=1; d=dist2(a,b)
                if d<best: best,pair=d,(a,b)
        return best,pair
    d,pair=solve(px,py)
    result=((points[pair[0][2]],points[pair[1][2]]),d**0.5)
    return result[0],result[1],checks

# Q6a: randomized/deterministic QuickSelect and Median of Medians

def quickselect(values: Sequence[int],k: int, pivot: str='random',seed: int=0):
    """Select 1-based k-th smallest; return (value, partition comparisons)."""
    if not 1<=k<=len(values): raise ValueError('k must be in 1..n')
    a=list(values); target=k-1; rng=random.Random(seed); comps=0; lo,hi=0,len(a)-1
    while True:
        if lo==hi:return a[lo],comps
        if pivot=='first': pi=lo
        elif pivot=='random': pi=rng.randrange(lo,hi+1)
        elif pivot=='middle': pi=(lo+hi)//2
        else: raise ValueError("pivot must be 'first', 'random', or 'middle'")
        pv=a[pi]; less=[]; equal=[]; greater=[]
        for v in a[lo:hi+1]:
            comps+=1
            if v<pv: less.append(v)
            else:
                comps+=1
                if v>pv: greater.append(v)
                else: equal.append(v)
        if target<lo+len(less): a[lo:hi+1]=less+equal+greater; hi=lo+len(less)-1
        elif target<lo+len(less)+len(equal): return pv,comps
        else:
            start=lo+len(less)+len(equal); a[lo:hi+1]=less+equal+greater; lo=start

def median_of_medians(values: Sequence[int],k: int):
    """Select 1-based k-th smallest with deterministic worst-case linear time."""
    if not 1<=k<=len(values): raise ValueError('k must be in 1..n')
    a=list(values)
    def select(seq,rank):
        if len(seq)<=5:return sorted(seq)[rank]
        groups=[sorted(seq[i:i+5]) for i in range(0,len(seq),5)]
        medians=[g[len(g)//2] for g in groups]
        pivot=select(medians,len(medians)//2)
        low=[v for v in seq if v<pivot]; eq=[v for v in seq if v==pivot]; high=[v for v in seq if v>pivot]
        if rank<len(low):return select(low,rank)
        if rank<len(low)+len(eq):return pivot
        return select(high,rank-len(low)-len(eq))
    return select(a,k-1)

# Q6b: meet-in-the-middle subset sum

def subset_sum_mitm(values: Sequence[int],target: int):
    """Return a subset index list summing to target, or None."""
    n=len(values); mid=n//2
    def sums(seq,offset):
        out=[(0,0)]
        for i,v in enumerate(seq):
            out += [(s+v,mask | (1<<(offset+i))) for s,mask in out]
        return out
    left=sums(values[:mid],0); right=sums(values[mid:],mid)
    right_by_sum={}
    for s,mask in right: right_by_sum.setdefault(s,mask)
    for s,mask in left:
        other=right_by_sum.get(target-s)
        if other is not None:
            combined=mask|other
            return [i for i in range(n) if combined>>i&1]
    return None

# Q7 model: inversion count using divide and conquer

def count_inversions(values: Sequence[int]):
    """Return (sorted list, strict inversion count)."""
    a=list(values)
    def sort(x):
        if len(x)<=1:return x,0
        mid=len(x)//2; left,lc=sort(x[:mid]); right,rc=sort(x[mid:])
        i=j=0; merged=[]; cross=0
        while i<len(left) and j<len(right):
            if left[i]<=right[j]: merged.append(left[i]); i+=1
            else: merged.append(right[j]); j+=1; cross+=len(left)-i
        merged.extend(left[i:]); merged.extend(right[j:])
        return merged,lc+rc+cross
    return sort(a)
