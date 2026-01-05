from collections import defaultdict, Counter
from collections.abc import Iterable
from itertools import groupby
from operator import attrgetter
from typing import TypeVar

import bleach

from .models import Adres, Brongegeven, Regel, Buurt

T = TypeVar('T')


# Nodig om melding en opmerking op te schonen in `Regel.labels()`.
strip_tags = bleach.Cleaner([], {}, strip=True).clean


def labels(self: Regel) -> list[tuple[str, str]]:
    """
    Onderdeel van een rapport.
    Hierin worden per adresgroep links labels en rechts waardes geprint.
    """
    def datum(s: str) -> str:
        """Haalt de datum uit de UTC-string."""
        return f'{s[8:10]}-{s[5:7]}-{s[0:4]}'

    arr = []

    if self.instructie:
        arr.append(('Hoe', self.instructie))
    if self.ophaaldagen:
        arr.append(('Ophaaldag', self.ophaaldagen +
                    (f', {self.frequentie}' if self.frequentie else '')))
    if self.buitenzetten:
        arr.append(('Buiten zetten', self.buitenzetten))
    if self.waar:
        arr.append(('Waar', self.waar))
    if self.opmerking:
        arr.append(('Opmerking', strip_tags(self.opmerking)))

    if self.melding:
        if self.melding_van:
            arr.append(('Let op', f'Van {datum(self.melding_van)}'
                                   f' tot {datum(self.melding_tot)}'
                                   f' {strip_tags(self.melding)}'))
        else:
            arr.append(('Let op', self.melding))

    return arr


def samengevoegde_huisnummers(adressen_per_regel: dict[Regel, list[Adres]],
                              ) -> dict[Regel, list[str]]:
    if len(adressen_per_regel) == 1:
        regel = next(iter(adressen_per_regel.keys()))
        return {regel: []}  # Voor alle adressen geldt 1 en dezelfde regel.
        # Afspraak: [] = "alle adressen".

    # Test status van adressen: voor de hele straat 1 regel?
    #
    # (Het is een beetje onhandig dat we op deze manier alle adressen langs
    #  moeten lopen, maar het zorgt er wel voor dat we bovenstaande test snel
    #  uit kunnen voeren.)

    regels_per_straat = defaultdict(Counter)

    for regel, adressen in adressen_per_regel.items():
        for adres in adressen:
            regels_per_straat[adres.straatnaam][regel] += 1

    hele_straat = {
        straat: len(regels) == 1 and regels.total() > 5
        for straat, regels in regels_per_straat.items()
    }

    # Nu we weten welke straten precies 1 regel hebben (en dus het huisnummer
    # niet belangrijk is) kunnen we alle huisnummers gaan samenvoegen.
    # - Waar huisnummers wel relevant zijn vatten we deze samen met een
    #   komma-gescheiden opsomming.
    # - Waar huisnummers niet relevant zijn schrijven we "alle huisnummers".

    def sortkey(ra: tuple[Regel, list[Adres]]) -> int:
        return -len(ra[1])

    def alle_huisnummers(straat: str) -> str:
        return f'{straat}, alle huisnummers'

    def gescheiden_huisnummers(straat: str, adressen: Iterable[Adres],
                               sep: str = ', ') -> str:
        huisnummers = sep.join(f'{a.huisnummer}{a.toevoeging}' for a in adressen)
        return f'{straat} {huisnummers}'

    get_straatnaam = attrgetter('straatnaam')

    return {
        regel: [
            alle_huisnummers(straat)
            if hele_straat[straat] else
            gescheiden_huisnummers(straat, straat_adressen)
            for straat, straat_adressen in groupby(adressen, get_straatnaam)
        ]
        for regel, adressen in sorted(adressen_per_regel.items(), key=sortkey)
    }


def samenvatting(data: Iterable[Brongegeven],
                 ) -> dict[Buurt, dict[str, dict[Regel, list[str]]]]:
    def sortkey(r: Brongegeven) -> tuple[str, ...]:
        return tuple(
            v or ''
            for v in (
                # Sorteer 23-H (huis) voor 23-1.
                r._replace(huisnummertoevoeging=
                           r.huisnummertoevoeging.replace('H', ' '))
                if r.huisnummertoevoeging else r
            )
        )

    get_buurt = attrgetter('buurt')
    get_fractie = attrgetter('afvalfractie')
    get_regel = attrgetter('regel')

    data = sorted(data, key=sortkey)

    return {
        buurt: {
            fractie: samengevoegde_huisnummers({
                regel: [item.adres for item in regel_data]
                for regel, regel_data in groupby(fractie_data, get_regel)
            })
            for fractie, fractie_data in groupby(buurt_data, get_fractie)
        }
        for buurt, buurt_data in groupby(data, get_buurt)
    }
