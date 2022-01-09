from __future__ import annotations

from argparse import ArgumentParser

import argcomplete

__all__ = ["Pdf2upParser"]


class Pdf2upParser(ArgumentParser):
    argument_signatures: list[tuple[str], dict] = [
        (["input_file"], {"metavar": "input"}),
        (
            ["-b", "--box"],
            {
                "type": int,
                "nargs": "+",
            },
        ),
        (["--all"], {"dest": "all_pages", "action": "store_true"}),
        (["-s", "--skip"], {"type": int}),
        (["-n", "--n-up"], {"type": int}),
        (["-c", "--cores"], {"type": int}),
    ]
    kwarg_names: list[str] = "input_file box all_pages skip".split()

    def __init__(self):
        super().__init__()
        for args, kwargs in self.argument_signatures:
            help_arg = sorted(args, key=hyphen_count)[-1]  # Kw/arg with most hyphens
            help_key = help_arg.lstrip("-").replace("-", "_")
            if help_key not in _HELP_MESSAGES:
                raise ValueError(f"Undocumented flag: '{help_arg}' has no help message")
            help_msg = _HELP_MESSAGES[help_key]
            kwargs.update({"help": help_msg})
            self.add_argument(*args, **kwargs)
        argcomplete.autocomplete(self)


_HELP_MESSAGES = {
    "all": (
        "override the default of only producing 4 images "
        "(which for default 2-up gives 8 pages as 4 PNGs)"
    ),
    "box": (
        "to specify a crop box for each pre-cropped 2-up page image, "
        "either as 1 side, 2 sides (L/R, T/B), or 4 sides (L, T, R, B)"
    ),
    "input_file": "",
    "n_up": "How many pages to 'paste' alongside onto a single page (default: 2)",
    "skip": "How many pages to skip forward from the original PDF",
    "cores": "Maximum CPU cores to run multicore execution (default: all available cores)",
}


def hyphen_count(flag) -> int:
    hyph_substr = flag[: flag.index(next(filter(str.isalnum, flag)))]
    return len(hyph_substr)
