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
from collections import defaultdict
from collections.abc import Iterable

from afvalwijzer.csv import laad_regels
from afvalwijzer.models import Adres, AfvalwijzerRegel, BuurtRegelset
from afvalwijzer.nummering import Adresreeksen
from afvalwijzer.pdf import Printer


def groepeer(regels: Iterable[AfvalwijzerRegel]
             ) -> dict[BuurtRegelset, list[Adres]]:
    """Groepeert alle adressen op buurt + regelset.

    :arg regels: Iterable van afvalwijzer regels. Een enkele afvalwijzer
    regel geeft informatie over de inzameling van een enkele afvalstroom
    op een enkel adres.
    :return: Alle adressen gegroepeerd per buurt + regelset. De regelset
    is de uitputtende set regels die gelden op een adres. Adressen met
    precies dezelfde regelset (en in dezelfde buurt) worden gegroepeerd.
    De return waarde is een dict van BuurtRegelset naar lijst van
    adressen.
    """
    # 1. Sorteer en groepeer alle regels op adres.
    adres_regelset = defaultdict(list)

    for regel in sorted(regels, key=lambda r: r.adres()):
        adres_regelset[regel.adres()].append(regel.regel())

    # 2. Zet de groepen om naar Regelset. Deze zijn hashable.
    # 3. Groepeer per buurt de adressen op regelset.
    buurt_regelset_adressen = defaultdict(list)

    for adres, regels in adres_regelset.items():
        regelset = tuple(sorted(regels))
        key = BuurtRegelset(adres.woonplaats, adres.buurt, regelset)
        buurt_regelset_adressen[key].append(adres)

    # # 4. Sorteer de regelset-groepen op buurt + eerste adres.
    # bra_items = sorted(buurt_regelset_adressen.items(),
    #                    key=lambda bra: (bra[0][:2], bra[1][0]))
    return dict(buurt_regelset_adressen)


def main(csv_file: str, pdf_file: str) -> None:
    """Leest de afvalwijzer CSV-export en zet dit om naar PDF.

    Voert de volgende stappen uit op de een lijst `AfvalwijzerRegel`s:

    1. Sorteer en groepeer alle regels op adres.
    2. Zet de groepen om naar Regelset. Deze zijn hashable.
    3. Groepeer per buurt de adressen op regelset.
    4. Sorteer de regelset-groepen op buurt + eerste adres.
    5. Vat adressen in reeksen.

    Houd er rekening mee dat een tussenliggend huisnummer in een andere buurt
    kan liggen.

    :arg csv_file: Het CSV-bestand met alle afvalwijzer regels
    (instructies). Elke regel (tekst) in het bestand beschrijft voor 1
    adres voor 1 afvalfractie hoe en wanneer dat aangeboden moet worden.
    :arg pdf_file: Het PDF-bestand om naartoe te schrijven.
    """
    pdf = Printer(font_cache_dir=os.path.split(pdf_file)[0])
    pdf.add_page()
    pdf.print_voorblad()
    pdf.add_page()

    regels = laad_regels(csv_file, strip=True)
    adres_reeks = Adresreeksen(r.adres() for r in regels)

    # 1. Sorteer en groepeer alle regels op adres.
    # 2. Zet de groepen om naar Regelset. Deze zijn hashable.
    # 3. Groepeer per buurt de adressen op regelset.
    # 4. Sorteer de regelset-groepen op buurt + eerste adres.
    buurt_regelset_adressen = groepeer(regels)

    # 5. Vat adressen in reeksen.
    laatste_buurt = BuurtRegelset(None, None, None)
    for buurt_regelset, adressen in buurt_regelset_adressen.items():
        if not (buurt_regelset.woonplaats == laatste_buurt.woonplaats and
                buurt_regelset.buurt == laatste_buurt.buurt):
            pdf.print_buurt(buurt_regelset)
            laatste_buurt = buurt_regelset

        adressen = adres_reeks(sorted(adressen))
        pdf.print_adressen(adressen)
        pdf.print_regelset(buurt_regelset.regelset)

    pdf.output(pdf_file)


if __name__ == '__main__':
    from config import afvalwijzer_csv_1k, afvalwijzer_csv_file

    afvalwijzer_csv = afvalwijzer_csv_1k        # For testing.
    # afvalwijzer_csv = afvalwijzer_csv_file      # For real.

    main(afvalwijzer_csv, 'output/afvalwijzer.pdf')
