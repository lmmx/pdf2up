from __future__ import annotations

import logging

__all__ = ["Console"]


class Console(logging.Logger):
    def __init__(self, name=None, level=logging.INFO, timestamped=False):
        self.logger = logging.getLogger(name=name)
        self.console = logging.StreamHandler()
        for target in (self.logger, self.console):
            target.setLevel(level)
        self.timestamped = timestamped
        self.console.setFormatter(self.log_format)
        self.logger.addHandler(self.console)

    @property
    def header_names(self) -> list[str]:
        """The log format header/s (with/without timestamp)."""
        return [*filter(lambda t: self.timestamped, ["asctime"]), "levelname"]

    @property
    def log_format(self) -> logging.Formatter:
        header_str = " ".join(map("[%({})s]".format, self.header_names))
        return logging.Formatter(fmt=header_str + "- %(message)s")


if __name__ == "__main__":
    logger = Console().logger

    logger.debug("Debug messages only go to STDERR if level <= `logging.DEBUG`")
    logger.info("So should info messages")
    logger.warning("and this warning (shown on STDERR)")
    logger.error("Also errors go both to file and to STDERR too")
