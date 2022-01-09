# pdf2up

A small utility to generate preview images of research papers (e.g. arXiv)
suitable for social media (e.g. Twitter)

## Installation

To install as a command line tool `pdf2up` run:

```sh
pip install pdf2up
```

## Usage

Run on the command line as `pdf2up input.pdf`, optionally with the following flags:

```
usage: pdf2up [-h] [-b BOX [BOX ...]] [--all] [-s SKIP] [-n N_UP] input

positional arguments:
  input

options:
  -h, --help            show this help message and exit
  -b BOX [BOX ...], --box BOX [BOX ...]
                        to specify a crop box for each pre-cropped 2-up page image, either
                        as 1 side, 2 sides (L/R, T/B), or 4 sides (L, T, R, B)
  --all                 override the default of only producing 4 images (which for default
                        2-up gives 8 pages as 4 PNGs)
  -s SKIP, --skip SKIP  How many pages to skip forward from the original PDF
  -n N_UP, --n-up N_UP  How many pages to 'paste' alongside onto a single page (default: 2)
```

To run as a library using the [`pdf2up.conversion`](src/pdf2up/conversion.py) module:

- The `pdf2png()` function gives the same interface as the CLI can be obtained using the CLI
- The `ConvertPdf2Png` class gives access to values configured by this interface
