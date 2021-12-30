from __future__ import annotations

from pathlib import Path
from subprocess import call

from more_itertools import ichunked
from pdf2image import convert_from_path
from pdfCropMargins import pdfCropMargins
from PIL import Image
from tqdm import tqdm

from .console_log import Console

logger = Console().logger


def pdf2png(
    input_file: str,
    box: int,
    all_pages: bool,
    skip: bool,
) -> list[Path]:
    if box:
        bsize = len(box)
        if bsize == 1:
            [l] = [t] = [r] = [b] = box
        elif bsize == 2:
            l, t = box
            r, b = l, t
        elif bsize == 4:
            l, t, r, b = box
        else:
            raise parser.error(
                f"Got {bsize} values for L,T,R,B crop box (expected 1, 2, or 4)"
            )

    input_pdf = Path(input_file).absolute()
    if not input_pdf.suffix == ".pdf":
        raise ValueError(f"'{input_pdf}' does not have a PDF suffix")
    crop_suffix = "_cropped"
    crop_pdf_dest = input_pdf.parent / f"{input_pdf.stem}{crop_suffix}.pdf"

    pcm_argv = ["-s", "-u", str(input_pdf), "-o", str(crop_pdf_dest)]
    exit_code, pcm_o, pcm_e = pdfCropMargins.crop(argv_list=pcm_argv, string_io=True)
    if exit_code:
        raise ValueError(f"pdfCropMargins failed: {pcm_o} -- {pcm_e}")

    pdf_pages = convert_from_path(crop_pdf_dest, dpi=300)
    if skip:
        pdf_pages = pdf_pages[skip:]
        if len(pdf_pages) < 1:
            raise ValueError(f"Invalid number of pages to skip ({len(pdf_pages)=})")
    if all_pages:
        # Technically not all since any odd last one out is skipped
        page_limit = len(pdf_pages) - (len(pdf_pages) % 2)
        max_i_len = len(str(page_limit))
    else:
        page_limit = 8
        max_i_len = 1
    i = 0
    pdf_pages_lim = pdf_pages[:page_limit]
    png_out_paths = []
    for page_pair in tqdm(ichunked(pdf_pages_lim, 2), total=len(pdf_pages_lim) // 2):
        iter_size = len(pdf_pages_lim[(i * 2) : (i + 1) * 2])
        if iter_size == 1:
            logger.info(f"Stopped ahead of iteration {i+1} to avoid unpaired page")
            continue
        p1, p2 = page_pair
        if not p1.height == p2.height:
            raise NotImplementedError("Images aren't same size, can't stack 2-up")
        combined_shape = (p1.width + p2.width, p1.height)
        two_up = Image.new("RGB", combined_shape)
        two_up.paste(p1, (0, 0))
        two_up.paste(p2, (p1.width, 0))
        if box:
            # Additional crop
            w, h = combined_shape
            two_up = two_up.crop((l, t, w - r, h - b))
        i_str = str(i).zfill(max_i_len)
        out_png = input_pdf.parent / f"{input_pdf.stem}_{i_str}.png"
        two_up.save(out_png)
        png_out_paths.append(out_png)
        i += 1
    return png_out_paths
