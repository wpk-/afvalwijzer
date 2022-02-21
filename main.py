"""
@TODO: Gebruik FPDF om direct de PDF te genereren.
@DONE: HTML uit get .csv bestand opschonen. https://stackoverflow.com/a/46371211
@DONE: filter dubbele regels (bijv. Marathonweg 2). eigenlijk een datafount.
@DONE: opmerking van-tot filteren naar acceptabele datumweergave.
@DONE: datum in de titel.
@DONE: paginering en logo van Amsterdam. -- werkt niet. nog in css draft spec.
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
from afvalwijzer.csv import AfvalwijzerCSV
from afvalwijzer.html import AfvalwijzerHTML
from afvalwijzer.pdf import AfvalwijzerPDF


def main(file_in: str, file_out: str) -> None:
    """Parse het databestand en schrijf in overzichtelijke en menselijk
    leesbare vorm naar HTML. De gebruiker kan deze in bijvoorbeeld Chrome
    openen en printen naar PDF.
    """
    index = AfvalwijzerCSV()
    index.parse(file_in)
    html = AfvalwijzerHTML(index)
    html.write(file_out)
    pdf = AfvalwijzerPDF(index)
    pdf.write(file_out + '.pdf')


if __name__ == '__main__':
    from config import afvalwijzer_csv_1k

    # For testing.
    main(afvalwijzer_csv_1k, 'afvalwijzer.html')
    # For real.
    # main(afvalwijzer_csv_file, 'afvalwijzer.html')
