from pathlib import Path
from imageio import imread, imwrite
from argparse import ArgumentParser
from subprocess import call

parser = ArgumentParser()
parser.add_argument("input")

pdf_crop_margins = "pdf-crop-margins"

arg_l = parser.parse_args()

input_pdf = Path(arg_l.input).absolute()
if not input_pdf.suffix == ".pdf":
    raise ValueError(f"'{input_pdf}' does not have a PDF suffix")
crop_suffix = "_cropped"
crop_pdf_dest = input_pdf.parent / f"{input_pdf.stem}{crop_suffix}.pdf"

call([
    pdf_crop_margins,
    "-s",
    "-u",
    str(input_pdf),
    "-o",
    str(crop_pdf_dest)
    ]
)
