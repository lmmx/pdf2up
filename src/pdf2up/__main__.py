from .cli import Pdf2upParser
from .conversion import pdf2png

def main():
    parser = Pdf2upParser()
    arg_l = parser.parse_args()
    pdf2png(**{k: arg_l.__dict__[k] for k in "box input_file all_pages skip".split()})


if __name__ == "__main__":
    main()
