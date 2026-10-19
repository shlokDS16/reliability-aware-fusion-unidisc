import random
def kappa(pairs):
    n=len(pairs); cats=set(a for a,b in pairs)|set(b for a,b in pairs)
    po=sum(a==b for a,b in pairs)/n
    pe=sum((sum(a==c for a,b in pairs)/n)*(sum(b==c for a,b in pairs)/n) for c in cats)
    return po,(po-pe)/(1-pe)
fields=[[0.85,0.1,0.05],[0.9,0.05,0.05],[0.6,0.3,0.1],[0.5,0.3,0.2],[0.4,0.3,0.2,0.1],[0.7,0.2,0.1],[0.8,0.2],[0.6,0.4],[0.95,0.05],[0.5,0.25,0.25],[0.7,0.15,0.15],[0.55,0.45],[0.6,0.2,0.2],[0.9,0.1],[0.65,0.35],[0.75,0.25]]
random.seed(3)
def sim(npap,acc,sd=0.12,reps=1500):
    res=[]
    for _ in range(reps):
        P=[];N=[];per={fi:[] for fi in range(len(fields))}
        for p in range(npap):
            a=min(0.99,max(0.3,random.gauss(acc,sd)))
            for fi,dist in enumerate(fields):
                k=len(dist); t=random.choices(range(k),dist)[0]
                r=lambda: t if random.random()<a else random.choice([c for c in range(k) if c!=t])
                x,y=r(),r()
                P.append((x,y)); N.append(((fi,x),(fi,y))); per[fi].append((x,y))
        po,kp=kappa(P); _,kn=kappa(N)
        ks=[]
        undefined=0
        for fi in per:
            cats=set(a for a,b in per[fi])|set(b for a,b in per[fi])
            if len(cats)==1: undefined+=1; continue
            ks.append(kappa(per[fi])[1])
        res.append((po,kp,kn,sum(ks)/len(ks),undefined))
    return res
for acc in (0.85,0.9,0.95):
    for n in (12,30):
        r=sim(n,acc)
        m=lambda i: sum(x[i] for x in r)/len(r)
        q=sorted(x[2] for x in r)
        print(f"acc={acc} n={n}: raw {m(0):.2f}; pooled kappa shared labels {m(1):.2f}; namespaced {m(2):.2f} (90% range {q[75]:.2f}-{q[1424]:.2f}); mean per-field kappa {m(3):.2f}; fields with undefined kappa per pilot {m(4):.1f}")
