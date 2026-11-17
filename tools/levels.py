"""Генератор и проверка уровней «Сокобан у костра».
Бочка, затолканная на горящий костёр, исчезает, костёр гаснет. Цель — потушить все костры.
Запуск: python3 levels.py  -> печатает JSON с 30 уровнями (проверенными решателем)."""
import random, json, math, sys
from collections import deque

DIRS = [(0,-1),(0,1),(-1,0),(1,0)]

def parse(m):
    H=len(m); W=max(len(r) for r in m)
    floor=set(); P=None; B=[]; F=[]
    for y,r in enumerate(m):
        for x,ch in enumerate(r.ljust(W)):
            if ch in '.PBF': floor.add((x,y))
            if ch=='P': P=(x,y)
            if ch=='B': B.append((x,y))
            if ch=='F': F.append((x,y))
    return floor,P,B,F

def solve(m, limit=300000):
    floor,P,B,F=parse(m)
    fidx={f:i for i,f in enumerate(F)}; allout=(1<<len(F))-1
    def reach(p,bs,out):
        blocked=set(bs)|{f for f,i in fidx.items() if not out>>i&1}
        seen={p}; q=[p]
        for c in q:
            for dx,dy in DIRS:
                n=(c[0]+dx,c[1]+dy)
                if n in floor and n not in blocked and n not in seen: seen.add(n); q.append(n)
        return seen
    def key(p,bs,out):
        r=reach(p,bs,out); return (min(r),bs,out),r
    k0,r0=key(P,tuple(sorted(B)),0)
    seen={k0:None}; q=deque([(k0,r0,0)])
    while q:
        (cp,bs,out),r,d=q.popleft()
        for b in bs:
            for dx,dy in DIRS:
                if (b[0]-dx,b[1]-dy) not in r: continue
                t=(b[0]+dx,b[1]+dy)
                if t not in floor or t in bs: continue
                nb=[x for x in bs if x!=b]; nout=out
                if t in fidx and not out>>fidx[t]&1: nout|=1<<fidx[t]
                else: nb.append(t)
                nb=tuple(sorted(nb))
                if nout==allout: return d+1,len(seen)
                k,rr=key(b,nb,nout)
                if k in seen: continue
                seen[k]=1
                if len(seen)>limit: return None,len(seen)
                q.append((k,rr,d+1))
    return None,len(seen)

def gen(rng, W, H, nbar, pillars):
    g=[['#']*W for _ in range(H)]
    for _ in range(rng.randint(3,6)):
        w=rng.randint(2,4); h=rng.randint(2,4)
        x=rng.randint(1,W-1-w); y=rng.randint(1,H-1-h)
        for yy in range(y,y+h):
            for xx in range(x,x+w): g[yy][xx]='.'
    fl=[(x,y) for y in range(H) for x in range(W) if g[y][x]=='.']
    for _ in range(pillars):
        x,y=rng.choice(fl); g[y][x]='#'
    fl=[(x,y) for y in range(H) for x in range(W) if g[y][x]=='.']
    if not fl: return None
    # оставить крупнейшую связную область
    best=set()
    left=set(fl)
    while left:
        s=left.pop(); comp={s}; q=[s]
        for c in q:
            for dx,dy in DIRS:
                n=(c[0]+dx,c[1]+dy)
                if n in left: left.discard(n); comp.add(n); q.append(n)
        if len(comp)>len(best): best=comp
    if len(best)<14: return None
    for (x,y) in fl:
        if (x,y) not in best: g[y][x]='#'
    cells=list(best); rng.shuffle(cells)
    need=3+nbar+1
    if len(cells)<need+6: return None
    for c in cells[:3]: g[c[1]][c[0]]='F'
    for c in cells[3:3+nbar]: g[c[1]][c[0]]='B'
    p=cells[3+nbar]; g[p[1]][p[0]]='P'
    # стены, не касающиеся пола — пустота
    for y in range(H):
        for x in range(W):
            if g[y][x]=='#' and not any(0<=y+j<H and 0<=x+i<W and g[y+j][x+i] in '.PBF' for i in (-1,0,1) for j in (-1,0,1)):
                g[y][x]=' '
    rows=[''.join(r) for r in g]
    # обрезать пустые края
    while rows and not rows[0].strip(): rows.pop(0)
    while rows and not rows[-1].strip(): rows.pop()
    lft=min(len(r)-len(r.lstrip()) for r in rows)
    rows=[r[lft:].rstrip() for r in rows]
    w=max(map(len,rows)); rows=[r.ljust(w) for r in rows]
    return rows

def score(m):
    pushes,states=solve(m)
    if pushes is None: return None
    floor,P,B,F=parse(m)
    direct=sum(min(abs(b[0]-f[0])+abs(b[1]-f[1]) for f in F) for b in B[:3])
    return pushes, states, pushes + 2*max(0,pushes-direct) + 2*math.log2(states+1)

if __name__=='__main__':
    rng=random.Random(int(sys.argv[1]) if len(sys.argv)>1 else 2026)
    pool=[]
    tries=0
    while len(pool)<900 and tries<20000:
        tries+=1
        stage=rng.random()
        W=rng.randint(7,10); H=rng.randint(7,10)
        nbar=3 if rng.random()<0.7 else 4
        m=gen(rng,W,H,nbar,rng.randint(0,4))
        if not m: continue
        s=score(m)
        if not s or s[0]<5: continue
        pool.append((s[2],s[0],s[1],m))
    pool.sort(key=lambda t:t[0])
    print(len(pool),'candidates; score range',pool[0][0],pool[-1][0],file=sys.stderr)
    json.dump(pool,open(sys.argv[2] if len(sys.argv)>2 else 'pool.json','w'))
