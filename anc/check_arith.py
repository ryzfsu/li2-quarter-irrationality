#!/usr/bin/env python3
"""Exact checks of the arithmetic part of main.tex (Section 3, Lemma 4.1, Section 1 numbers, Appendix A).

Python standard library only; exact integers and Fractions. Reads the eighteen
intervals and Table A.1 from the LaTeX sources and recomputes them.
Run: python3 check_arith.py [--brute N1,N2,...]
"""
from fractions import Fraction as Q
from collections import Counter
import json, os, re, sys

if not __debug__:
    raise SystemExit('run without -O')

S = (157, 190, 215, 240, 265, 322, 323)


def fl(x):
    return x.numerator // x.denominator


def floors(x):
    return {a: fl(a*x) for a in S}


def gains(F):
    C = 2*F[240] - F[265] - F[215]
    return (C, 2*F[240] + 2*F[190] - F[215] - F[323] - F[322],
            2*F[240] + 2*F[215] - F[265] - F[323] - F[322],
            2*F[190] + F[157] - F[215] - F[322], 2*F[215] + F[157] - F[265] - F[322])


_here = os.path.dirname(os.path.abspath(__file__))
_tex = next(q for q in ('main.tex', os.path.join(_here, 'main.tex'), os.path.join(_here, '..', 'main.tex'))
            if os.path.exists(q))
tex = open(_tex).read()
rows_tex = tex.split(r'\endhead')[1].split(r'\end{longtable}')[0]
out = {}

# ---------------------------------------------------------------- intervals
block = tex.split(r'\mathcal E_1,\dots,\mathcal E_{18}$ be the open intervals')[1].split(r'\end{array}')[0]
pairs = re.findall(r'\((\d+)/(\d+),\\,(\d+)/(\d+)\)', block)
E = [(Q(int(a), int(b)), Q(int(c), int(d)), (int(a), int(b)), (int(c), int(d))) for a, b, c, d in pairs]
assert len(E) == 18, len(E)
Es = sorted(E)
assert all(x[1] <= y[0] for x, y in zip(Es, Es[1:])), 'E_i not disjoint'
assert Es[0][0] == Q(1, 322) and Es[-1][1] < Q(1, 5)
assert E[0][:2] == (Q(1, 322), Q(1, 265))

# ---------------------------------------------------------------- Table A.1
rows = []
for line in rows_tex.splitlines():
    line = line.strip()
    if not line or line == r'\hline':
        continue
    m = re.match(r'\$([\(\[])(\d+)/(\d+),(\d+)/(\d+)\)\$ & (.*) \\\\$', line)
    assert m, line
    br, k1, a1, k2, a2, rest = m.groups()
    cells = [c.strip() for c in rest.split('&')]
    rows.append((br, Q(int(k1), int(a1)), Q(int(k2), int(a2)), cells))
assert len(rows) == 45
used = set()
npieces = 0
for lo, hi, _, _ in E:
    pieces = [r for r in rows if lo <= r[1] and r[2] <= hi]
    assert pieces and pieces[0][1] == lo and pieces[-1][2] == hi, (lo, hi)
    assert pieces[0][0] == '(' and all(p[0] == '[' for p in pieces[1:])
    assert all(p[2] == q[1] for p, q in zip(pieces, pieces[1:]))
    for br, u, v, cells in pieces:
        used.add((u, v))
        npieces += 1
        # no jump of any F_a strictly inside (u, v); value on [u, v) is the value at u (or just right of u)
        for a in S:
            assert not any(u < Q(k, a) < v for k in range(fl(a*u), fl(a*v) + 2)), (u, v, a)
        Fv = floors((u + v)/2)
        if br == '[':
            assert floors(u) == Fv
        assert [int(c) for c in cells[:7]] == [Fv[a] for a in S], (u, v, cells[:7], Fv)
        g = gains(Fv)
        if lo == Q(1, 322):
            assert 'E3' in cells[7] and int(cells[-1]) == 1 and max(0, *g) == 0   # M = 0 on E_1
        else:
            assert [int(c) for c in cells[7:12]] == list(g), (u, v, cells[7:12], g)
            mu = int(cells[12])
            assert mu == 1 + (g[0] == 1)
            assert max(0, *g) >= mu
assert len(used) == 45 == npieces
out['table_A1_rows'] = npieces

# ---------------------------------------------------------------- Lemma 3.2 (states and floor bookkeeping)
def rho(t):
    h, j, k, l, m = t
    return (h, m, l, k, j)


def sigma(t):
    h, j, k, l, m = t
    add = lambda *v: tuple(map(sum, zip(*v)))
    neg = lambda v: tuple(-x for x in v)
    return (add(h, m, neg(k)), add(j, k, neg(m)), m, l, k)


def u_of(t):
    h, j, k, l, m = t
    add = lambda *v: tuple(map(sum, zip(*v)))
    neg = lambda v: tuple(-x for x in v)
    return (add(l, m, neg(j)), add(h, m, neg(k)), add(h, j, neg(l)), add(j, k, neg(m)))


def orbit(t):
    seen, todo = {t}, [t]
    while todo:
        w = todo.pop()
        for v in (rho(w), sigma(w)):
            if v not in seen:
                seen.add(v)
                todo.append(v)
    return seen


def aff(A, B):
    return (A, B)          # the integer A*N + B*lambda


for b in (190, 215):
    e = 2*b - 165
    t = (aff(240, 0), aff(240, 0), aff(b, 1), aff(157 + b, -1), aff(405 - b, 1))
    O = orbit(t)
    s1, s2, s3 = sigma(t), sigma(rho(sigma(t))), sigma(rho(sigma(rho(sigma(t)))))
    assert s1 == (aff(645 - 2*b, 0), aff(e, 0), aff(405 - b, 1), aff(157 + b, -1), aff(b, 1))
    assert s2 == (aff(323 - b, 1), aff(322, 0), aff(e, 0), aff(405 - b, 1), aff(157 + b, -1))
    assert s3 == (aff(240, 0), aff(240, 0), aff(322, 0), aff(e, 0), aff(405 - b, 1))
    assert u_of(t) == (aff(322, 0), aff(645 - 2*b, 0), aff(323 - b, 1), aff(e, 0))
    assert {s1, s2, s3} <= O
    for w in O:
        ms = sorted(list(w) + list(u_of(w)))
        assert ms == sorted(list(t) + list(u_of(t)))
        for A, B in ms:
            for lam in (0, b):          # lambda = 0 and lambda = bN, in units of N
                assert 0 <= A + B*lam <= 430
    # floor bookkeeping: sum floor(t) - sum floor(s) as formal multisets of (A,B)
    from collections import Counter
    def diff(s):
        c = Counter(t)
        c.subtract(Counter(s))
        return {k: v for k, v in c.items() if v}
    assert diff(s1) == {aff(240, 0): 2, aff(645 - 2*b, 0): -1, aff(e, 0): -1}
    assert diff(s2) == {aff(240, 0): 2, aff(b, 1): 1, aff(323 - b, 1): -1, aff(322, 0): -1, aff(e, 0): -1}
    assert diff(s3) == {aff(b, 1): 1, aff(157 + b, -1): 1, aff(322, 0): -1, aff(e, 0): -1}
    assert {645 - 2*b, e} == {265, 215}
# E3 state
t3 = (aff(240, 0), aff(240, 0), aff(190, 0), aff(157, 1), aff(215, 0))
s3p = sigma(rho(sigma(t3)))
assert s3p == (aff(323, -1), aff(132, 1), aff(215, 0), aff(215, 0), aff(157, 1))
assert u_of(s3p) == ((240, 0), (265, 0), (240, 0), (190, 0))
assert u_of(t3) == ((132, 1), (265, 0), (323, -1), (215, 0))
assert s3p in orbit(t3)
for A, B in list(t3) + list(u_of(t3)):
    for lam in (0, 190):
        assert 0 <= A + B*lam <= 430
assert 455 < 2*265 and 455 > 322   # 1 <= floor(455x) < 2 for 1/322 < x < 1/265
# (F1) for the tuple (240,240,190,157,215,165): H_1, H_2, alpha, beta
h_, j_, k_, l_, m_, q_ = 240, 240, 190, 157, 215, 165
assert (max(l_+q_, h_+m_-k_, h_+j_-l_, j_+k_-m_), max(l_+q_, min(h_+m_-k_, h_+j_-l_), j_+k_-m_),
        max(0, l_+q_-k_, l_+q_-m_), max(0, k_+l_-h_)) == (323, 322, 132, 107)
cE3 = Counter(t3)
cE3.subtract(Counter(s3p))
assert {k: v for k, v in cE3.items() if v} == {aff(240, 0): 2, aff(190, 0): 1, aff(215, 0): -1, aff(323, -1): -1, aff(132, 1): -1}
assert max(240, 190, 215) < 265          # these floors vanish for p > 265N
out['lemma_3_2_states'] = 'PASS'

# ---------------------------------------------------------------- Lemma 3.3 (band) and C periodicity
band = []
for k in range(1, 48):
    j = 5*k // 48
    rh = 5*k - 48*j
    ak = Q(k, 240)
    bk = Q(k - j, 215) if rh <= 21 else Q(k + j + 1, 265)
    assert bk == min(Q(k - j, 215), Q(k + j + 1, 265))
    assert 0 < rh < 48 and ak < bk <= Q(k + 1, 240)
    assert bk - ak == (Q(rh, 10320) if rh <= 21 else Q(48 - rh, 12720))
    for a in (215, 240, 265):
        assert not any(ak < Q(m, a) < bk for m in range(fl(a*ak), fl(a*bk) + 2))
    assert gains(floors((ak + bk)/2))[0] == 1
    band.append((k, j, rh, ak, bk))
# Table A.2, read from main.tex
tA2 = tex.split(r'\label{tab:band}')[1].split(r'\end{tabular}')[0]
rowsA2 = re.findall(r'(\d) & \$(\d+)\\le k\\le(\d+)\$ & \$(\d+),\\dots,(\d+)\$ & \$(\d+)\\le k\\le(\d+)\$ & \$(\d+),\\dots,(\d+)\$', tA2)
assert [int(r[0]) for r in rowsA2] == [0, 1, 2, 3, 4], rowsA2
for jj, l1, h1, v1, w1, l2, h2, v2, w2 in (tuple(map(int, r)) for r in rowsA2):
    assert [k for k, j, rh, _, _ in band if j == jj and rh <= 21] == list(range(l1, h1 + 1))
    assert [k for k, j, rh, _, _ in band if j == jj and rh >= 22] == list(range(l2, h2 + 1))
    assert (v1, w1) == (l1 - jj, h1 - jj) and (v2, w2) == (l2 + jj + 1, h2 + jj + 1)
for x in [Q(n, 997) for n in range(1, 1000)]:
    assert gains(floors(x + Q(1, 5)))[0] == gains(floors(x))[0]
assert band[0][3] > Q(1, 322) and Q(9, 5) + band[-1][4] < 2
out['band'] = 'PASS'

# ---------------------------------------------------------------- Proposition 3.4 on all of (1/322, 2)
cuts = sorted({Q(k, a) for a in S for k in range(0, 2*a + 1) if Q(1, 322) <= Q(k, a) <= 2})
def mu(x):
    inC = any(Q(r, 5) + ak < x < Q(r, 5) + bk for r in range(10) for _, _, _, ak, bk in band)
    inE = sum(1 for lo, hi, _, _ in E if lo < x < hi)
    return int(inC) + inE
checked = 0
for u, v in zip(cuts, cuts[1:]):
    for x in (u, (u + v)/2):
        if not (Q(1, 322) < x < 2):
            continue
        m = mu(x)
        if m == 0:
            continue
        checked += 1
        assert m <= 2
        if Q(1, 322) < x < Q(1, 265):
            assert m == 1 and gains(floors(x))[0] == 0
        else:
            assert max(0, *gains(floors(x))) >= m, (x, m, gains(floors(x)))
out['prop_3_4_points_with_mu_positive'] = checked

# ---------------------------------------------------------------- Lemma 4.1 (density)
def H(n):
    return sum((Q(1, i) for i in range(1, n + 1)), Q(0))
S1 = sum((Q(1, k - j) for k, j, rh, _, _ in band if rh <= 21), Q(0))
S2 = sum((Q(1, k + j + 1) for k, j, rh, _, _ in band if rh >= 22), Q(0))
d0 = sum((1/ak - 1/bk for *_, ak, bk in band), Q(0))/40
assert d0 == (240*H(47) - 215*S1 - 265*S2)/40 and d0 > Q('1.6187')
ell = sum((bk - ak for *_, ak, bk in band), Q(0))
m = sum(((bk*bk - ak*ak)/2 for *_, ak, bk in band), Q(0))/ell
assert ell == Q(1139, 22790) and m == Q(164041, 1640160)
jen = ell/40*sum((1/(Q(r, 5) + m)**2 for r in range(1, 10)), Q(0))
assert jen > Q('0.0260')
tail = sum((1/(Q(r, 5) + ak) - 1/(Q(r, 5) + bk) for r in range(1, 10) for *_, ak, bk in band), Q(0))/40
assert tail >= jen
ext = sum((1/lo - 1/hi for lo, hi, _, _ in E), Q(0))/40
assert ext == Q(202007398913, 64696932300) and ext > Q('3.1223')
assert d0 + jen + ext > Q('4.7670')
assert len(band)*10 + len(E) == 488


def trunc(x, n=10):
    i = x.numerator*10**n//x.denominator
    return f'{i//10**n}.{i % 10**n:0{n}d}'


out['density'] = {'delta_0': trunc(d0), 'jensen_tail': trunc(jen), 'extra': trunc(ext),
                  'lower_bound_sum': trunc(d0 + jen + ext), 'exact_delta': trunc(d0 + tail + ext)}
numB1 = re.findall(r'\$(-?\d+\.\d+)\\ldots\$', tex.split(r'\label{tab:num}')[1].split(r'\end{tabular}')[0])
assert numB1[3:] == [trunc(d0), trunc(jen), trunc(ext)], numB1
# Section 1: the primes 265N<p<322N contribute 57/40, and the rest of delta is below 3.35
assert (Q(322) - Q(265))/40 == Q(57, 40)
assert d0 + tail + ext - Q(57, 40) < Q('3.35')
assert '$57/40$ of $\\delta$' in tex and 'the rest of $\\delta$ is below $3.35<23.63856-18.87333$' in tex
assert Q('3.35') < Q('23.63856') - Q('18.87333')
assert r'\frac{202007398913}{64696932300}' in tex and r'=1139/22790' in tex and r'=164041/1640160' in tex

# ---------------------------------------------------------------- supplementary brute force (full orbits)
def brute(N):
    def isprime(n):
        if n < 2:
            return False
        i = 2
        while i*i <= n:
            if n % i == 0:
                return False
            i += 1
        return True
    ctx = []
    for b in (190, 215):
        t = (aff(240, 0), aff(240, 0), aff(b, 1), aff(157 + b, -1), aff(405 - b, 1))
        ctx.append((b, t, 'E1'))
    ctx.append((190, t3, 'E3'))
    fails = 0
    tested = 0
    for p in range(5, 323*N + 1):
        if p*p <= 430*N or not isprime(p):
            continue
        need = mu(Q(N, p))
        nat = (323*N >= p) + (322*N >= p)
        best = 0
        for b, t, kind in ctx:
            O = list(orbit(t))
            worst = None
            for lam in range(b*N + 1):
                ev = lambda f: f[0]*N + f[1]*lam
                base = sum(ev(f)//p for f in t)
                binom = (b*N)//p - lam//p - (b*N - lam)//p
                g = None
                for w in O:
                    uu = [ev(f) for f in u_of(w)]
                    Hs = max(uu) >= p
                    Ks = uu[0] >= p or min(uu[1], uu[2]) >= p or uu[3] >= p
                    val = nat + binom + base - sum(ev(f)//p for f in w) - Hs - Ks
                    g = val if g is None else max(g, val)
                worst = g if worst is None else min(worst, g)
                if worst <= best:
                    break
            best = max(best, worst)
        tested += 1
        if best < need:
            fails += 1
            print('FAIL', N, p, need, best)
    return tested, fails


if '--brute' in sys.argv:
    Ns = [int(v) for v in sys.argv[sys.argv.index('--brute') + 1].split(',')]
    out['brute'] = {}
    for N in Ns:
        tested, fails = brute(N)
        assert fails == 0
        out['brute'][N] = {'primes': tested, 'failures': fails}

out['status'] = 'PASS'
print(json.dumps(out, indent=1))
