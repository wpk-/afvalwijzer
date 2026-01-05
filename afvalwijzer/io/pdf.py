from collections.abc import Iterable, Iterator
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Literal

import pikepdf
from fpdf import FPDF, FPDF_VERSION, TextStyle
from fpdf.outline import TableOfContents, OutlineSection

from afvalwijzer.content import labels, samenvatting
from afvalwijzer.models import Adres, Brongegeven, Regel, Buurt

T_ORIENTATION = Literal["", "portrait", "p", "P", "landscape", "l", "L"]
T_FORMAT = Literal["", "a3", "A3", "a4", "A4", "a5", "A5", "letter", "Letter", "legal", "Legal"] | tuple[float, float]

PAGE_WIDTH = 210
MARGIN_LEFT = 31
MARGIN_RIGHT = 29
MARGIN_TOP = 10
MARGIN_BOTTOM = 27
CONTENT_WIDTH = PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT

FONT_FILE = 'C:/Windows/Fonts/corbel.ttf'
FONT_FILE_BOLD = 'C:/Windows/Fonts/corbelb.ttf'
FONT_FAMILY = 'Corbel'
LINE_HEIGHT = 0.45
FONT_SIZE_H1 = 21
FONT_SIZE_H2 = 13
FONT_SIZE_H3 = 11
FONT_SIZE_BASE = 10.5
FONT_SIZE_FOOTER = 10.5
FONT_SIZE_HEADER = 8.5
INDENT = 4

DEBUG_BOX = False


def read(file_in: str | Path, filters: dict[str, bool | int | str],
         ) -> Iterator[Brongegeven]:
    """Leest de Afvalwijzer data-export vanuit PowerBI (xlsx).
    """
    raise NotImplementedError(
        'PDF is een bestandsformaat voor opgemaakte tekst en niet voor ruwe'
        ' brongegevens.'
    )


def write(file_out: str | Path, data: Iterable[Brongegeven],
          filters: dict[str, bool | int | str]) -> None:
    """Schrijft de data in samengevatte, menselijk leesbare, vorm.

    `filters` zijn dezelfde filters als die zijn toegepast op `read()`, wat
    inzicht kan geven in welke records nu geschreven worden.
    """
    if 'woonfunctie' in filters:
        bewoners = 'bewoners' if filters['woonfunctie'] else 'bedrijven'
        if 'stadsdeel' in filters:
            titel = f'Afvalwijzer voor {bewoners} in stadsdeel {filters["stadsdeel"]}'
        else:
            titel = f'Afvalwijzer voor {bewoners}'
    elif 'stadsdeel' in filters:
        titel = f'Afvalwijzer voor stadsdeel {filters["stadsdeel"]}'
    else:
        titel = 'Afvalwijzer'

    printer = Printer(font_cache_dir=Path(file_out).parent)

    printer.set_title(titel)
    printer.print_voorblad()
    printer.print_voorwoord()
    printer.print_index()
    printer.print_data(data)

    printer.output(file_out)

    # Better metadata, see: https://py-pdf.github.io/fpdf2/Metadata.html
    with pikepdf.open(file_out, allow_overwriting_input=True) as pdf:
        with pdf.open_metadata(set_pikepdf_as_editor=False) as meta:
            meta["dc:title"] = titel
            meta["dc:language"] = "nl-NL"
            meta["dc:creator"] = ["Paul Koppen"]
            meta["dc:description"] = "Een naslagwerk van alle regels in de afvalwijzer."
            meta["pdf:Keywords"] = "Gemeente Amsterdam afvalwijzer regels aanbieden afval"
            meta["pdf:Producer"] = f"py-pdf/fpdf{FPDF_VERSION}"
            meta["xmp:CreatorTool"] = 'afvalwijzer.py'
            meta["xmp:CreateDate"] = datetime.now(tz=timezone.utc).isoformat()
        pdf.save()


def formatted_date(dt: date) -> str:
    maanden = ['januari', 'februari', 'maart', 'april', 'mei', 'juni', 'juli',
               'augustus', 'september', 'oktober', 'november', 'december']
    return f'{dt.day} {maanden[dt.month - 1]} {dt.year}'


class CustomTableOfContents(TableOfContents):
    def get_text_style(self, pdf: FPDF, item: OutlineSection) -> TextStyle:
        return (
            TextStyle(font_style='B', t_margin=5)
            if item.level < 1 else
            TextStyle(font_style='')
        )


class LevelCounter:
    def __init__(self) -> None:
        self.counts = (0,)

    def __str__(self) -> str:
        return '.'.join(map(str, self.counts[1:]))

    def inc(self, level: int = 1) -> str:
        if len(self.counts) > level:
            self.counts = self.counts[:level] + (self.counts[level] + 1,)
        else:
            self.counts = self.counts[:level] + (0,) * (level - len(self.counts)) + (1,)
        return str(self)


class Printer(FPDF):
    def __init__(self, orientation: T_ORIENTATION = 'P', unit: str = 'mm',
                 format: T_FORMAT = 'A4', *args, **kwargs) -> None:
        super().__init__(orientation, unit, format, *args, **kwargs)

        self.set_author('Gemeente Amsterdam')
        self.set_title('Afvalwijzer')
        self.datum = formatted_date(date.today())
        self.sectie_nummering = LevelCounter()

        self.set_margins(MARGIN_LEFT, MARGIN_TOP, MARGIN_RIGHT)
        self.set_auto_page_break(True, MARGIN_BOTTOM)
        self.add_font(FONT_FAMILY, style='', fname=FONT_FILE, uni=True)
        self.add_font(FONT_FAMILY, style='B', fname=FONT_FILE_BOLD, uni=True)
        self.set_line_width(0.25)

    def footer(self) -> None:
        """Print pagina footers.

        Dit gaat vanzelf. Je hoeft deze functie niet aan te roepen.
        """
        page = self.page_no()
        label = self.get_page_label()

        if page > 2:
            font_size = FONT_SIZE_FOOTER
            line_height = LINE_HEIGHT * font_size
            cw = CONTENT_WIDTH

            self.set_font(FONT_FAMILY, '', font_size)
            self.set_y(-line_height - 10)
            self.cell(cw, line_height, label, DEBUG_BOX, ln=1, align='R')

    def header(self) -> None:
        """Print pagina headers.

        Dit gaat vanzelf. Je hoeft deze functie niet aan te roepen.
        """
        page = self.page_no()
        font_size = FONT_SIZE_HEADER
        line_height = LINE_HEIGHT * font_size
        cw = CONTENT_WIDTH

        datum = self.datum

        col2_width = 30
        col1_width = cw - col2_width

        self.set_font(FONT_FAMILY, '', font_size)

        if page == 1:
            self.x += col1_width
            self.cell(col2_width, line_height, datum, DEBUG_BOX, ln=0)
            self.image('files/logo_gemeente_amsterdam.png', w=55.9, x=13)
            self.ln()
        else:
            self.cell(col1_width, line_height, self.author, DEBUG_BOX)
            self.cell(col2_width, line_height, datum, DEBUG_BOX, ln=1)
            self.cell(col1_width, line_height, 'Afval & Grondstoffen',
                      DEBUG_BOX, ln=1)
            self.cell(col1_width, line_height, '', DEBUG_BOX, ln=1)
            self.cell(col1_width, line_height, self.title, ln=1)
            self.y += 5 * line_height

    def print_data(self, data: Iterable[Brongegeven]) -> None:
        for buurt, buurt_data in samenvatting(data).items():
            self.print_hoofdstuk(buurt.buurtnaam, nummering=True)

            for fractie, fractie_data in buurt_data.items():
                self.print_sectie(fractie, nummering=True)

                if len(fractie_data) == 1:
                    regel = next(iter(fractie_data.keys()))
                    self.print_tekst(
                        f'U dient {fractie.lower()} als volgt aan te bieden:'
                    )
                    self.print_tekst()

                    for label, tekst in labels(regel):
                        self.print_label(label, tekst)

                else:
                    self.print_tekst(
                        f'In {buurt.buurtnaam} gelden op verschillende adressen'
                        f' verschillende regels voor het aanbieden van'
                        f' {fractie.lower()}. Hieronder staan de regels met daarbij'
                        f' vermeld voor welke adressen deze gelden.'
                    )

                    for i, (regel, adressen) in enumerate(fractie_data.items(), start=1):
                        self.print_subsectie(f'Optie {i}', nummering=True)
                        for label, tekst in labels(regel):
                            self.print_label(label, tekst)
                        self.print_tekst()
                        self.print_tekst('Deze regels gelden op de volgende adressen:')
                        self.print_tekst()
                        for adres in adressen:
                            self.print_item(adres)

            # Voor elk nieuw hoofdstuk.
            self.add_page()

    def print_hoofdstuk(self, titel: str, nummering: bool = False) -> None:
        """Print de titel van het hoofdstuk, optioneel met nummering.
        """
        cw = CONTENT_WIDTH
        font_size = FONT_SIZE_H1
        line_height = LINE_HEIGHT * font_size

        if nummering:
            titel = f'{self.sectie_nummering.inc(1)} {titel}'

        self.start_section(titel, level=0)
        self.set_font(FONT_FAMILY, style='B', size=font_size)
        self.cell(cw, h=10, text=titel, border=DEBUG_BOX, ln=1)
        self.y += line_height * 1.5

    def print_index(self, titel: str = 'Inhoud') -> None:
        toc = CustomTableOfContents(level_indent=0, line_spacing=1.35)
        # i, ii, iii, ...
        self.add_page(label_style="r",  label_start=1)
        self.print_hoofdstuk(titel)
        self.insert_toc_placeholder(toc.render_toc, allow_extra_pages=True)
        self.set_page_label(label_style="D",  label_start=1)

    def print_item(self, tekst: str) -> None:
        """Print een item in een ongenummerde lijst, met een * ervoor.
        """
        cw = CONTENT_WIDTH - INDENT
        font_size = FONT_SIZE_BASE
        line_height = LINE_HEIGHT * font_size

        # Zapfdingbats is a standard font that all PDF readers must render.
        # The character "n" in that font renders as a square box.
        # See also: https://py-pdf.github.io/fpdf2/Unicode.html
        self.set_font('Zapfdingbats', style='', size=font_size*0.6)
        self.cell(w=INDENT, h=line_height, text='n', border=DEBUG_BOX, ln=0)
        self.set_font(FONT_FAMILY, style='', size=font_size)
        self.multi_cell(w=cw, h=line_height, text=tekst, border=DEBUG_BOX, ln=1)

    def print_label(self, label: str, tekst: str) -> None:
        """Print een dikgedrukt label met ":" gevolgd door tekst.
        """
        cw = CONTENT_WIDTH - INDENT
        font_size = FONT_SIZE_BASE
        line_height = LINE_HEIGHT * font_size

        self.set_font(FONT_FAMILY, style='', size=font_size)
        # self.y += line_height // 2
        self.x += INDENT
        self.multi_cell(w=cw, h=line_height, text=f'**{label}:** {tekst}',
                        border=DEBUG_BOX, ln=1, markdown=True)

    def print_sectie(self, titel: str, level: int = 2, nummering: bool = False,
                     ) -> None:
        """Print de kop van een sectie, mogelijk met nummering.
        De sectie wordt toegevoegd aan de index.
        """
        cw = CONTENT_WIDTH
        font_size = {1: FONT_SIZE_H1, 2: FONT_SIZE_H2, 3: FONT_SIZE_H3}[level]
        line_height = LINE_HEIGHT * font_size

        if nummering:
            titel = f'{self.sectie_nummering.inc(level)} {titel}'

        if level < 3:
            # Exclude Optie 1, Optie 2, etc. from the table of contents.
            self.start_section(titel, level=level-1)
        self.set_font(FONT_FAMILY, style='B', size=font_size)
        self.y += line_height
        self.cell(cw, h=10, text=titel, border=DEBUG_BOX, ln=1)
        self.y += line_height // 2

    def print_subsectie(self, titel: str, nummering: bool = False) -> None:
        """Zie `print_sectie`.
        """
        self.print_sectie(titel, level=3, nummering=nummering)

    def print_tekst(self, tekst: str = '') -> None:
        """Print tekst over zoveel regels als nodig.
        """
        cw = CONTENT_WIDTH
        font_size = FONT_SIZE_BASE
        line_height = LINE_HEIGHT * font_size

        self.set_font(FONT_FAMILY, style='', size=font_size)
        self.multi_cell(w=cw, h=line_height, text=tekst, border=DEBUG_BOX, ln=1)

    def print_voorblad(self) -> None:
        font_size = FONT_SIZE_H1
        line_height = LINE_HEIGHT * font_size
        cw = CONTENT_WIDTH

        self.add_page()
        self.set_font(FONT_FAMILY, style='B', size=font_size)
        self.y += line_height
        if 'in stadsdeel' in self.title:
            ix = self.title.index('in stadsdeel')
            self.cell(cw, line_height, self.title[:ix+2], DEBUG_BOX, ln=1)
            self.cell(cw, line_height, self.title[ix+3:], DEBUG_BOX, ln=1)
        else:
            self.cell(cw, line_height, self.title, DEBUG_BOX, ln=1)

    def print_voorwoord(self) -> None:
        self.add_page()
        self.print_hoofdstuk('Voorwoord')
        self.print_tekst(
            'Gemeente Amsterdam heeft regels opgesteld voor het aanbieden van'
            ' afval. De regels die gelden zijn adres-gebonden. Dat betekent'
            ' dat zelfs binnen één straat voor verschillende huishoudens'
            ' verschillende regels kunnen gelden. Ook gelden er vaak'
            ' verschillende regels voor verschillende soorten afval. Zo kan'
            ' bijvoorbeeld papier op een andere dag ingezameld worden dan het'
            ' glas.'
        )
        self.print_tekst()
        self.print_tekst(
            'Dit document beschrijft voor alle adressen de geldende regels'
            ' voor het aanbieden van afval.'
        )
        self.print_tekst()
        self.print_tekst(
            'De indeling van het document is als volgt. Voor elke buurt is een'
            ' apart hoofdstuk, op alfabetische volgorde. Binnen het hoofdstuk'
            ' staan secties voor elke soort afval. Op die manier kunt u'
            ' eenvoudig de regels vinden die gelden op uw adres.'
        )
