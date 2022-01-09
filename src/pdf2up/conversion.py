from __future__ import annotations
from dataclasses import dataclass

from pathlib import Path

from more_itertools import ichunked
from pdf2image import convert_from_path
from pdfCropMargins import pdfCropMargins
from PIL import Image
from tqdm import tqdm

from .console_log import Console

logger = Console().logger


def pdf2png(
    input_file: str,
    box: list[int],
    all_pages: bool,  # Technically not all, since any odd last one out is skipped
    skip: int | None,
    n_up: int = 3,
) -> list[Path]:
    p2p = ConvertPdf2Png(
        input_file=input_file,
        box=box,
        all_pages=all_pages,
        skip=skip,
        n_up=n_up,
    )
    p2p.crop_and_convert()
    return p2p.png_out_paths


@dataclass
class ConvertPdf2Png:
    input_file: str
    box: list[int]
    all_pages: bool  # Technically not all, since any odd last one out is skipped
    skip: int | None
    n_up: int = 2
    # The rest are not intended to be set in the CLI but can be used if called directly
    crop_suffix: str = "_cropped"
    imaging_dpi: int = 300
    default_n_pages: int = 4  # number of pages to paste `n_up` if `all_pages` is False

    def __post_init__(self):
        self.validate_pdf_suffix()
        self.validate_box_size()
        if self.all_pages:
            # round number of pages down to nearest `n_up` (default: 2)
            self.page_limit = len(self.pdf_pages) - (len(self.pdf_pages) % self.n_up)
        else:
            self.page_limit: int = self.n_up * self.default_n_pages
        self.max_i_len: int = len(str(self.page_limit))

    def crop_and_convert(self) -> None:
        self.crop()
        self.set_pdf_pages()
        paired_page_range = ichunked(self.pdf_pages_lim, self.n_up)
        for i, pp_islice in enumerate(tqdm(paired_page_range, total=self.pp_total)):
            self.process_page_pair(page_pair=tuple(pp_islice), pair_idx=i)
        return

    def crop(self) -> None:
        pcm_argv = ["-s", "-u", str(self.input_pdf), "-o", str(self.crop_pdf_dest)]
        exit_code, pcm_o, pcm_e = pdfCropMargins.crop(
            argv_list=pcm_argv, string_io=True
        )
        if exit_code:
            raise ValueError(f"pdfCropMargins failed: {pcm_o} -- {pcm_e}")
        return

    def set_pdf_pages(self) -> None:
        pages: list[Image] = convert_from_path(self.crop_pdf_dest, dpi=self.imaging_dpi)
        self._pdf_pages = pages[self.skip :]
        if len(self._pdf_pages) < 1:
            raise ValueError(f"Invalid # of pages to skip: {len(pages)=}, {self.skip=}")
        self.pdf_pages_lim = self.pdf_pages[: self.page_limit]
        self.pp_total = len(self.pdf_pages_lim) // self.n_up
        self.png_out_paths = list(map(self.png_path, range(self.pp_total)))
        return

    def process_page_pair(self, page_pair: tuple[Image, ...], pair_idx: int) -> None:
        p_start = pair_idx * self.n_up
        p_end = p_start + self.n_up
        iter_size = len(self.pdf_pages_lim[p_start:p_end])
        if iter_size < self.n_up:
            debug_msg = f"({iter_size=}, {self.n_up=})"
            logger.info(f"Stopped iteration early to avoid unpaired page {debug_msg}")
            breakpoint()
        else:
            if not (set(img.height for img in page_pair)):
                err_msg = f"Images are not same size, can't stack {self.n_up}-up"
                raise NotImplementedError(err_msg)
            p1, *p_rest = page_pair
            total_width = sum(p.width for p in page_pair)
            combined_shape = (total_width, p1.height)
            paste_up = Image.new("RGB", combined_shape)
            paste_up.paste(p1, (0, 0))
            prev_width = p1.width
            for p_n in p_rest:
                paste_up.paste(p_n, (prev_width, 0))
                prev_width += p1.width
            if self.box:
                # Additional crop
                l, t, r, b = self.box_dims_ltrb()
                w, h = combined_shape
                paste_up = paste_up.crop((l, t, w - r, h - b))
            out_png = self.png_path(pair_idx=pair_idx)
            paste_up.save(out_png)
        return

    def png_path(self, pair_idx: int) -> Path:
        return self.input_pdf.parent / self.png_filename(pair_idx=pair_idx)

    def png_filename(self, pair_idx: int) -> str:
        return f"{self.input_pdf.stem}_{str(pair_idx).zfill(self.max_i_len)}.png"

    @property
    def pdf_pages(self) -> list[...]:
        if not hasattr(self, "_pdf_pages"):
            err_msg = "pdf_pages not set: did you forget to call `crop_and_convert()`?"
            raise AttributeError(err_msg)
        return self._pdf_pages

    @property
    def input_pdf(self) -> Path:
        return Path(self.input_file).absolute()

    @property
    def crop_pdf_dest(self) -> Path:
        return self.input_pdf.parent / f"{self.input_pdf.stem}{self.crop_suffix}.pdf"

    def validate_box_size(self) -> None:
        if self.box is not None and not self.has_valid_box_size:
            raise ValueError(
                f"Got {len(self.box)} values for L,T,R,B crop box (expected 1, 2, or 4)"
            )

    def validate_pdf_suffix(self) -> None:
        if self.input_pdf.suffix != ".pdf":
            raise ValueError(f"'{self.input_pdf}' does not have a PDF suffix")

    @property
    def has_valid_box_size(self) -> bool:
        """:attr:`box` must be specified as 1, 2, or all 4 sides"""
        return len(self.box) in [1, 2, 4]

    def box_dims_ltrb(self) -> tuple[int, int, int, int]:
        bsize = len(self.box)
        assert self.has_valid_box_size, "INVALID BOX SIZE"  # Validated in __post_init__
        if bsize == 1:
            [l] = [t] = [r] = [b] = self.box
        elif bsize == 2:
            r, b = l, t = self.box
        elif bsize == 4:
            l, t, r, b = self.box
        return l, t, r, b
