"""
Een verzameling functies die inzicht geven in de waardes in het 1GB data
bestand.
"""
import csv
from operator import itemgetter
from typing import Iterable, Sequence, Callable

from afvalwijzer.models import AfvalwijzerRegel


def test_info(regels: Iterable[AfvalwijzerRegel], velden: Sequence[str]
              ) -> None:
    """Print alle unieke combinaties van waardes in velden.

    Loopt alle regels langs en verzamelt de set van veldwaardes. De set
    is hier de unieke set. Dus herhalingen worden niet meegenomen. Deze
    set wordt simpel geprint met de velden gescheiden door puntkomma's.

    Dit is bruikbaar om de samenhang tussen een selectie velden te
    onderzoeken. Zie hiervoor ook de overige test_info_*() functies.
    """
    indices = [AfvalwijzerRegel._fields.index(veld) for veld in velden]
    get_info = itemgetter(*indices)
    info = {*map(get_info, regels)}

    for x in sorted(info):
        print(';'.join(x))


def test_info_afvalkalender(regels: Iterable[AfvalwijzerRegel]) -> None:
    """Wat is de samenhang tussen de velden:
    - afvalwijzer_afvalkalender_melding
    - afvalwijzer_afvalkalender_opmerking

    Conclusie:
    De velden zijn nooit beiden tegelijk gevuld. Gebruik daarom
    `afvalwijzer_afvalkalender_melding or afvalwijzer_afvalkalender_opmerking`.
    """
    test_info(regels, ['afvalwijzer_afvalkalender_melding',
                       'afvalwijzer_afvalkalender_opmerking'])


def test_info_buitenzetten(regels: Iterable[AfvalwijzerRegel]) -> None:
    """Wat is de samenhang tussen de velden:
    - afvalwijzer_buitenzetten en
    - afvalwijzer_buitenzetten_vanaf_tot

    Conclusie:
    Deze velden zijn altijd gelijk. Gebruik afvalwijzer_buitenzetten.
    """
    test_info(regels, ['afvalwijzer_buitenzetten',
                       'afvalwijzer_buitenzetten_vanaf_tot'])


def test_info_fractie(regels: Iterable[AfvalwijzerRegel]) -> None:
    """Welke fracties zijn er?

    Conclusie:
        GFT;GFT
        Glas;Glas
        Grof;GA
        Grofvuil;GA
        Papier;Papier
        Plastic;Plastic
        Rest;Rest
        Restafval;Rest
        Textiel;Textiel
    """
    test_info(regels, ['afvalwijzer_fractie_naam', 'afvalwijzer_fractie_code'])


def test_info_frequentie(regels: Iterable[AfvalwijzerRegel]) -> None:
    """Wat staat er precies in het frequentie veld?

    Conclusie:
    Tekstuele beschrijving van welke week de regel geldt. Bijvoorbeeld om
    de 4 weken of 1e dinsdag van de maand.
    """
    test_info(regels, ['afvalwijzer_afvalkalender_frequentie',
                       'afvalwijzer_afvalkalender_frequentie'])


def test_info_instructies(regels: Iterable[AfvalwijzerRegel]) -> None:
    """Wat is de samenhang tussen de velden:
    - afvalwijzer_instructie,
    - afvalwijzer_instructie2,
    - afvalwijzer_waar, en
    - afvalwijzer_url

    Pieter: URL mag weg. Is niet nodig voor PDF en gaat telkens over
            verschillende velden. Datapunt verwerkt het veld instructie
            uit 21Q op basis van meer gegevens en levert instructie2. Die
            laatste moet dus gebruikt worden voor het printen van regels.
            Het veld waar geeft duiding waar de burger het afval aan
            dient te bieden.
    Conclusie: instructie en url negeren, instructie2 en waar gebruiken.
    """
    test_info(regels, ['afvalwijzer_instructie', 'afvalwijzer_instructie2',
                       'afvalwijzer_waar', 'afvalwijzer_url'])


def test_info_ophaaldagen(regels: Iterable[AfvalwijzerRegel]) -> None:
    """Wat is de samenhang tussen de velden:
    - afvalwijzer_ophaaldagen en
    - afvalwijzer_ophaaldagen2

    Conclusie:
    ophaaldagen2 is altijd een kopie van ophaaldagen, of het veld is leeg.
    Pieter: leeg is goed want dat is correctie op wat uit 21QUBZ komt.
    """
    test_info(regels, ['afvalwijzer_ophaaldagen', 'afvalwijzer_ophaaldagen2'])


def head(n: int, file_in: str, file_out: str) -> None:
    """Kopieert de eerste n regels uit bestand file_in naar file_out.
    Het data bestand is zo groot dat een kleinere versie fijn is.
    """
    with open(file_in) as f_in:
        with open(file_out, 'w') as f_out:
            f_out.writelines(l for (i, l) in zip(range(n), f_in))


def main(file_in: str, test_func: Callable[[Iterable[AfvalwijzerRegel]], None]
         ) -> None:
    with open(file_in, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=';', quotechar='"')
        assert tuple(next(reader)) == AfvalwijzerRegel._fields, 'File header'
        regels = (AfvalwijzerRegel(*line) for line in reader)
        test_func(regels)


if __name__ == '__main__':
    from config import afvalwijzer_csv_1k, afvalwijzer_csv_file

    if not afvalwijzer_csv_1k.is_file():
        head(10000, afvalwijzer_csv_file, afvalwijzer_csv_1k)

    main(afvalwijzer_csv_1k, test_info_fractie)
    # main(afvalwijzer_csv_1k, test_info_instructies)
    # main(afvalwijzer_csv_1k, test_info_ophaaldagen)
    # main(afvalwijzer_csv_1k, test_info_buitenzetten)
    # main(afvalwijzer_csv_1k, test_info_afvalkalender)
    # main(afvalwijzer_csv_1k, test_info_frequentie)
