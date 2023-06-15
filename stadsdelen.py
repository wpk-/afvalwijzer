"""
Maakt een afvalwijzer PDF per stadsdeel.

Het script download voor elk stadsdeel de CSV met alle huidige regels.
Dit downloaden neemt enige tijd.
"""
from logging import getLogger, INFO, WARNING
from os import fdopen
from time import time
from typing import Any, Dict

import requests

from afvalwijzer import maak_pdf

getLogger('fontTools').setLevel(WARNING)
getLogger('fpdf').setLevel(INFO)
getLogger('PIL').setLevel(INFO)

logger = getLogger(__name__)


def download_csv(csv_file: str, url: str, params: Dict[str, Any] = None) -> None:
    logger.debug(url)
    logger.debug(params)

    with requests.get(url, params, stream=True) as r:
        r.raise_for_status()
        with open(csv_file, 'wb') as f:
            f.write(r.content)


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)

    afvalwijzer_url = 'https://api.data.amsterdam.nl/v1/afvalwijzer/afvalwijzer/'
    params = {
        'statusAdres[in]': ','.join((
                'Verblijfsobject in gebruik',
                'Plaats aangewezen',
                'Verbijfsobject in gebruik (niet ingemeten)',
            )),
        '_format': 'csv',
        # '_pageSize': 1000,
    }

    for name, query in [
        ('afvalwijzer-centrum', {'gbdBuurtCode[like]': 'A*'}),
        ('afvalwijzer-west', {'gbdBuurtCode[like]': 'E*'}),
        ('afvalwijzer-nieuw-west', {'gbdBuurtCode[like]': 'F*'}),
        ('afvalwijzer-zuid', {'gbdBuurtCode[like]': 'K*'}),
        ('afvalwijzer-oost', {'gbdBuurtCode[like]': 'M*'}),
        ('afvalwijzer-noord', {'gbdBuurtCode[like]': 'N*'}),
        ('afvalwijzer-weesp', {'gbdBuurtCode[like]': 'S*'}),
        ('afvalwijzer-zuidoost', {'gbdBuurtCode[like]': 'T*'}),
    ]:
        csv_file = f'files/{name}.csv'
        pdf_file = f'output/{name}.pdf'

        print(pdf_file)

        # Download de CSV-data naar een tijdelijk bestand en krijg de naam.
        t1 = time()
        download_csv(csv_file, afvalwijzer_url, {**params, **query})
        print(f'- gedownload in {time() - t1:.2f} sec.')

        # Zet om naar PDF.
        t2 = time()
        maak_pdf(csv_file, pdf_file)
        print(f'- omgezet naar pdf in {time() - t2:.2f} sec.')
