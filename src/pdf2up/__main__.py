from __future__ import annotations

from pathlib import Path

from .cli import Pdf2upParser
from .conversion import pdf2png


def main() -> list[Path]:
    parser = Pdf2upParser()
    arg_l = parser.parse_args()
    config_dict = vars(arg_l)
    if config_dict["box"] is None:
        config_dict["box"] = [0,0,0,0]
    config_dict = {
        k: v for k, v in vars(arg_l).items()
        if (
            v is not None
            or k in ["skip"] # skip can be passed as None and is required
        )
    }
    pdf2png(**config_dict)
    return  # Don't return the new PNG Paths when called on command line


if __name__ == "__main__":
    main()
