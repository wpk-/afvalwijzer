import csv
from collections import defaultdict
from pathlib import Path
from typing import Dict, Set, Tuple, List, Union, Iterator

from afvalwijzer.models import Adres, Regel, AfvalwijzerRegel, BuurtRegels, \
    AdresRegels


class AfvalwijzerCSV:
    """Klasse voor het parsen van de Afvalwijzer data dump (csv).

    De aanpak voor het parsen is als volgt. Elke tekstregel in het
    bestand beschrijft een geldende regel gekoppeld aan een adres.
    Verschillende tekstregels kunnen meerdere regels op hetzelfde adres
    beschrijven. Zo bouwen we per adres de verzameling van alle regels
    die daar gelden.

    Vervolgens bekijken we, per buurt, op welke adressen precies dezelfde
    regels gelden. Voor de presentatie is het namelijk handig om niet 100
    keer dezelfde regels te herhalen, maar in plaats daarvan alle
    adressen bij elkaar te nemen en die set regels eenmalig af te
    drukken.

    Een regelset is een tuple (dat is handig, want tuples zijn hashable)
    en adressen_op_regelset somt alle adressen waarvoor precies al die
    regels van de set gelden.

    regels_op_adres slaat voor elk adres de set geldende regels op.
    adressen_op_regelset mapt sets geldende regels naar groepen adressen.
    """
    def __init__(self) -> None:
        self.regels_op_adres: Dict[Adres, Set[Regel]] = {}
        self.adressen_op_regelset: Dict[Tuple[Regel, ...], List[Adres]] = {}

    def parse(self, filename: Union[Path, str]) -> None:
        """Leest en verwerkt het csv bestand."""
        regels_op_adres = defaultdict(set)
        adressen_op_regelset = defaultdict(list)

        with open(filename, encoding='utf-8', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=';', quotechar='"')
            # Controleert de csv header.
            assert tuple(
                next(reader)) == AfvalwijzerRegel._fields, 'File header'
            afvalwijzer = (AfvalwijzerRegel(*line) for line in reader)

            for awr in afvalwijzer:
                regels_op_adres[awr.adres()].add(awr.regel())

        for adres, regels in regels_op_adres.items():
            regelset = tuple(sorted(regels))
            adressen_op_regelset[regelset].append(adres)

        for adressen in adressen_op_regelset.values():
            adressen.sort()

        # Sorteer de regels op adres. Binnen een buurt worden straten
        # gegroepeerd die dezelfde regels hebben. Vervolgens worden onder elke
        # groep de regels getoond. Het is dus handig om deze adresgroepen te
        # sorteren.
        adressen_op_regelset = {
            rs: aa
            for rs, aa in sorted(adressen_op_regelset.items(),
                                 key=lambda rs_aa: rs_aa[1][0])
        }

        self.regels_op_adres = dict(regels_op_adres)
        self.adressen_op_regelset = adressen_op_regelset

    def buurt_regels(self) -> Iterator[BuurtRegels]:
        """Maakt per buurt lijsten van paren adressen+regelset.

        :return: Een `BuurtRegels` iterator, gesorteerd op buurt. De info
            binnen elke `BuurtRegels` is gesorteerd op (elk eerste)
            adres.
        """
        buurt_regels = BuurtRegels(('', ''), [])

        for regelset, adressen in self.adressen_op_regelset.items():
            buurt = regelset[0].woonplaats, regelset[0].buurt
            adres_regels = AdresRegels(adressen, regelset)

            if buurt == buurt_regels.buurt:
                buurt_regels.regels.append(adres_regels)
            else:
                if len(buurt_regels.regels):
                    yield buurt_regels
                buurt_regels = BuurtRegels(buurt, [adres_regels])

        if len(buurt_regels.regels):
            yield buurt_regels