from __future__ import annotations

from pathlib import Path

from .cli import Pdf2upParser
from .conversion import pdf2png


def main() -> list[Path]:
    parser = Pdf2upParser()
    arg_l = parser.parse_args()
    pngs = pdf2png(**{k: arg_l.__dict__[k] for k in parser.kwarg_names})
    return # Don't return the new PNG Paths when called on command line

if __name__ == "__main__":
    main()
