from pathlib import Path
from typing import Union

from afvalwijzer.csv import laad_regels
from afvalwijzer.pdf import Printer


def maak_pdf(csv_file: Union[str, Path], pdf_file: Union[str, Path]) -> None:
    """Leest de afvalwijzer CSV-export en zet dit om naar PDF.

    :arg csv_file: Het CSV-bestand met alle afvalwijzer regels.
    :arg pdf_file: Het PDF-bestand om naartoe te schrijven.
    """
    printer = Printer(font_cache_dir=Path(pdf_file).parent)
    printer.add_page()
    printer.print_voorblad()
    printer.add_page()

    regels, adres_reeksen = laad_regels(csv_file)

    laatste_buurt = (None, None)
    for regelset, adressen in regels.items():
        if regelset[0][:2] != laatste_buurt:
            printer.print_buurt(regelset[0])
            laatste_buurt = regelset[0][:2]

        adressen = adres_reeksen(adressen)
        printer.print_adressen(adressen)
        printer.print_regelset(regelset)

    printer.output(pdf_file)
