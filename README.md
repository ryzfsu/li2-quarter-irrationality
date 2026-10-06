# Irrationality of the dilogarithm at 1/4

Ruiyi Zhang

This repository contains the manuscript proving that `Li_2(1/4)` is irrational, its
LaTeX source, and the ancillary verification files.

- `main.tex`, `main.pdf` (12 pages)
- `anc/` - two Python 3 scripts that recheck, in exact rational arithmetic, the finite
  statements of the paper (the floor table, the tables of constants, the orbit tuples,
  the density bounds and the analytic constants), together with the recorded outputs.
  The proof is complete without them. See `anc/README.md`.
- `SHA256SUMS`

The source is the payload submitted to arXiv on 2026-09-29 as `submit/8148488`;
`main.tex` and `anc/` are byte-identical to that stored source. The paper carries no
arXiv identifier.

## Build

    pdflatex main.tex
    pdflatex main.tex

## Checks

    cd anc && python3 check_arith.py && python3 check_analytic.py
