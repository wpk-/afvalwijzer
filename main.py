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
import os.path

from afvalwijzer.csv import laad_regels
from afvalwijzer.pdf import Printer


def main(csv_file: str, pdf_file: str) -> None:
    """Leest de afvalwijzer CSV-export en zet dit om naar PDF.

    :arg csv_file: Het CSV-bestand met alle afvalwijzer regels.
    :arg pdf_file: Het PDF-bestand om naartoe te schrijven.
    """
    pdf = Printer(font_cache_dir=os.path.split(pdf_file)[0])
    pdf.add_page()
    pdf.print_voorblad()
    pdf.add_page()

    regels, adres_reeksen = laad_regels(csv_file)

    laatste_buurt = (None, None)
    for regelset, adressen in regels.items():
        if regelset[0][:2] != laatste_buurt:
            pdf.print_buurt(regelset[0])
            laatste_buurt = regelset[0][:2]

        adressen = adres_reeksen(adressen)
        pdf.print_adressen(adressen)
        pdf.print_regelset(regelset)

    pdf.output(pdf_file)


if __name__ == '__main__':
    from config import afvalwijzer_csv_1k, afvalwijzer_csv_file

    from time import time
    t0 = time()

    afvalwijzer_csv = afvalwijzer_csv_1k        # Test
    # afvalwijzer_csv = afvalwijzer_csv_file      # Live

    main(afvalwijzer_csv, 'output/afvalwijzer.pdf')

    print(f'Klaar in {time()-t0:.2f} sec.')
