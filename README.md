# pdf2up

A small utility to generate preview images of research papers (e.g. arXiv)
suitable for social media (e.g. Twitter)

## Installation

To install as a command line tool `pdf2up` run:

```sh
pip install pdf2up
```

## Usage

Run `pdf2up input.pdf`, optionally with the following flags:

- `-b`/`--box` to specify a crop box for each pre-cropped 2-up page image
  - 4 values: `-b 1 2 3 4` gets read as `left, top, right, bottom`
  - 2 values: `-b 1 2` gets repeated as `-b 1 2 1 2`
  - 1 value: `-b 1` = `-b 1 1 1 1`

- `--all` to override the default of 8 pages (4 images, each 2-up)
