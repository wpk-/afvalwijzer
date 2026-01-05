from collections import defaultdict
from collections.abc import Iterable
from datetime import date
from io import StringIO
from itertools import count
from pathlib import Path
from typing import Literal
from zipfile import ZipFile, ZIP_DEFLATED

from afvalwijzer.content import labels, samenvatting
from afvalwijzer.models import Brongegeven

TEMPLATE_DOCX = 'files/afvalwijzer-template.docx'


def read(file_in: str | Path, filters: dict[str, bool | int | str],
         ) -> Iterable[Brongegeven]:
    raise NotImplementedError('DOCX is geen bestandsformaat voor ruwe data.')


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

    with ZipFile(TEMPLATE_DOCX) as tpl:
        with ZipFile(file_out, 'w', ZIP_DEFLATED, compresslevel=9) as doc:
            doc.comment = tpl.comment
            for item in tpl.infolist():
                if item.filename == 'word/document.xml':
                    doc.writestr(item, document_xml(data, titel))
                elif item.filename in ('word/header1.xml', 'word/header2.xml',
                                       'docProps/core.xml', 'customXml/item1.xml'):
                    text = tpl.read(item.filename)
                    text = replace_dates(text)
                    text = replace_text(text, '{Titel}', titel)
                    doc.writestr(item, text)
                else:
                    doc.writestr(item, tpl.read(item.filename))


def replace_dates(content: bytes, encoding: str = 'utf-8') -> bytes:
    def formats(dt: date) -> tuple[str, str, str]:
        iso = dt.isoformat()
        kort = iso.replace('-', '')
        lang = f'{dt.day} {maand[dt.month]} {dt.year}'
        return iso, kort, lang

    maand = ['', 'januari', 'februari', 'maart', 'april', 'mei', 'juni', 'juli',
             'augustus', 'september', 'oktober', 'november', 'december']

    toen = date(2025, 2, 3)
    vandaag = date.today()

    for t, v in zip(formats(toen), formats(vandaag)):
        content = content.replace(t.encode(encoding), v.encode(encoding))

    return content


def replace_text(content: bytes, old: str, new: str, *,
                 encoding: str = 'utf-8') -> bytes:
    return content.replace(old.encode(encoding), new.encode(encoding))


def document_xml(data: Iterable[Brongegeven], title: str) -> str:
    xml = DocumentXML()

    buf_a = StringIO()
    buf_a.write(xml.document_start())
    buf_a.write(xml.cover_page(title))
    buf_a.write(xml.title('Voorwoord'))
    buf_a.write(xml.text())
    buf_a.write(xml.text(
        'Gemeente Amsterdam heeft regels opgesteld voor het aanbieden van afval.'
        ' Deze regels zijn adres-gebonden. Dat betekent dat binnen één straat'
        ' voor verschillende huishoudens verschillende regels kunnen gelden.'
        ' Ook gelden vaak verschillende regels voor verschillende soorten'
        ' afval. Zo kan papier bijvoorbeeld op een andere dag ingezameld worden'
        ' dan het glas.'))
    buf_a.write(xml.text())
    buf_a.write(xml.text(
        'Dit document beschrijft voor alle adressen de geldende regels voor het'
        ' aanbieden van afval.'))
    buf_a.write(xml.text())
    buf_a.write(xml.text(
        'De indeling van het document is als volgt. Voor elke buurt is een'
        ' apart hoofdstuk, op alfabetische volgorde. Binnen het hoofdstuk'
        ' staan secties voor elke soort afval. Op die manier kunt u'
        ' eenvoudig de regels vinden die gelden op uw adres.'))
    # buf_a.write(xml.title('Inhoud'))

    buf_b = StringIO()
    buf_b.write(xml.page_layout(1))

    for buurt, buurt_data in samenvatting(data).items():
        buf_b.write(xml.section(1, buurt.buurtnaam))

        for fractie, fractie_data in buurt_data.items():
            buf_b.write(xml.section(2, fractie))

            if len(fractie_data) == 1:
                regel = next(iter(fractie_data.keys()))
                buf_b.write(xml.text(
                    f'U dient {fractie.lower()} als volgt aan te bieden:'))
                buf_b.write(xml.text())
                for caption, text in labels(regel):
                    buf_b.write(xml.label_item(caption, text))

            else:
                buf_b.write(xml.text(
                    f'In {buurt.buurtnaam} gelden op verschillende adressen'
                    f' verschillende regels voor het aanbieden van'
                    f' {fractie.lower()}. Hieronder staan de regels met daarbij'
                    f' vermeld voor welke adressen deze gelden.'))

                for i, (regel, adressen) in enumerate(fractie_data.items(), start=1):
                    buf_b.write(xml.section(3, f'Optie {i}'))
                    for caption, text in labels(regel):
                        buf_b.write(xml.label_item(caption, text))
                    buf_b.write(xml.text())
                    buf_b.write(xml.text('Deze regels gelden op de volgende adressen:'))
                    buf_b.write(xml.text())
                    for adres in adressen:
                        buf_b.write(xml.list_item(adres))

        buf_b.write(xml.page_break())

    buf_b.write(xml.page_layout(2))
    buf_b.write(xml.document_end())

    return (
        buf_a.getvalue() +
        # xml.index(maxlevel=2) +
        buf_b.getvalue()
    )


class DocumentXML:
    def __init__(self) -> None:
        self.w_id = count()
        self.level_counter = defaultdict(int)
        self.section_titles = []

    def cover_page(self, title: str, subtitle: str = '') -> str:
        title = title.replace('in stadsdeel', 'in          stadsdeel')
        return f'''
      <w:tbl>
         <w:tblPr>
            <w:tblStyle w:val="Tabelraster" />
            <w:tblpPr w:leftFromText="142" w:rightFromText="142" w:vertAnchor="page" w:tblpY="3857" />
            <w:tblOverlap w:val="never" />
            <w:tblW w:w="7258" w:type="dxa" />
            <w:tblBorders>
               <w:top w:val="nil" />
               <w:left w:val="nil" />
               <w:bottom w:val="nil" />
               <w:right w:val="nil" />
               <w:insideH w:val="nil" />
               <w:insideV w:val="nil" />
            </w:tblBorders>
            <w:tblLayout w:type="fixed" />
            <w:tblCellMar>
               <w:left w:w="0" w:type="dxa" />
               <w:right w:w="0" w:type="dxa" />
            </w:tblCellMar>
            <w:tblLook w:val="04A0" w:firstRow="1" w:lastRow="0" w:firstColumn="1" w:lastColumn="0" w:noHBand="0" w:noVBand="1" />
         </w:tblPr>
         <w:tblGrid>
            <w:gridCol w:w="7258" />
         </w:tblGrid>
         <w:tr>
            <w:trPr>
               <w:trHeight w:hRule="exact" w:val="2722" />
            </w:trPr>
            <w:tc>
               <w:tcPr>
                  <w:tcW w:w="7258" w:type="dxa" />
               </w:tcPr>
               <w:sdt>
                  <w:sdtPr>
                     <w:alias w:val="Titel" />
                     <w:tag w:val="" />
                     <w:id w:val="-298003193" />
                     <w:placeholder>
                        <w:docPart w:val="93B5A8C633DD478FAF53439635F299F2" />
                     </w:placeholder>
                     <w:dataBinding w:prefixMappings="xmlns:ns0='http://purl.org/dc/elements/1.1/' xmlns:ns1='http://schemas.openxmlformats.org/package/2006/metadata/core-properties' " w:xpath="/ns1:coreProperties[1]/ns0:title[1]" w:storeItemID="{{6C3C8BC8-F283-45AE-878A-BAB7291924A1}}" />
                     <w:text />
                  </w:sdtPr>
                  <w:sdtEndPr />
                  <w:sdtContent>
                     <w:p>
                        <w:pPr>
                           <w:pStyle w:val="DocumentnaamKopRapporttiteltitelpagina" />
                        </w:pPr>
                        <w:r>
                           <w:t>{title}</w:t>
                        </w:r>
                     </w:p>
                  </w:sdtContent>
               </w:sdt>
               <w:p />
               <w:p>
                  <w:pPr>
                     <w:pStyle w:val="Ondertitelrapport" />
                     <w:framePr w:hSpace="0" w:wrap="auto" w:vAnchor="margin" w:yAlign="inline" />
                     <w:suppressOverlap w:val="0" />
                  </w:pPr>
                  <w:r>
                     <w:t>{subtitle}</w:t>
                  </w:r>
               </w:p>
            </w:tc>
         </w:tr>
      </w:tbl>
      <w:p />
      <w:p />
      <w:p />'''

    def document_start(self) -> str:
        return '''<?xml version="1.0" encoding="UTF-8"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:aink="http://schemas.microsoft.com/office/drawing/2016/ink" xmlns:am3d="http://schemas.microsoft.com/office/drawing/2017/model3d" xmlns:cx="http://schemas.microsoft.com/office/drawing/2014/chartex" xmlns:cx1="http://schemas.microsoft.com/office/drawing/2015/9/8/chartex" xmlns:cx2="http://schemas.microsoft.com/office/drawing/2015/10/21/chartex" xmlns:cx3="http://schemas.microsoft.com/office/drawing/2016/5/9/chartex" xmlns:cx4="http://schemas.microsoft.com/office/drawing/2016/5/10/chartex" xmlns:cx5="http://schemas.microsoft.com/office/drawing/2016/5/11/chartex" xmlns:cx6="http://schemas.microsoft.com/office/drawing/2016/5/12/chartex" xmlns:cx7="http://schemas.microsoft.com/office/drawing/2016/5/13/chartex" xmlns:cx8="http://schemas.microsoft.com/office/drawing/2016/5/14/chartex" xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:oel="http://schemas.microsoft.com/office/2019/extlst" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:w10="urn:schemas-microsoft-com:office:word" xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml" xmlns:w15="http://schemas.microsoft.com/office/word/2012/wordml" xmlns:w16="http://schemas.microsoft.com/office/word/2018/wordml" xmlns:w16cex="http://schemas.microsoft.com/office/word/2018/wordml/cex" xmlns:w16cid="http://schemas.microsoft.com/office/word/2016/wordml/cid" xmlns:w16du="http://schemas.microsoft.com/office/word/2023/wordml/word16du" xmlns:w16sdtdh="http://schemas.microsoft.com/office/word/2020/wordml/sdtdatahash" xmlns:w16sdtfl="http://schemas.microsoft.com/office/word/2024/wordml/sdtformatlock" xmlns:w16se="http://schemas.microsoft.com/office/word/2015/wordml/symex" xmlns:wne="http://schemas.microsoft.com/office/word/2006/wordml" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" xmlns:wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing" xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas" xmlns:wpg="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup" xmlns:wpi="http://schemas.microsoft.com/office/word/2010/wordprocessingInk" xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape" mc:Ignorable="w14 w15 w16se w16cid w16 w16cex w16sdtdh w16sdtfl w16du wp14">
   <w:body>
'''

    def document_end(self) -> str:
        return '''
   </w:body>
</w:document>'''

    def index(self, maxlevel=3) -> str:
        def page(lvl: int) -> int:
            nonlocal current_page
            current_page += page_inc[lvl]
            return int(current_page)

        current_page = 18
        page_inc = {1: 1./8, 2: 3./8, 3: 0}

        return ''.join(
            self.index_item(level, text, w_name, page_number=page(level), toc=i==0)
            for i, (level, text, w_name) in enumerate(self.section_titles)
            if level <= maxlevel
        ) + '''
      <w:p>
         <w:r>
            <w:fldChar w:fldCharType="end" />
         </w:r>
      </w:p>'''


    def index_item(self, level: int, text: str, w_name: str, page_number: int, toc: bool = False) -> str:
        bold_text = '''
               <w:b w:val="0" />''' if level == 1 else ''

        toc_declaration = r'''
         <w:r>
            <w:fldChar w:fldCharType="begin" />
         </w:r>
         <w:r>
            <w:instrText xml:space="preserve"> TOC \o "1-3" \h \z \u </w:instrText>
         </w:r>
         <w:r>
            <w:fldChar w:fldCharType="separate" />
         </w:r>''' if toc else ''

        return rf'''
      <w:p>
         <w:pPr>
            <w:pStyle w:val="Inhopg{level}" />
            <w:tabs>
               <w:tab w:val="right" w:leader="dot" w:pos="8494" />
            </w:tabs>
            <w:rPr>
               <w:rFonts w:asciiTheme="minorHAnsi" w:eastAsiaTheme="minorEastAsia" w:hAnsiTheme="minorHAnsi" w:cstheme="minorBidi" />{bold_text}
               <w:noProof />
               <w:kern w:val="2" />
               <w:sz w:val="24" />
               <w:szCs w:val="24" />
               <w14:ligatures w14:val="standardContextual" />
            </w:rPr>
         </w:pPr>{toc_declaration}
         <w:hyperlink w:anchor="{w_name}" w:history="1">
            <w:r>
               <w:rPr>
                  <w:rStyle w:val="Hyperlink" />
                  <w:noProof />
               </w:rPr>
               <w:t>{text}</w:t>
            </w:r>
            <w:r>
               <w:rPr>
                  <w:noProof />
                  <w:webHidden />
               </w:rPr>
               <w:tab />
            </w:r>
            <w:r>
               <w:rPr>
                  <w:noProof />
                  <w:webHidden />
               </w:rPr>
               <w:fldChar w:fldCharType="begin" />
            </w:r>
            <w:r>
               <w:rPr>
                  <w:noProof />
                  <w:webHidden />
               </w:rPr>
               <w:instrText xml:space="preserve"> PAGEREF {w_name} \h </w:instrText>
            </w:r>
            <w:r>
               <w:rPr>
                  <w:noProof />
                  <w:webHidden />
               </w:rPr>
            </w:r>
            <w:r>
               <w:rPr>
                  <w:noProof />
                  <w:webHidden />
               </w:rPr>
               <w:fldChar w:fldCharType="separate" />
            </w:r>
            <w:r>
               <w:rPr>
                  <w:noProof />
                  <w:webHidden />
               </w:rPr>
               <w:t>{page_number}</w:t>
            </w:r>
            <w:r>
               <w:rPr>
                  <w:noProof />
                  <w:webHidden />
               </w:rPr>
               <w:fldChar w:fldCharType="end" />
            </w:r>
         </w:hyperlink>
      </w:p>'''

    def label_item(self, label: str, text: str) -> str:
        return f'''
      <w:p>
         <w:pPr>
            <w:pStyle w:val="Opsommingbullet" />
            <w:numPr>
               <w:ilvl w:val="0" />
               <w:numId w:val="0" />
            </w:numPr>
            <w:ind w:left="227" />
         </w:pPr>
         <w:r>
            <w:rPr>
               <w:b />
               <w:bCs />
            </w:rPr>
            <w:t xml:space="preserve">{label}: </w:t>
         </w:r>
         <w:r>
            <w:t>{text}</w:t>
         </w:r>
      </w:p>'''

    def list_item(self, text: str) -> str:
        return f'''
      <w:p>
         <w:pPr>
            <w:pStyle w:val="Opsommingbullet" />
         </w:pPr>
         <w:r>
            <w:t>{text}</w:t>
         </w:r>
      </w:p>'''

    def page_break(self) -> str:
        return '''
	  <w:p>
         <w:r>
            <w:br w:type="page" />
         </w:r>
	  </w:p>'''

    def page_layout(self, layout_index: Literal[1, 2]) -> str:
        if layout_index == 1:
            return '''
      <w:p>
         <w:pPr>
            <w:sectPr>
               <w:headerReference w:type="default" r:id="rId12" />
               <w:footerReference w:type="default" r:id="rId13" />
               <w:headerReference w:type="first" r:id="rId14" />
               <w:pgSz w:w="11906" w:h="16838" w:code="9" />
               <w:pgMar w:top="2665" w:right="1644" w:bottom="1531" w:left="1758" w:header="709" w:footer="709" w:gutter="0" />
               <w:cols w:space="708" />
               <w:titlePg />
               <w:docGrid w:linePitch="360" />
            </w:sectPr>
         </w:pPr>
      </w:p>'''
        elif layout_index == 2:
            return '''
      <w:sectPr>
         <w:footerReference w:type="default" r:id="rId15" />
         <w:pgSz w:w="11906" w:h="16838" w:code="9" />
         <w:pgMar w:top="2665" w:right="1644" w:bottom="1531" w:left="1758" w:header="709" w:footer="709" w:gutter="0" />
         <w:cols w:space="708" />
         <w:docGrid w:linePitch="360" />
      </w:sectPr>'''

    def section(self, level: int, text: str) -> str:
        w_id = next(self.w_id)
        w_name = f'_Toc{189336553 + w_id}'

        self.level_counter[level] += 1
        try:
            del self.level_counter[level + 1]
            del self.level_counter[level + 2]
        except KeyError:
            pass
        level_text = '.'.join(map(str, self.level_counter.values()))

        self.section_titles.append((level, f'{level_text} {text}', w_name))

        page_break = '''
            <w:lastRenderedPageBreak />''' if level == 1 else ''

        return f'''
	  <w:p>
         <w:pPr>
            <w:pStyle w:val="Kop{level}" />
         </w:pPr>
         <w:bookmarkStart w:id="{w_id}" w:name="{w_name}" />
         <w:r>{page_break}
            <w:t>{text}</w:t>
         </w:r>
         <w:bookmarkEnd w:id="{w_id}" />
      </w:p>'''

    def text(self, text: str = None) -> str:
        return f'''
      <w:p>
         <w:r>
            <w:t>{text}</w:t>
         </w:r>
      </w:p>''' if text else '''
      <w:p />'''

    def title(self, text: str) -> str:
        return f'''{self.page_break()}
      <w:p>
         <w:pPr>
            <w:pStyle w:val="DocumentnaamKopRapporttiteltitelpagina" />
         </w:pPr>
         <w:r>
            <w:lastRenderedPageBreak />
            <w:t>{text}</w:t>
         </w:r>
      </w:p>
      <w:p />
      <w:p />
      <w:p />'''
