import csv

import bleach as bleach

from afvalwijzer.models import AfvalwijzerRegel


def laad_regels(filename: str, strip: bool = False) -> list[AfvalwijzerRegel]:
    """Leest de Afvalwijzer data dump (csv).

    Elke tekstregel in het bestand beschrijft een geldende regel
    gekoppeld aan een adres. Verschillende tekstregels kunnen meerdere
    regels op hetzelfde adres beschrijven.

    :arg filename: Pad naar en naam van het CSV-bestand met afval regels.
    :arg strip: Schoon de gegevens op door HTML-tags te verwijderen.
    Default is False.
    :return: Een lijst met afvalregels. Een regel geeft instructies voor
    het aanbieden van afval van een afvalfractie op een adres.
    """
    with open(filename, encoding='utf-8', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=';', quotechar='"')

        if tuple(next(reader)) != AfvalwijzerRegel._fields:
            raise ValueError('De CSV file header wordt niet herkend.')

        if not strip:
            return [AfvalwijzerRegel(*line) for line in reader]
        else:
            strip_tags = bleach.Cleaner([], {}, strip=True).clean
            regels = (AfvalwijzerRegel(*line) for line in reader)
            return [
                r._replace(
                    afvalwijzer_afvalkalender_melding=strip_tags(
                        r.afvalwijzer_afvalkalender_melding),
                    afvalwijzer_afvalkalender_opmerking=strip_tags(
                        r.afvalwijzer_afvalkalender_opmerking)
                )
                for r in regels
            ]
