import csv
import logging
from collections import defaultdict
from pathlib import Path

from afvalwijzer.models import Adres, AfvalwijzerRegel, Regelset
from afvalwijzer.nummering import Adresreeksen

logger = logging.getLogger(__name__)


def laad_regels(filename: Path) -> tuple[dict[Regelset, list[Adres]],
                                         Adresreeksen]:
    """Leest de Afvalwijzer data dump (csv).

    Elke tekstregel in het bestand beschrijft een geldende regel
    gekoppeld aan een adres. Verschillende tekstregels kunnen meerdere
    regels op hetzelfde adres beschrijven.

    Deze functie leest de regels en sorteert en groepeert de data.

    :arg filename: Pad naar en naam van het CSV-bestand met afval regels.
    :return: Twee objecten: 1) een dict van regelset -> lijst van alle
    adressen waarvoor deze regelset geldt. 2) een Adresreeksen instantie
    te gebruiken om reeksen adressen netjes te nummeren.
    """
    adres_regels = defaultdict(set)

    # 1. Lees alle regels en groepeer op adres.
    with open(filename, encoding='utf-8', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')

        header = tuple(next(reader))

        if header != AfvalwijzerRegel._fields:
            logger.warning(header)
            logger.warning(AfvalwijzerRegel._fields)
            raise ValueError('De CSV file header wordt niet herkend.')

        for line in reader:
            try:
                awr = AfvalwijzerRegel(*line)
            except TypeError as err:
                logger.warning(line)
                raise err
            adres_regels[awr.adres()].add(awr.regel())

    # 2. Groepeer de adressen op regelset.
    regelset_adressen = defaultdict(list)

    for adres, regels in adres_regels.items():
        regelset = tuple(sorted(regels))
        regelset_adressen[regelset].append(adres)

    # 3. Sorteer de adressen per regelset-groep.
    for adressen in regelset_adressen.values():
        adressen.sort()

    # 4. Sorteer de groepen op adres (het eerste).
    regelset_adressen = dict(sorted(regelset_adressen.items(),
                                    key=lambda rs_aa: rs_aa[1][0]))

    return regelset_adressen, Adresreeksen(adres_regels.keys())
