# Ancillary files: exact checks for "Irrationality of the dilogarithm at 1/4"

The proof in the paper is complete without these scripts. They recheck part of it: the finite statements
listed in Table C.1 (the floor table, the tables of constants, the orbit tuples, the density bounds, and
the analytic constants), in exact rational arithmetic, using only the Python 3 standard library.

- `check_arith.py` — Table A.1 and the intervals E_i as printed in `main.tex`, Table A.2, Lemma 3.3, the
  tuples and floor sums of Lemma 3.2, Proposition 3.4 on (1/322, 2), Lemma 4.1, and rows 4–6 of Table B.1.
  With `--brute 1,2,3,4,5,6,7,8` it also compares the full Rhin–Viola orbit bound with mu(N/p) for N <= 8.
- `check_analytic.py` — the constants of Lemmas 5.1–5.5, rows 1–3 of Table B.1, Table B.2, and
  23.63856 - 4.7670 - 18.87333 = -0.00177.
- `*_result.json` — outputs of the runs below.

The scripts read `main.tex` from the current directory, from their own directory, or from the parent
directory (the arXiv source layout). Run from this directory:

    python3 check_arith.py                              # about 10 s
    python3 check_arith.py --brute 1,2,3,4,5,6,7,8      # about 3 min
    python3 check_analytic.py                           # under 1 s
