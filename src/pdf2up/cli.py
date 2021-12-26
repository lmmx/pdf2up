from __future__ import annotations

from argparse import ArgumentParser

import argcomplete


class Pdf2upParser(ArgumentParser):
    argument_signatures: list[tuple[str], dict] = [
        (["input_file"], {"metavar": "input"}),
        (["-b", "--box"], {"type": int, "nargs": "+"}),
        (["--all"], {"dest": "all_pages", "action": "store_true"}),
        (["-s", "--skip"], {"type": int}),
    ]
    kwarg_names: list[str] = "input_file box all_pages skip".split()

    def __init__(self):
        super().__init__()
        for args, kwargs in self.argument_signatures:
            self.add_argument(*args, **kwargs)
        argcomplete.autocomplete(self)
