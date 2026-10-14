import itertools, math, random
import numpy as np
random.seed(0); np.random.seed(0)
# toy joint over L=3 tokens, V=3
L,V=3,3
p0=np.random.dirichlet(np.ones(V**L)).reshape((V,)*L)
# (1) masked-cross-entropy identity: sum_k 1/k E_{|S^c|=k} sum_{i in S^c} -log p(x_i|x_S) == E_pi sum_l -log p(x_pi(l)|x_pi(<l)) for TRUE conditionals
def cond(x,i,S):  # p0(x_i | x_S)
    idx=[slice(None)]*L
    for j in S: idx[j]=x[j]
    sub=p0[tuple(idx)]
    # marginalize others
    axes=tuple(a for a in range(L) if a not in S)
    m=p0
    m_num=np.sum(p0, axis=tuple(a for a in range(L) if a not in S and a!=i)) if True else None
    # build joint over (S,i)
    keep=sorted(list(S)+[i])
    marg=np.sum(p0,axis=tuple(a for a in range(L) if a not in keep))
    pos={a:n for n,a in enumerate(keep)}
    ix=[None]*len(keep)
    for j in S: ix[pos[j]]=x[j]
    ix[pos[i]]=slice(None)
    vec=marg[tuple(ix)]
    return vec[x[i]]/vec.sum()
def lhs(x):
    tot=0
    for k in range(1,L+1):
        sets=[S for S in itertools.combinations(range(L),L-k)]
        e=0
        for S in sets:
            e+=sum(-math.log(cond(x,i,S)) for i in range(L) if i not in S)
        tot+=e/len(sets)/k
    return tot
def rhs(x):
    tot=0; perms=list(itertools.permutations(range(L)))
    for pi in perms:
        tot+=sum(-math.log(cond(x,pi[l],set(pi[:l]))) for l in range(L))
    return tot/len(perms)
x=(0,2,1); print("masked-CE sum_k(1/k)E vs E_pi AO-AR:",lhs(x),rhs(x))
# (2) Beta integral: int_0^1 lam^(k-1)(1-lam)^(L-k) dlam = (k-1)!(L-k)!/L!  and uniform count under linear schedule
for k in range(1,L+1):
    num=sum(( (j/2000+1/4000)**(k-1)*(1-(j/2000+1/4000))**(L-k))/2000 for j in range(2000))
    print(k,num,math.factorial(k-1)*math.factorial(L-k)/math.factorial(L))
Ls=5
for k in range(Ls+1):
    val=sum(math.comb(Ls,k)*(j/2000+1/4000)**k*(1-(j/2000+1/4000))**(Ls-k)/2000 for j in range(2000))
    print("count",k,round(val,4),round(1/(Ls+1),4))
# (3) uniform-channel ratio formula (single token), compare with direct ratio
Vn=5; a=0.37; b=(1-a)/Vn
# q(j|x0)= a*delta + b (uniform channel per D3PM/MDLM eq 6: alpha x + (1-alpha) pi)
pd=np.random.dirichlet(np.ones(Vn))
def q(j,x0): return a*(j==x0)+b
pt=np.array([sum(q(j,x0)*pd[x0] for x0 in range(Vn)) for j in range(Vn)])
xt=1; xh=3
direct=pt[xh]/pt[xt]
post=np.array([q(xt,x0)*pd[x0] for x0 in range(Vn)]); post/=post.sum()
formula=(b/(b+a))*post[xt]+((b+a)/b)*post[xh]+(1-post[xt]-post[xh])
print("uniform ratio direct vs affine-in-posterior formula:",direct,formula)
# absorbing: ratio = alpha/(1-alpha) * p0(xh) (single token, xt=mask)
al=0.4; print("absorb single token:", (al*pd[xh])/(1-al), al/(1-al)*pd[xh])
# (4) ARDM: k*L_t - sum_{i<k} L_{t+i} = E_sigma TC(x_sigma(t..t+k-1) | x_sigma(<t)) for exact conditionals
def H(joint): 
    j=joint[joint>0]; return -(j*np.log(j)).sum()
def condH(keep_target, cond_set):
    # H(X_target | X_cond)
    def marg(keys):
        keys=sorted(keys); return np.sum(p0,axis=tuple(a for a in range(L) if a not in keys))
    return H(marg(list(cond_set)+list(keep_target)))-(H(marg(list(cond_set))) if cond_set else 0)
perms=list(itertools.permutations(range(L)))
def Lt(t): # t=1..L : E_sigma H(X_sigma(t)|X_sigma(<t)) (exact)
    return np.mean([condH([pi[t-1]],list(pi[:t-1])) for pi in perms])
t,k=1,2
lhs_=k*Lt(t)-sum(Lt(t+i) for i in range(k))
def TC(pi):
    tg=list(pi[t-1:t-1+k]); c=list(pi[:t-1])
    return sum(condH([g],c) for g in tg)-condH(tg,c)
print("ARDM k*L_t - sum L_{t+i}:",lhs_," E TC:",np.mean([TC(pi) for pi in perms]))
