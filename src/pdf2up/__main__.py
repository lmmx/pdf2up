from __future__ import annotations

from pathlib import Path

from .cli import Pdf2upParser
from .conversion import pdf2png


def main() -> list[Path]:
    parser = Pdf2upParser()
    arg_l = parser.parse_args()
    pdf2png(**vars(arg_l))
    return  # Don't return the new PNG Paths when called on command line


if __name__ == "__main__":
    main()
