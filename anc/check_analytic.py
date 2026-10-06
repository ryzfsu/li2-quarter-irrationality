#!/usr/bin/env python3
"""Exact checks of the analytic constants and identities in main.tex (Lemmas 5.1-5.5, Section 6, Appendix B).

Python standard library only. All decisions use fractions.Fraction; logarithms are
enclosed by the atanh series with an explicit tail bound. Run: python3 check_analytic.py
"""
from fractions import Fraction as F
import json, os

if not __debug__:
    raise SystemExit('run without -O')

TERMS = 30


def log_unit(q):
    """Enclosure of log q for 1 <= q <= 2."""
    assert 1 <= q <= 2
    z = (q - 1) / (q + 1)
    s = 2 * sum((z**(2*k + 1) / (2*k + 1) for k in range(TERMS)), F(0))
    tail = 2 * z**(2*TERMS + 1) / ((2*TERMS + 1) * (1 - z*z))
    return s, s + tail


LOG2 = log_unit(F(2))


def log_enc(q):
    q = F(q)
    assert q > 0
    e = 0
    while q < 1:
        q *= 2
        e -= 1
    while q > 2:
        q /= 2
        e += 1
    lo, hi = log_unit(q)
    if e >= 0:
        return lo + e*LOG2[0], hi + e*LOG2[1]
    return lo + e*LOG2[1], hi + e*LOG2[0]


def lin(terms):
    """Enclosure of sum c*log(q) for rational c."""
    lo = hi = F(0)
    for c, q in terms:
        a, b = log_enc(q)
        c = F(c)
        lo += c*a if c > 0 else c*b
        hi += c*b if c > 0 else c*a
    return lo, hi


def trunc(x, n=10):
    s = -1 if x < 0 else 1
    v = abs(x)
    i = v.numerator * 10**n // v.denominator
    return ('-' if s < 0 else '') + f'{i // 10**n}.{i % 10**n:0{n}d}'


out = {}

# Lemma 5.1: powers of 4 and of (4 - eta) in the substitution.
# powers of 4: z^{k-l-q}, (1-y)^l, (1+3y)^{j+q-m}, denominator, dy
assert -132 + 157 + 190 - 215 == 0
# powers of (4-eta): y^k, (1-y)^l, (1+3y)^{190N}, denominator^{-(215N+1)}, dy -> -(322N+1)
assert -190 - 157 - 190 + 215 == -322 and 1 - 2 == -1
assert 190 % 2 == 0

# Lemma 5.2, upper bound: weighted AM-GM constant and one-variable maxima.
assert F(215, 25) == F(43, 5) and F(215, 190) == F(43, 38)
xm = F(215, 455)
assert xm == F(43, 91) and 215/xm - 240/(1 - xm) == 0
tm = F(73, 22)
assert 190/(1 + tm) - 322/(4 + tm) == 0
MR = lin([(25, F(5, 43)), (190, F(38, 43)), (215, F(43, 91)), (240, F(48, 91)),
          (190, F(95, 22)), (-322, F(161, 22))])
rate_MR = (-MR[1]/40, -MR[0]/40)
assert rate_MR[0] > F('18.87333')
out['rate_Phi_plus'] = [trunc(rate_MR[0]), trunc(rate_MR[1])]
assert (1 + log_enc(4)[1]) / 3 < 1

# Lemma 5.2, lower bound on the box [0.4711,0.4713]x[3.3999,3.4001].
xl, xh, tl, th = F('0.4711'), F('0.4713'), F('3.3999'), F('3.4001')
assert 1 - xh == F('0.5287') and 1 + tl == F('4.3999') and xh + th == F('3.8714') and 4 + th == F('7.4001')
PHI = lin([(240, xl), (240, 1 - xh), (190, tl), (190, 1 + tl), (-215, xh + th), (-322, 4 + th)])
rate_low = (-PHI[1]/40, -PHI[0]/40)
assert rate_low[1] < F('18.88')
assert (xh + th) * (4 + th) < 29
assert F(4, 10**8) / 29 > F(1, 10**9)
out['rate_Phi_minus'] = [trunc(rate_low[0]), trunc(rate_low[1])]

# Lemma 5.3: arc identities checked as polynomial identities at enough rational points.
def cnorm2(re, im):
    return re*re + im*im
pts = [F(k, 7) for k in range(8)]
for t in pts:
    # |t + A(1-t)|^2 with A=(3+4i)/5
    assert cnorm2(t + F(3, 5)*(1 - t), F(4, 5)*(1 - t)) == 1 - F(4, 5)*t*(1 - t)
    # |u + B(1-u)|^2 with B=(5-12i)/13
    assert cnorm2(t + F(5, 13)*(1 - t), -F(12, 13)*(1 - t)) == 1 - F(16, 13)*t*(1 - t)
    assert cnorm2(t + F(5, 13)*(1 - t), -F(12, 13)*(1 - t)) - t*t == (1 - t)*(13 - 3*t)/13
assert 1 - F(4, 5)*F(1, 4) == F(4, 5) and 1 - F(16, 13)*F(1, 4) == F(9, 13)
assert F(3, 5)*F(5, 13) + F(4, 5)*(-F(12, 13)) == -F(33, 65)      # Re(B conj(A))
assert (1 - (-F(33, 65)))/2 == F(49, 65) and (1 - F(5, 13))/2 == F(4, 13)
assert F(49, 65) > F(4, 5)**2
assert F(5, 4)*F(13, 9) < 2
# t(1-t) <= omega on a grid (the proof is algebraic; this is a sanity check)
for t in pts:
    for u in pts:
        assert t*(1 - t) <= t*(1 - u) + u*(1 - t)

# Lemma 5.5: exact values at the three rational points.
def data(r, s):
    a1 = r*r + F(6, 5)*r + 1
    a2 = s*s + F(10, 13)*s + 1
    a3 = r*r + F(66, 65)*r*s + s*s
    a4 = 9*s*s + F(120, 13)*s + 16
    return a1, a2, a3, a4


def grad(r, s):
    a1, a2, a3, a4 = data(r, s)
    LR = 240 - 265*r*(r + F(3, 5))/a1 - 215*r*(r + F(33, 65)*s)/a3
    LS = 190 + 157*s*(s + F(5, 13))/a2 - 215*s*(s + F(33, 65)*r)/a3 - 322*s*(9*s + F(60, 13))/a4
    return LR, LS


# moduli and cosh forms of a_1..a_4: rational-function identities, checked exactly on an 11x11 grid
def cmul(a, b):
    return (a[0]*b[0] - a[1]*b[1], a[0]*b[1] + a[1]*b[0])
def cdiv(a, b):
    n = b[0]**2 + b[1]**2
    return ((a[0]*b[0] + a[1]*b[1])/n, (a[1]*b[0] - a[0]*b[1])/n)
def nrm2(a):
    return a[0]**2 + a[1]**2
ch = lambda w: (w + 1/w)/2
for r in [F(k, 7) for k in range(1, 12)]:
    for s in [F(k, 5) for k in range(1, 12)]:
        X = cdiv((r, F(0)), (r + F(3, 5), F(4, 5)))
        Y = cdiv((s, F(0)), (s + F(5, 13), -F(12, 13)))
        a1, a2, a3, a4 = data(r, s)
        assert nrm2(cmul(X, (1 - X[0], -X[1]))) == (r/a1)**2
        assert nrm2(cmul(Y, (1 - Y[0], -Y[1]))) == (s/a2)**2
        assert nrm2((X[0] - Y[0], X[1] - Y[1])) == a3/(a1*a2)
        assert nrm2((4 - Y[0], -Y[1])) == a4/a2
        assert a1 == 2*r*(ch(r) + F(3, 5)) and a2 == 2*s*(ch(s) + F(5, 13))
        assert a3 == 2*r*s*(ch(r/s) + F(33, 65)) and a4 == 24*s*(ch(3*s/4) + F(5, 13))
# exponents of L from Psi, and the cosh form of L
assert -240 + F(215, 2) == -F(265, 2) and -190 + F(215, 2) + 161 == F(157, 2)
assert 240 - F(265, 2) - F(215, 2) == 0 and 190 + F(157, 2) - F(215, 2) - 161 == 0
assert -F(265, 2) + F(157, 2) - F(215, 2) == -F(323, 2)
g1 = grad(F(29, 25), F(139, 100))
g2 = grad(F(59, 50), F(71, 50))
g3 = grad(F(117, 100), F(7, 5))
assert g1[0] > 0 and g1[1] > 0
assert g2[0] < 0 and g2[1] < 0
assert -F(1, 4) < g3[0] < 0 < g3[1] < F(3, 10)
a1, a2, a3, a4 = data(F(117, 100), F(7, 5))
assert (a1, a2, a3, a4) == (F(37729, 10000), F(1312, 325), F(49921, 10000), F(15133, 325))
Lval = lin([(240, F(117, 100)), (190, F(7, 5)), (-F(265, 2), a1), (F(157, 2), a2),
            (-F(215, 2), a3), (-161, a4)])
assert Lval[1] < F('-755.99')
assert F(1, 4)*F(1, 116) + F(3, 10)*F(1, 70) == F(1, 464) + F(3, 700)
assert F(117, 116) - 1 == F(1, 116) and F(71, 70) - 1 == F(1, 70)   # log(1+1/n) < 1/n
assert F('-755.99') + F(1, 464) + F(3, 700) < F('-755.98')
assert F('755.98') == 40*F('18.8995')
assert 161*F(9, 16) > F(157, 2)
# Lemma 5.5: (log l'')' = -sinh v (2+g cosh v-g^2)/((1+g cosh v)(cosh v+g)) and |.| < 2,
# checked at cosh v = (w+1/w)/2, sinh v = (w-1/w)/2 for rational w > 0 and 0 < g < 1
for w in [F(k, 3) for k in range(1, 13)]:
    c, sh = (w + 1/w)/2, (w - 1/w)/2
    assert c*c - sh*sh == 1
    for g in (F(3, 5), F(5, 13), F(33, 65), F(1, 7), F(6, 7)):
        lhs = g*sh/(1 + g*c) - 2*sh/(c + g)           # derivative of log((1+g c)/(c+g)^2)
        assert lhs == -sh*(2 + g*c - g*g)/((1 + g*c)*(c + g))
        assert 2 + g*c - g*g <= 2*(1 + g*c) and abs(sh) < c + g
        assert abs(lhs) < 2
# e^{-2 log(4/3)} = 9/16
assert F(3, 4)**2 == F(9, 16)
# amplitude 5*pi/24 < 1 uses pi < 4
assert 2*F(5, 4)*F(1, 3)/4 * 4 == F(5, 6)
out['gradient'] = {k: [trunc(v[0], 5), trunc(v[1], 5)] for k, v in
                   (('29/25,139/100', g1), ('59/50,71/50', g2), ('117/100,7/5', g3))}
out['L(117/100,7/5)'] = [trunc(Lval[0], 5), trunc(Lval[1], 5)]

# Lemma 4.1 and Section 6: the constant c_D and the final inequality.
c0 = ((645 + 132*log_enc(4)[0] + 107*log_enc(3)[0])/40, (645 + 132*log_enc(4)[1] + 107*log_enc(3)[1])/40)
assert c0[1] < F('23.63856')
out['c_D'] = [trunc(c0[0]), trunc(c0[1])]
assert 40*F('18.88') == F('755.2') and 40*F('18.87333') == F('754.9332')
assert F('23.63856') - F('4.7670') - F('18.87333') == F('-0.00177')
assert F('18.88') < F('18.8995')
# Tables B.1 (rows 1-3) and B.2 as printed in main.tex
import re
_here = os.path.dirname(os.path.abspath(__file__))
_tex = next(q for q in ('main.tex', os.path.join(_here, 'main.tex'), os.path.join(_here, '..', 'main.tex'))
            if os.path.exists(q))
tex = open(_tex).read()
blk = lambda lab: tex.split(r'\label{' + lab + '}')[1].split(r'\end{tabular}')[0]
num = re.findall(r'\$(-?\d+\.\d+)\\ldots\$', blk('tab:num'))
assert len(num) == 6 and all(out[k] == [v, v] for k, v in zip(('rate_Phi_plus', 'rate_Phi_minus', 'c_D'), num[:3])), num
grd = re.findall(r'\$(-?\d+\.\d+)\\ldots\$', blk('tab:grad'))
assert grd == [x for v in out['gradient'].values() for x in v] + [out['L(117/100,7/5)'][0]], grd
assert out['L(117/100,7/5)'][0] == out['L(117/100,7/5)'][1]
out['status'] = 'PASS'
print(json.dumps(out, indent=1))
