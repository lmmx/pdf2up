from pathlib import Path
from tqdm import tqdm
from sys import stderr
from argparse import ArgumentParser
from subprocess import call
from pdf2image import convert_from_path
from more_itertools import ichunked
from PIL import Image
import argcomplete


def main():
    parser = ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("-b", "--box", type=int, nargs="+")
    argcomplete.autocomplete(parser)

    pdf_crop_margins = "pdf-crop-margins"

    arg_l = parser.parse_args()
    box = arg_l.box
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

    input_pdf = Path(arg_l.input).absolute()
    if not input_pdf.suffix == ".pdf":
        raise ValueError(f"'{input_pdf}' does not have a PDF suffix")
    crop_suffix = "_cropped"
    crop_pdf_dest = input_pdf.parent / f"{input_pdf.stem}{crop_suffix}.pdf"

    call([pdf_crop_margins, "-s", "-u", str(input_pdf), "-o", str(crop_pdf_dest)])

    page_limit = 8
    pdf_pages = convert_from_path(crop_pdf_dest)
    i = 0
    pdf_pages_lim = pdf_pages[:page_limit]
    for page_pair in tqdm(ichunked(pdf_pages_lim, 2), total=len(pdf_pages_lim) // 2):
        iter_size = len(pdf_pages_lim[(i * 2) : (i + 1) * 2])
        if iter_size == 1:
            print(
                f"Stopped ahead of iteration {i+1} to avoid unpaired page", file=stderr
            )
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
        out_png = input_pdf.parent / f"{input_pdf.stem}_{i}.png"
        two_up.save(out_png)
        i += 1


if __name__ == "__main__":
    main()
