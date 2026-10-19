from math import comb
import random
def binom_cdf(k,n,p): return sum(comb(n,i)*p**i*(1-p)**(n-i) for i in range(0,k+1))
print("P3 per-field: P(field <= 7/12 | p)")
for p in (0.95,0.9,0.85,0.8,0.7,0.6):
    f=binom_cdf(7,12,p)
    print(f"  p={p}: per-field fail {f:.3f}; any of 16 fields fails {1-(1-f)**16:.3f}; any of 25 {1-(1-f)**25:.3f}")
print("P4 per-item: any of 9 QA items <=7/12")
for p in (0.9,0.85,0.8,0.7):
    f=binom_cdf(7,12,p); print(f"  p={p}: {1-(1-f)**9:.3f}")
print("P5: P(>=9/12 | p)")
for p in (0.5,0.6,0.7,0.75,0.8,0.9):
    print(f"  p={p}: pass {1-binom_cdf(8,12,p):.3f}")
# hypergeometric multimodal
def hyp0(N,K,n): 
    return comb(N-K,n)/comb(N,n)
print("P(no b/ab in 12 of 608 with 53):", round(hyp0(608,53,12),3), " in 30:", round(hyp0(608,53,30),3))
print("expected b/ab in 12:", 12*53/608)
# pooled kappa simulation with paper clustering
def kappa(pairs):
    n=len(pairs); cats=set(a for a,b in pairs)|set(b for a,b in pairs)
    po=sum(a==b for a,b in pairs)/n
    pe=sum((sum(a==c for a,b in pairs)/n)*(sum(b==c for a,b in pairs)/n) for c in cats)
    return (po-pe)/(1-pe) if pe<1 else float('nan')
random.seed(7)
fields=[ [0.85,0.1,0.05],[0.9,0.05,0.05],[0.6,0.3,0.1],[0.5,0.3,0.2],[0.4,0.3,0.2,0.1],[0.7,0.2,0.1],[0.8,0.2],[0.6,0.4],[0.95,0.05],[0.5,0.25,0.25],[0.7,0.15,0.15],[0.55,0.45],[0.6,0.2,0.2],[0.9,0.1],[0.65,0.35],[0.75,0.25]]
def sim(npap, acc, sd=0.12, reps=3000):
    out=[]
    for _ in range(reps):
        pairs=[]
        for p in range(npap):
            a=min(0.99,max(0.3,random.gauss(acc,sd)))
            for dist in fields:
                k=len(dist); t=random.choices(range(k),dist)[0]
                def rate():
                    if random.random()<a: return t
                    return random.choice([c for c in range(k) if c!=t])
                pairs.append((rate(),rate()))
        out.append(kappa(pairs))
    out.sort()
    return out
for acc in (0.80,0.85,0.90):
    big=sim(400,acc,reps=60); truek=sum(big)/len(big)
    for n in (12,24,36):
        o=sim(n,acc,reps=1500)
        pass70=sum(x>=0.70 for x in o)/len(o)
        lo,hi=o[int(0.05*len(o))],o[int(0.95*len(o))]
        print(f"acc={acc} true pooled kappa~{truek:.2f} n={n}: 90% range [{lo:.2f},{hi:.2f}] P(est>=0.70)={pass70:.2f}")
