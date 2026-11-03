# Irrationality of the dilogarithm at 1/4

Ruiyi Zhang

DOI: [10.5281/zenodo.23247746](https://doi.org/10.5281/zenodo.23247746)

This repository contains the manuscript proving that `Li_2(1/4)` is irrational, its
LaTeX source, and the ancillary verification files.

- `main.tex`, `main.pdf` (12 pages)
- `anc/` - two Python 3 scripts that recheck, in exact rational arithmetic, the finite
  statements of the paper (the floor table, the tables of constants, the orbit tuples,
  the density bounds and the analytic constants), together with the recorded outputs.
  The proof is complete without them. See `anc/README.md`.
- `SHA256SUMS`

## Build

    pdflatex main.tex
    pdflatex main.tex

## Checks

    cd anc && python3 check_arith.py && python3 check_analytic.py

## Citation

Ruiyi Zhang, *Irrationality of the dilogarithm at 1/4*, preprint, Zenodo, 2026. https://doi.org/10.5281/zenodo.23247746

```bibtex
@misc{zhang2026li2quarter,
  author    = {Zhang, Ruiyi},
  title     = {Irrationality of the dilogarithm at 1/4},
  year      = {2026},
  publisher = {Zenodo},
  note      = {Preprint},
  doi       = {10.5281/zenodo.23247746},
  url       = {https://doi.org/10.5281/zenodo.23247746}
}
```
