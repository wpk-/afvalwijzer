from collections.abc import Iterable
from datetime import date
from typing import Union

from fpdf import FPDF

from afvalwijzer.models import Adres, Regel, Straat

PAGE_WIDTH = 210
MARGIN_LEFT = 31
MARGIN_RIGHT = 29
MARGIN_TOP = 10
MARGIN_BOTTOM = 27
CONTENT_WIDTH = PAGE_WIDTH - MARGIN_LEFT - MARGIN_RIGHT

FONT_FILE = 'C:/Windows/Fonts/corbel.ttf'
FONT_FILE_BOLD = 'C:/Windows/Fonts/corbelb.ttf'
LINE_HEIGHT = 0.45
FONT_SIZE_TITLE = 21
FONT_SIZE_BASE = 10.5
FONT_SIZE_FOOTER = 10.5
FONT_SIZE_HEADER = 8.5

DEBUG_BOX = False


def print_datum(dt: date) -> str:
    maanden = ['januari', 'februari', 'maart', 'april', 'mei', 'juni', 'juli',
               'augustus', 'september', 'oktober', 'november', 'december']
    return f'{dt.day} {maanden[dt.month - 1]} {dt.year}'


class Printer(FPDF):
    def __init__(self, orientation: str = 'P', unit: str = 'mm',
                 format: str = 'A4', *args, **kwargs) -> None:
        super().__init__(orientation, unit, format, *args, **kwargs)

        self.set_author('Gemeente Amsterdam')
        self.set_title('Afvalwijzer')
        self.datum = print_datum(date.today())

        self.set_margins(MARGIN_LEFT, MARGIN_TOP, MARGIN_RIGHT)
        self.set_auto_page_break(True, MARGIN_BOTTOM)
        self.add_font('Corbel', style='', fname=FONT_FILE, uni=True)
        self.add_font('Corbel', style='B', fname=FONT_FILE_BOLD, uni=True)
        self.set_line_width(0.25)

    def footer(self) -> None:
        """Print pagina footers.

        Dit gaat vanzelf. Je hoeft deze functie niet aan te roepen.
        """
        page = self.page_no()

        if page > 1:
            font_size = FONT_SIZE_FOOTER
            line_height = LINE_HEIGHT * font_size
            cw = CONTENT_WIDTH

            self.set_font('Corbel', '', font_size)
            self.set_y(-line_height - 10)
            self.cell(cw, line_height, str(page), DEBUG_BOX, ln=1, align='R')

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

        self.set_font('Corbel', '', font_size)

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

    def print_adressen(self, adressen: Iterable[str]) -> None:
        font_size = FONT_SIZE_BASE
        line_height = LINE_HEIGHT * font_size
        cw = CONTENT_WIDTH - 10

        self.set_font('Corbel', 'B', font_size)
        self.y += line_height // 2

        for adres in adressen:
            self.x += 5
            self.cell(5, line_height, '•', DEBUG_BOX, 0)
            self.multi_cell(cw, line_height, adres, DEBUG_BOX, ln=1)

        self.y += line_height // 2

    def print_buurt(self, buurt: Union[Adres, Regel, Straat]) -> None:
        font_size = FONT_SIZE_TITLE
        line_height = LINE_HEIGHT * font_size
        cw = CONTENT_WIDTH

        self.set_font('Corbel', 'B', font_size)
        self.y += line_height

        text = f'{buurt.woonplaats}, buurt {buurt.buurt}'
        self.cell(cw, 10, text, border=DEBUG_BOX or 'B', ln=1)

        self.y += line_height // 2

    def print_regelset(self, regelset: Iterable[Regel, ...]) -> None:
        font_size = FONT_SIZE_BASE
        line_height = LINE_HEIGHT * font_size
        cw = CONTENT_WIDTH - 50

        for regel in regelset:
            for i, (label, uitleg) in enumerate(regel.labels()):
                fractie = regel.fractie if i == 0 else ''
                self.cell(20, line_height, fractie, DEBUG_BOX)
                self.x += 2
                self.cell(26, line_height, label, DEBUG_BOX, align='R')
                self.x += 2
                self.multi_cell(cw, line_height, uitleg, DEBUG_BOX, ln=1)

    def print_voorblad(self) -> None:
        font_size = FONT_SIZE_TITLE
        line_height = LINE_HEIGHT * font_size
        cw = CONTENT_WIDTH

        self.set_font('Corbel', 'B', font_size)
        self.y += line_height
        self.cell(cw, line_height, self.title, DEBUG_BOX, ln=1)
