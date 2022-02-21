from collections import defaultdict
from typing import Iterable, Dict, Tuple, List, Iterator

from afvalwijzer.models import Adres


class HuisnummerIndex:
    """Zet reeksen adressen om naar een overzichtelijke tekst.
    Bijvoorbeeld: "Silodam 1A--465B"

    Je instantieert de klasse met de uitputtende lijst van alle adressen.
    Vervolgens roep je parse() aan met een gedeeltelijke adreslijst. Deze
    geeft een iterator over (minder) adressen waarbij de
    huisnummertoevoeging waar mogelijk een reeks is. Aansluitend op het
    voorbeeld hierboven:
        straatnaam = "Silodam",
        huisnummer = 1,
        toevoeging = "A--465B".
    """
    def __init__(self, adressen: Iterable[Adres]) -> None:
        straat_key = self.straat_key
        nummer_key = self.nummer_key

        d = defaultdict(set)
        for adres in adressen:
            straat = straat_key(adres)
            nummer = nummer_key(adres)
            d[straat].add(nummer)
        self.reeksen: Dict[Tuple[str, str, str], List[Tuple[int, str]]] = {k: sorted(v) for k, v in d.items()}

    @staticmethod
    def nummer_key(a: Adres) -> Tuple[int, str]:
        """Geeft het tuple huisnummer, toevoeging.
        """
        return a.huisnummer, a.toevoeging

    @staticmethod
    def reeks_adres(start: Adres, eind: Adres) -> Adres:
        """Construeert een adres dat een reeks weergeeft.
        In het teruggegeven adres is de toevoeging aangepast om de reeks
        weer te geven. Dus bijvoorbeeld "A--465B".
        Als start en eind hetzelfde adres betreffen wordt start
        onveranderd teruggegeven.
        """
        if start == eind:
            return start
        toevoeging = f'{start.toevoeging}–{eind.huisnummer}{eind.toevoeging}'
        return start._replace(toevoeging=toevoeging)

    @staticmethod
    def straat_key(a: Adres) -> Tuple[str, str, str]:
        """Geeft het tuple woonplaats, buurt, straatnaam.
        """
        return a.woonplaats, a.buurt, a.straatnaam

    def parse(self, adressen: Iterable[Adres]) -> Iterator[Adres]:
        """Filtert een gesorteerde lijst adressen en combineert reeksen.

        Voorbeeld input:
            Emilie Knappertstraat 38
            Emilie Knappertstraat 46
            Esther de Boer-van Rijkstraat 5
            Esther de Boer-van Rijkstraat 6
            Esther de Boer-van Rijkstraat 7
            Esther de Boer-van Rijkstraat 17

        Voorbeeld output:
            Emilie Knappertstraat 38, 46
            Esther de Boer-van Rijkstraat 5–7, 17

        Waarom niet 38–46? Omdat er nog huisnummers tussen liggen. Die
        staan in de uitputtende adreslijst gegeven aan de constructor.
        Let op: hadden er geen huisnummers tussen 38 en 46 gelegen, dan
        was de output wel 38–46 geweest!
        """
        # `adressen` moet al gesorteerd zijn.
        straat_key = self.straat_key
        nummer_key = self.nummer_key
        reeksen = self.reeksen

        reeks_start = None
        reeks_eind = None
        start_straat = None
        nummer_reeks = None

        for adres in adressen:
            straat = straat_key(adres)
            nummer = nummer_key(adres)

            if straat == start_straat and nummer == next(nummer_reeks):
                reeks_eind = adres
            else:
                if reeks_start is not None:
                    yield self.reeks_adres(reeks_start, reeks_eind)
                reeks_eind = reeks_start = adres
                start_straat = straat
                pos = reeksen[straat].index(nummer)
                nummer_reeks = iter(reeksen[straat][pos + 1:])

        if reeks_start is not None:
            yield self.reeks_adres(reeks_start, reeks_eind)