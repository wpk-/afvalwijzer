"""
@DONE: Gebruik FPDF om direct de PDF te genereren.
@DONE: HTML uit get .csv bestand opschonen. https://stackoverflow.com/a/46371211
@DONE: filter dubbele regels (bijv. Marathonweg 2). eigenlijk een datafount.
@DONE: opmerking van-tot filteren naar acceptabele datumweergave.
@DONE: datum in de titel.
@DONE: paginering en logo van Amsterdam.
@DONE: reeksen huisnummers. als er geen adres tussen ligt, dan van-tot.
@DONE: UTF-8.


Opmaak:

    # Amsterdam (woonplaatsnaam), buurt F84c (gbd_buurt_code)
    # --------------------------------------------
    # Cycladenlaan (adres)
    # Restafval (fractie_naam)
    # Let op:        van 31-8-2021 (afvalkalender_van) tot 31-8-2022 (afvalkalender_tot)
    #                Breng uw kerstboom naar het inzamelpunt in uw buurt. (afvalkalender_melding)
    # Hoe:           In de container voor restafval (instructie2)
    # Ophaaldag:     maandag, dinsdag, ... (ophaaldagen2), 1e dinsdag van de maand. (afvalkalender_frequentie)
    # Buiten zetten: Woensdag vanaf 21.00 tot Donderdag 07.00 (buitenzetten)
    # Waar:          Kaart met containers in de buurt (waar)
    # Opmerking:     In Nieuw-West moet u uw tuinafval apart aanmelden.(afvalkalender_opmerking)


Daardoor zijn een aantal velden niet nodig:
- afvalkalender_frequentie (is al opgenomen in de instructie)
- routetype_naam (zegt iets over de route, niet over afval aanbieden)
- basisroutetype (zegt iets over de route, niet over afval aanbieden)
- instructie (is leeg of bevat exact dezelfde tekst als afvalwijzer_waar)
- afvalwijzer_ophaaldagen (is soms verkeerd, dan is ophaaldagen2 correct)
- afvalwijzer_buitenzetten_vanaf_tot (is identiek aan afvalwijzer_buitenzetten)

"""
from logging import getLogger, INFO, WARNING
from pathlib import Path

from afvalwijzer import maak_pdf

getLogger('fontTools').setLevel(WARNING)
getLogger('fpdf').setLevel(INFO)
getLogger('PIL').setLevel(INFO)

logger = getLogger(__name__)


if __name__ == '__main__':
    import argparse
    import logging
    from time import time
    
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        description='Maak een schone afvalwijzer pdf.')

    parser.add_argument('csv_file', metavar='IN',
                        help='CSV-bestand met alle regels van de afvalwijzer.')
    parser.add_argument('pdf_file', metavar='OUT', nargs='?',
                        help='PDF-bestand om naartoe te schrijven.')

    args = parser.parse_args()

    csv_file = Path(args.csv_file)
    pdf_file = Path(args.pdf_file or f'output/{csv_file.stem}.pdf')

    t0 = time()

    maak_pdf(csv_file, pdf_file)
    print(f'Klaar in {time()-t0:.2f} sec.')
