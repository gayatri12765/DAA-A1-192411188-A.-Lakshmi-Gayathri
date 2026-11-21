"""Reproducible demonstrations for DAA Assignment 4B (Python 3, standard library)."""
from itertools import permutations
from time import perf_counter
from math import inf


def word_wrap(words, width):
    if width <= 0 or any(len(word) > width for word in words):
        raise ValueError('width must be positive and every word must fit on a line')
    n = len(words); dp = [inf] * (n + 1); nxt = [None] * n; dp[n] = 0
    for i in range(n - 1, -1, -1):
        used = 0
        for j in range(i, n):
            used += len(words[j]) + (j > i)
            if used > width: break
            slack = width - used
            cost = 0 if j == n - 1 else slack ** 2
            if cost + dp[j + 1] < dp[i]: dp[i] = cost + dp[j + 1]; nxt[i] = j + 1
    lines=[]; i=0
    while i<n:
        j=nxt[i]; text=' '.join(words[i:j]); slack=width-len(text)
        lines.append((text,slack,0 if j==n else slack**2)); i=j
    return dp,nxt,lines


def knapsack(capacity, items):
    # item=(id,weight,value)
    ordered=sorted(items,key=lambda x:x[2]/x[1],reverse=True); rem=capacity; frac=[]; val=0
    for item in ordered:
        take=min(1,rem/item[1]); frac.append((item[0],take)); val+=take*item[2]; rem-=take*item[1]
        if rem<=0: break
    n=len(items); dp=[[0]*(capacity+1) for _ in range(n+1)]
    for i,(_,w,v) in enumerate(items,1):
        for c in range(capacity+1): dp[i][c]=max(dp[i-1][c],dp[i-1][c-w]+v if w<=c else 0)
    c=capacity; chosen=[]
    for i in range(n,0,-1):
        if dp[i][c]!=dp[i-1][c]:
            ident,w,v=items[i-1]; chosen.append(ident); c-=w
    return val,frac,dp[n][capacity],list(reversed(chosen)),dp


def dijkstra(n, edges, source):
    g=[[] for _ in range(n)]
    for u,v,w in edges:g[u].append((v,w))
    d=[inf]*n;p=[None]*n; done=[False]*n; order=[];d[source]=0
    for _ in range(n):
        choices=[i for i in range(n) if not done[i]]
        if not choices:break
        u=min(choices,key=lambda x:d[x])
        if d[u]==inf:break
        done[u]=True;order.append(u)
        for v,w in g[u]:
            if not done[v] and d[u]+w<d[v]:d[v]=d[u]+w;p[v]=u
    return d,p,order


def bellman(n,edges,s):
    d=[inf]*n;p=[None]*n;d[s]=0
    for _ in range(n-1):
        changed=False
        for u,v,w in edges:
            if d[u]!=inf and d[u]+w<d[v]:d[v]=d[u]+w;p[v]=u;changed=True
        if not changed:break
    neg=any(d[u]!=inf and d[u]+w<d[v] for u,v,w in edges)
    return d,p,neg


def floyd_warshall(n,edges):
    d=[[inf]*n for _ in range(n)]
    for i in range(n):d[i][i]=0
    for u,v,w in edges:d[u][v]=min(d[u][v],w)
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if d[i][k]+d[k][j]<d[i][j]:d[i][j]=d[i][k]+d[k][j]
    return d


def warshall(n,edges):
    r=[[False]*n for _ in range(n)]
    for i in range(n):r[i][i]=True
    for u,v,_ in edges:r[u][v]=True
    for k in range(n):
        for i in range(n):
            for j in range(n):r[i][j]=r[i][j] or (r[i][k] and r[k][j])
    return r


def assembly(a,b,x1,x2,e1,e2,t1,t2,z1,z2):
    n=len(a); f1=[0]*n;f2=[0]*n;p1=[None]*n;p2=[None]*n
    f1[0]=e1+a[0];f2[0]=e2+b[0]
    trace=[]
    for j in range(1,n):
        stay1=f1[j-1]+a[j]; trans1=f2[j-1]+x2[j-1]+a[j]
        stay2=f2[j-1]+b[j]; trans2=f1[j-1]+x1[j-1]+b[j]
        f1[j]=min(stay1,trans1);p1[j]=1 if stay1<=trans1 else 2
        f2[j]=min(stay2,trans2);p2[j]=2 if stay2<=trans2 else 1
        trace.append((j+1,stay1,trans1,p1[j],stay2,trans2,p2[j]))
    end1=f1[-1]+z1;end2=f2[-1]+z2;line=1 if end1<=end2 else 2;total=min(end1,end2)
    route=[0]*n;route[-1]=line
    for j in range(n-1,0,-1):route[j-1]=p1[j] if route[j]==1 else p2[j]
    return total,route,trace,(end1,end2)


def kruskal(n,edges):
    parent=list(range(n));rank=[0]*n;chosen=[];work=0
    def find(x):
        while parent[x]!=x: parent[x]=parent[parent[x]];x=parent[x]
        return x
    for u,v,w in sorted(edges,key=lambda e:e[2]):
        work+=1;ru,rv=find(u),find(v)
        if ru!=rv:
            if rank[ru]<rank[rv]:ru,rv=rv,ru
            parent[rv]=ru
            if rank[ru]==rank[rv]:rank[ru]+=1
            chosen.append((u,v,w))
            if len(chosen)==n-1:break
    return chosen,work


def prim(n,edges):
    g=[[] for _ in range(n)]
    for u,v,w in edges:g[u].append((v,w));g[v].append((u,w))
    used={0};chosen=[];scans=0
    while len(used)<n:
        candidate=None
        for u in used:
            for v,w in g[u]:
                scans+=1
                if v not in used and (candidate is None or w<candidate[2]):candidate=(u,v,w)
        if candidate is None:raise ValueError('graph disconnected')
        chosen.append(candidate);used.add(candidate[1])
    return chosen,scans


def boruvka(n,edges):
    parent=list(range(n));components=n;chosen=[];rounds=[]
    def find(x):
        while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
        return x
    while components>1:
        best={}
        for e in edges:
            u,v,w=e;ru,rv=find(u),find(v)
            if ru!=rv:
                if ru not in best or w<best[ru][2]:best[ru]=e
                if rv not in best or w<best[rv][2]:best[rv]=e
        add=[]
        for e in best.values():
            u,v,w=e;ru,rv=find(u),find(v)
            if ru!=rv:parent[ru]=rv;components-=1;chosen.append(e);add.append(e)
        rounds.append(add)
        if not add:raise ValueError('graph disconnected')
    return chosen,rounds


def tsp(cost):
    n=len(cost);m=n-1;dp={};prev={}
    for j in range(1,n):dp[(1<<(j-1),j)]=cost[0][j];prev[(1<<(j-1),j)]=0
    for mask in range(1,1<<m):
        for j in range(1,n):
            if not mask>>(j-1)&1:continue
            key=(mask,j)
            if key in dp:continue
            pm=mask^(1<<(j-1));best=min((dp[(pm,k)]+cost[k][j],k) for k in range(1,n) if pm>>(k-1)&1)
            dp[key]=best[0];prev[key]=best[1]
    full=(1<<m)-1;last=min(range(1,n),key=lambda j:dp[(full,j)]+cost[j][0]);total=dp[(full,last)]+cost[last][0]
    route=[last];mask=full;j=last
    while mask!=(1<<(j-1)):
        k=prev[(mask,j)];mask^=1<<(j-1);j=k;route.append(j)
    route.reverse();return total,[0]+route+[0],len(dp),dp


def main():
    words='Dynamic programming helps engineers design efficient reliable algorithms'.split()
    print('TASK 1 WORD WRAP')
    for w in (16,20,24):
        dp,nxt,lines=word_wrap(words,w);print('width',w,'cost',dp[0]);print('lines',lines);print('dp',dp)
    print('boundary',word_wrap(['longword'],8)[0][0],word_wrap(['longword'],8)[2])
    print('\nTASK 2 KNAPSACK')
    items=[('A',10,60),('B',20,100),('C',30,120)]; print('cap 50',knapsack(50,items)[:4])
    bad=[('A',10,60),('B',20,100),('C',30,120)];print('counterexample cap 50; ratio greedy selects B then A; DP',knapsack(50,bad)[2:4])
    print('\nTASK 3 GRAPHS')
    edges=[(0,1,4),(0,2,2),(1,2,1),(1,3,5),(2,3,8),(2,4,10),(3,4,2),(3,5,6),(4,5,3),(4,6,4),(5,6,1),(6,7,2),(5,7,7),(1,7,20)]
    print('normal dijkstra',dijkstra(8,edges,0))
    neg=[(u,v,(20 if (u,v)==(1,3) else w)) for u,v,w in edges]+[(7,1,-16)];print('negative dijkstra',dijkstra(8,neg,0)[0]);print('bellman',bellman(8,neg,0)[0:3])
    cyc=neg+[(1,7,1)];print('negative cycle detected',bellman(8,cyc,0)[2])
    small=edges[:]
    print('Floyd matrix');[print(row) for row in floyd_warshall(8,small)]
    print('Warshall matrix');[print(''.join('1' if x else '0' for x in row)) for row in warshall(8,small)]
    print('\nTASK 4 ASSEMBLY')
    a=[7,9,3,4,8,4];b=[8,5,6,4,5,7];x1=[2,3,1,3,4];x2=[2,1,2,2,1]
    for title,aa,bb,xx1,xx2 in [('base',a,b,x1,x2),('transfer+20',a,b,[2,3,21,3,4],x2),('station3 slower',a[:2]+[13]+a[3:],b,x1,x2)]:
        print(title,assembly(aa,bb,xx1,xx2,2,4,[0]*5,[0]*5,3,2)[:3])
    print('\nTASK 5 MST')
    mst=[(0,1,4),(0,2,3),(1,2,1),(1,3,2),(2,3,4),(2,4,2),(3,4,3),(3,5,5),(4,5,3),(4,6,6),(5,6,2),(5,7,4),(6,7,1),(1,7,8)]
    for f in (kruskal,prim):
        chosen,work=f(8,mst);print(f.__name__,chosen,'cost',sum(e[2] for e in chosen),'work',work)
    ch,rounds=boruvka(8,mst);print('boruvka',ch,'cost',sum(e[2] for e in ch),'rounds',rounds)
    tied=[(u,v,1 if (u,v) in [(0,1),(0,2),(1,2)] else w) for u,v,w in mst];print('tie MST kruskal',kruskal(8,tied)[0])
    print('\nTASK 6 TSP')
    cost=[[0,10,15,20,12,18,9],[10,0,35,25,17,28,20],[15,35,0,30,22,16,27],[20,25,30,0,19,24,14],[12,17,22,19,0,13,21],[18,28,16,24,13,0,11],[9,20,27,14,21,11,0]]
    print('6 destinations',tsp(cost)[:3])
    small=[[0,10,15,20,12],[10,0,35,25,17],[15,35,0,30,22],[20,25,30,0,19],[12,17,22,19,0]]
    exact=tsp(small);exhaust=min((sum(small[r[i]][r[(i+1)%5]] for i in range(5)),r) for r in ((0,)+p for p in permutations(range(1,5))))
    print('4 destinations DP',exact[:3],'exhaustive',exhaust)
    for m in range(4,9):
        mat=[[0 if i==j else 1+((i*7+j*11)%31) for j in range(m+1)] for i in range(m+1)]
        t0=perf_counter();result=tsp(mat);elapsed=perf_counter()-t0
        print('n_dest',m,'states',result[2],'seconds',round(elapsed,6),'table entries',result[2])

if __name__=='__main__':main()
