from datetime import date
from pathlib import Path
from typing import List, Tuple, Union, Iterable

from fpdf import FPDF

from afvalwijzer.csv import AfvalwijzerCSV
from afvalwijzer.models import AdresRegels, Adres, BuurtRegels, Regel
from afvalwijzer.html import strip_tags
from afvalwijzer.nummering import HuisnummerIndex


class AfvalwijzerPDF:
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
        self.pdf = PDF(titel=f'Afvalwijzer, {date.today().isoformat()}',
                       auteur='Gemeente Amsterdam')

    def print_adres_regels(self, adres_regels: AdresRegels) -> None:
        """Rendert de adressen en dan de regels. Zie AdresRegels.
        """
        self.print_adressen(adres_regels.adressen)
        self.print_regels(adres_regels.regels)

    def print_adressen(self, adressen: List[Adres]) -> None:
        """Rendert een lijst met adressen, netjes genummerd.
        """
        lijst = []
        adres = []
        laatste_straat = None

        for a in self.nummering.parse(adressen):
            if a.straatnaam == laatste_straat:
                adres.append(f'{a.huisnummer}{a.toevoeging}')
            else:
                if adres:
                    lijst.append(', '.join(adres))
                laatste_straat = a.straatnaam
                adres = [f'{a.straatnaam} {a.huisnummer}{a.toevoeging}']
        lijst.append(', '.join(adres))

        self.pdf.print_adreslijst(lijst)

    def print_buurt_regels(self, buurt_regels: BuurtRegels) -> None:
        """Rendert de buurt en alle AdresRegels die daaronder vallen.
        """
        buurt = buurt_regels.buurt
        regels = buurt_regels.regels

        self.pdf.print_buurt(f'{buurt[0]}, buurt {buurt[1]}')
        for adres_regels in buurt_regels.regels:
            self.print_adres_regels(adres_regels)

    def print_regels(self, regelset: Tuple[Regel, ...]) -> None:
        """Rendert een verzameling regels.
        """
        def datum(s: str) -> str:
            """Haalt de datum uit de UTC string."""
            return f'{s[8:10]}-{s[5:7]}-{s[0:4]}'

        for r in regelset:
            regels = []

            if r.melding:
                if r.melding_van:
                    regels.append(('Let op:', f'Van {datum(r.melding_van)}'
                                              f' tot {datum(r.melding_tot)}'))
                    regels.append(('', strip_tags(r.melding)))
                else:
                    regels.append(('Let op:', strip_tags(r.melding)))
            if r.instructie:
                regels.append(('Hoe:', r.instructie))
            if r.ophaaldagen:
                regels.append(('Ophaaldag:', r.ophaaldagen +
                               (f', {r.frequentie}' if r.frequentie else '')))
            if r.buitenzetten:
                regels.append(('Buiten zetten:', r.buitenzetten))
            if r.waar:
                regels.append(('Waar:', r.waar))
            if r.opmerking:
                regels.append(('Opmerking:', strip_tags(r.opmerking)))

            self.pdf.print_regels([(r.fractie if i == 0 else '', label, info)
                                   for i, (label, info) in enumerate(regels)])

    def write(self, filename: Union[Path, str]) -> None:
        """Schrijft het hele HTML-bestand.
        """
        self.pdf.add_page()
        for buurt_regels in self.afvalwijzer.buurt_regels():
            self.print_buurt_regels(buurt_regels)
        self.pdf.output(filename)


FONT_FILE = 'C:/Windows/Fonts/corbel.ttf'
FONT_FILE_BOLD = 'C:/Windows/Fonts/corbelb.ttf'
PAGE_WIDTH = 210
PAGE_MARGIN_LEFT = 31
PAGE_MARGIN_RIGHT = 29
PAGE_MARGIN_TOP = 10
PAGE_MARGIN_BOTTOM = 27
CONTENT_WIDTH = PAGE_WIDTH - PAGE_MARGIN_LEFT - PAGE_MARGIN_RIGHT
FONT_SIZE_BASE = 10.5
FONT_SIZE_HEADING = 21
FONT_SIZE_FOOTER = 10.5
FONT_SIZE_HEADER = 8.5
LINE_HEIGHT = 0.45
DEBUG_BOX = False


def datum_vandaag() -> str:
    maanden = ['januari', 'februari', 'maart', 'april', 'mei', 'juni', 'juli',
               'augustus', 'september', 'oktober', 'november', 'december']
    vandaag = date.today()
    return f'{vandaag.day} {maanden[vandaag.month]} {vandaag.year}'


DATUM = datum_vandaag()


class PDF(FPDF):
    def __init__(self, auteur: str = None, titel: str = None) -> None:
        super().__init__('P', 'mm', 'A4')

        if auteur:
            self.set_author(auteur)
        if titel:
            self.set_title(titel)

        self.add_font('Corbel', fname=FONT_FILE, uni=True)
        self.add_font('Corbel', fname=FONT_FILE_BOLD, style='B',
                      uni=True)

        self.set_margins(PAGE_MARGIN_LEFT, PAGE_MARGIN_TOP, PAGE_MARGIN_RIGHT)
        self.set_auto_page_break(True, PAGE_MARGIN_BOTTOM)
        self.set_line_width(0.25)

        self.add_page()
        line_height = self.prepare_font(FONT_SIZE_HEADING, 'B')
        self.y += line_height
        self.cell(CONTENT_WIDTH, line_height, 'Afvalwijzer', DEBUG_BOX, ln=1)

    def footer(self) -> None:
        if self.page_no() > 1:
            line_height = self.prepare_font(FONT_SIZE_FOOTER)
            self.set_y(-line_height - 10)
            self.cell(CONTENT_WIDTH, line_height, f'{self.page_no()}',
                      DEBUG_BOX, ln=1, align='R')

    def header(self) -> None:
        line_height = self.prepare_font(FONT_SIZE_HEADER)
        width_col_2 = 30
        width_col_1 = CONTENT_WIDTH - width_col_2

        if self.page_no() == 1:
            self.x += width_col_1
            self.cell(width_col_2, line_height, DATUM, DEBUG_BOX, ln=0)
            self.image('files/logo_gemeente_amsterdam.png', w=55.9, x=13)
            self.ln()
        else:
            self.cell(width_col_1, line_height, self.author, DEBUG_BOX)
            self.cell(width_col_2, line_height, DATUM, DEBUG_BOX, ln=1)
            self.cell(width_col_1, line_height, 'Afval & Grondstoffen',
                      DEBUG_BOX, ln=1)
            self.cell(width_col_1, line_height, '', DEBUG_BOX, ln=1)
            self.cell(width_col_1, line_height, 'Afvalwijzer', ln=1)
            self.y += 5 * line_height

    def prepare_font(self, font_size: float, font_style: str = '') -> int:
        # Actually returns a float but that makes the type checker go wild.
        self.set_font('Corbel', font_style, font_size)
        return font_size * LINE_HEIGHT

    def print_buurt(self, text: str) -> None:
        font_size = FONT_SIZE_HEADING
        line_height = self.prepare_font(font_size)
        self.y += line_height
        self.set_font('Corbel', 'B', font_size)
        self.cell(CONTENT_WIDTH, 10, text, border=DEBUG_BOX or 'B', ln=1)
        self.y += line_height // 2

    def print_adreslijst(self, items: Iterable[str]) -> None:
        line_height = self.prepare_font(FONT_SIZE_BASE)
        self.y += line_height // 2
        for item in items:
            self.x += 5
            self.cell(5, line_height, '•', DEBUG_BOX, 0)    # ●
            self.multi_cell(CONTENT_WIDTH - 10, line_height, item,
                            DEBUG_BOX, ln=1)
        self.y += line_height // 2

    def print_regels(self, triplets: Iterable[Tuple[str, str, str]]) -> None:
        line_height = self.prepare_font(FONT_SIZE_BASE)
        for fractie, label, uitleg in triplets:
            self.cell(20, line_height, fractie, DEBUG_BOX)
            self.x += 2
            self.cell(26, line_height, label, DEBUG_BOX, align='R')
            self.x += 2
            self.multi_cell(CONTENT_WIDTH - 50, line_height, uitleg,
                            DEBUG_BOX, ln=1)