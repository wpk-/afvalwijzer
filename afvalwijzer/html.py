from datetime import date
from html.parser import HTMLParser
from io import StringIO
from pathlib import Path
from typing import List, Iterator, Tuple, Union

from afvalwijzer.csv import AfvalwijzerCSV
from afvalwijzer.models import Adres, Regel, AdresRegels, BuurtRegels
from afvalwijzer.nummering import HuisnummerIndex


class AfvalwijzerHTML:
    """Verwerkt de AfvalwijzerCSV data tot een weergave in HTML.
    Gebruik bijvoorbeeld Chrome om de HTML te printen naar PDF.

    De weergave is er specifiek op gericht om geprint te kunnen worden.
    Het object nummering helpt om reeksen van huisnummers in dezelfde
    straat overzichtelijk te kunnen printen, zoals "Silodam 1A--465B".

    Adressen waarvoor dezelfde regels gelden worden gegroepeerd, per
    buurt. Het kan dus voorkomen dat op twee adressen exact dezelfde
    regels gelden maar dat ze toch apart afgedrukt worden. Dat is dan
    omdat ze in verschillende buurten liggen.

    De layout is ongeveer als volgt, waarbij de veldnamen verwijzen naar
    de kolommen uit de data dump (velden van AfvalwijzerRegel):

    Amsterdam (woonplaatsnaam), buurt F84c (gbd_buurt_code)
    --------------------------------------------
    Cycladenlaan (adres)
    Restafval (fractie_naam)
    Let op:        van 31-8-2021 (afvalkalender_van) tot 31-8-2022 (afvalkalender_tot)
                   Breng uw kerstboom naar het inzamelpunt in uw buurt. (afvalkalender_melding)
    Hoe:           In de container voor restafval (instructie2)
    Ophaaldag:     maandag, dinsdag, ... (ophaaldagen2), 1e dinsdag van de maand. (afvalkalender_frequentie)
    Buiten zetten: Woensdag vanaf 21.00 tot Donderdag 07.00 (buitenzetten)
    Waar:          Kaart met containers in de buurt (waar)
    Opmerking:     In Nieuw-West moet u uw tuinafval apart aanmelden.(afvalkalender_opmerking)
    """

    def __init__(self, afvalwijzer: AfvalwijzerCSV) -> None:
        self.afvalwijzer = afvalwijzer
        self.nummering = HuisnummerIndex(afvalwijzer.regels_op_adres.keys())

    @staticmethod
    def css() -> str:
        """Aanpassingen aan de CSS graag hier."""
        return '''
.buurt{display:grid;grid-template-columns:4rem 1fr;gap:0.5rem 1rem}
.buurt h1{border-bottom:black thin solid;grid-column:1/3;margin-bottom:.5rem}
.adressen{grid-column:1/3;margin:.5rem 0}
.fractie{}
label{text-align:right}
.regels{display:grid;grid-template-columns:6rem 1fr;gap:0 1rem}
        '''

    def adressen_html(self, adressen: List[Adres]) -> Iterator[str]:
        """Rendert een lijst met adressen, netjes genummerd.
        """
        yield '<ul class="adressen">'
        laatste_straat = None
        for a in self.nummering.parse(adressen):
            if a.straatnaam == laatste_straat:
                yield f', {a.huisnummer}{a.toevoeging}'
            else:
                laatste_straat = a.straatnaam
                yield f'<li>{a.straatnaam} {a.huisnummer}{a.toevoeging}'
        yield '</ul>'

    @staticmethod
    def regels_html(regelset: Tuple[Regel, ...]) -> Iterator[str]:
        """Rendert een verzameling regels.
        """
        def datum(s: str) -> str:
            """Haalt de datum uit de UTC string."""
            return f'{s[8:10]}-{s[5:7]}-{s[0:4]}'

        for r in regelset:
            yield (f'<div class="fractie">{r.fractie}</div>'
                   f'<div class="regels">')
            if r.melding:
                yield '<label>Let op:</label><div>'
                if r.melding_van:
                    yield (f'<div>Van {datum(r.melding_van)}'
                           f' tot {datum(r.melding_tot)}</div>')
                yield f'<div>{strip_tags(r.melding)}</div></div>'
            if r.instructie:
                yield f'<label>Hoe:</label><div>{r.instructie}</div>'
            if r.ophaaldagen:
                yield f'<label>Ophaaldag:</label><div>{r.ophaaldagen}'
                if r.frequentie:
                    yield f', {r.frequentie}'
                yield f'</div>'
            if r.buitenzetten:
                yield (f'<label>Buiten zetten:</label>'
                       f'<div>{r.buitenzetten}</div>')
            if r.waar:
                yield f'<label>Waar:</label><div>{r.waar}</div>'
            if r.opmerking:
                yield (f'<label>Opmerking:</label>'
                       f'<div>{strip_tags(r.opmerking)}</div>')
            yield '</div>'

    def adres_regels_html(self, adres_regels: AdresRegels) -> str:
        """Rendert de adressen en dan de regels. Zie AdresRegels.
        """
        return (''.join(self.adressen_html(adres_regels.adressen))
                + ''.join(self.regels_html(adres_regels.regels)))

    def buurt_regels_html(self, buurt_regels: BuurtRegels) -> str:
        """Rendert de buurt en alle AdresRegels die daaronder vallen.
        """
        buurt = buurt_regels.buurt
        regels = buurt_regels.regels
        return (f'<div class="buurt">'
                f'<h1>{buurt[0]}, buurt {buurt[1]}</h1>'
                f'{"".join(self.adres_regels_html(ar) for ar in regels)}'
                f'</div>')

    def write(self, filename: Union[Path, str]) -> None:
        """Schrijft het hele HTML-bestand.
        """
        buurt_regels_iter = self.afvalwijzer.buurt_regels()
        with open(filename, 'w') as f:
            f.write(f'<!doctype html>'
                    f'<html><head>'
                    f'<title>Afvalwijzer, {date.today().isoformat()}</title>'
                    f'<style type="text/css">{self.css()}</style>'
                    f'</head><body>')
            for br in buurt_regels_iter:
                f.write(self.buurt_regels_html(br))
            f.write(f'</body></html>')


class MLStripper(HTMLParser):
    """Klasse in markup language te strippen.
    """
    # https://stackoverflow.com/a/925630
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.text = StringIO()

    def handle_data(self, d):
        self.text.write(d)

    def get_data(self):
        return self.text.getvalue()


def strip_tags(html):
    """Verwijdert HTML-opmaak.
    """
    # https://stackoverflow.com/a/925630
    s = MLStripper()
    s.feed(html)
    return s.get_data()
