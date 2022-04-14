from collections import defaultdict
from collections.abc import Iterable, Iterator

from afvalwijzer.models import Adres, Huisnummer, Straat


def huisnummer(adres: Adres) -> Huisnummer:
    """Geeft het tuple huisnummer, toevoeging.
    """
    return Huisnummer(adres.huisnummer, adres.toevoeging)


def reeks(start: Adres, eind: Adres) -> Adres:
    """Maakt een adres dat een reeks weergeeft.

    :arg start: Begin van de reeks is een adres.
    :arg eind: Eind van de reeks is een adres.
    :return: Een nieuw adres waarin de huisnummertoevoeging wordt
    gebruikt om de reeks aan te geven. Dus bijvoorbeeld "A--465B".
    Als start en eind gelijk zijn wordt simpelweg start teruggegeven.
    """
    if start == eind:
        return start
    toevoeging = f'{start.toevoeging}–{eind.huisnummer}{eind.toevoeging}'
    return start._replace(toevoeging=toevoeging)


def straat(adres: Adres) -> Straat:
    """Geeft het tuple woonplaats, buurt, straatnaam.
    """
    return Straat(adres.woonplaats, adres.buurt, adres.straatnaam)


class Adresreeksen:
    """Zet reeksen adressen om naar een overzichtelijke tekst.
    Bijvoorbeeld: "Silodam 1A--465B"

    Je instantieert de klasse met de uitputtende lijst van alle adressen.
    Vervolgens roep je maak_reeksen() aan met een gedeeltelijke
    adreslijst. Deze geeft een gereduceerde lijst adressen waarbij de
    huisnummertoevoeging--waar mogelijk--een reeks is. Aansluitend op het
    voorbeeld hierboven:

        straatnaam = "Silodam",
        huisnummer = 1,
        toevoeging = "A--465B".
    """
    def __init__(self, adressen: Iterable[Adres]) -> None:
        d = defaultdict(set)
        for adres in adressen:
            d[straat(adres)].add(huisnummer(adres))

        self.reeksen: dict[Straat, list[Huisnummer]] = {
            k: sorted(v) for k, v in d.items()}

    def __call__(self, adressen: Iterable[Adres]) -> Iterator[str]:
        return self.pretty_print(adressen)

    def pretty_print(self, adressen: Iterable[Adres]) -> Iterator[str]:
        """Zet een lijst adressen om tot netjes genummerde adressen.

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
        Let op: Als er geen huisnummers tussen 38 en 46 gelegen hadden,
        dan was de output wel 38–46 geweest!

        :arg adressen: Lijst met enkele (niet reeksen) adressen. De lijst
        moet gesorteerd zijn.
        :return: Iterator over strings van netjes te printen adressen.
        Elke straatnaam komt een keer voor met alle huisnummers (en
        huisnummertoevoegingen) erachter netjes opgesomd.
        """
        reeksen = self.reeksen

        reeks_start = None
        reeks_eind = None
        start_straat = None
        nummer_reeks = None

        straat_nummers = defaultdict(list)

        for adres in adressen:
            st = straat(adres)
            nr = huisnummer(adres)

            if st == start_straat and nr == next(nummer_reeks):
                reeks_eind = adres
            else:
                if reeks_start is not None:
                    a = reeks(reeks_start, reeks_eind)
                    straat_nummers[a.straatnaam].append(
                        f'{a.huisnummer}{a.toevoeging}')
                reeks_eind = reeks_start = adres
                start_straat = st
                pos = reeksen[st].index(nr)
                nummer_reeks = iter(reeksen[st][pos + 1:])

        if reeks_start is not None:
            a = reeks(reeks_start, reeks_eind)
            straat_nummers[a.straatnaam].append(
                f'{a.huisnummer}{a.toevoeging}')

        return (f'{st} {", ".join(nrs)}' for st, nrs in straat_nummers.items())
