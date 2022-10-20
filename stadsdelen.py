"""
Maakt een afvalwijzer PDF per stadsdeel.

Het script download voor elk stadsdeel de CSV met alle huidige regels.
Dit downloaden neemt enige tijd.
"""
from os import fdopen
from pathlib import Path
from shutil import copyfileobj
from tempfile import mkstemp
from time import time
from typing import Any, Dict

import requests

from afvalwijzer import maak_pdf


def download_csv(url: str, params: Dict[str, Any] = None) -> str:
    tmp_fd, tmp_file = mkstemp(suffix='.csv')

    with requests.get(url, params, stream=True) as r:
        r.raise_for_status()
        with fdopen(tmp_fd, 'wb') as f:
            copyfileobj(r.raw, f)
            # for chunk in r.iter_content():
            #     f.write(chunk)

    return tmp_file


if __name__ == '__main__':
    afvalwijzer_url = 'https://api.data.amsterdam.nl/v1/afvalwijzer/afvalwijzer/'
    params = {
        'statusAdres[in]': ('Verblijfsobject in gebruik',
                            'Plaats aangewezen',
                            'Verbijfsobject in gebruik (niet ingemeten)',
                            ),
        '_format': 'csv',
        # '_pageSize': 1000,
    }

    for pdf_file, query in [
        ('output/afvalwijzer-centrum.pdf', {'gbdBuurtCodeId[like]': 'A*'}),
        ('output/afvalwijzer-west.pdf', {'gbdBuurtCodeId[like]': 'E*'}),
        ('output/afvalwijzer-nieuw-west.pdf', {'gbdBuurtCodeId[like]': 'F*'}),
        ('output/afvalwijzer-zuid.pdf', {'gbdBuurtCodeId[like]': 'K*'}),
        ('output/afvalwijzer-oost.pdf', {'gbdBuurtCodeId[like]': 'M*'}),
        ('output/afvalwijzer-noord.pdf', {'gbdBuurtCodeId[like]': 'N*'}),
        ('output/afvalwijzer-weesp.pdf', {'gbdBuurtCodeId[like]': 'S*'}),
        ('output/afvalwijzer-zuidoost.pdf', {'gbdBuurtCodeId[like]': 'T*'}),
    ]:
        print(pdf_file)

        # Download de CSV-data naar een tijdelijk bestand en krijg de naam.
        t1 = time()
        csv_file = download_csv(afvalwijzer_url, {**params, **query})
        print(f'- gedownload in {time() - t1:.2f} sec.')

        try:
            # Zet om naar PDF.
            t2 = time()
            maak_pdf(csv_file, pdf_file)
            print(f'- omgezet naar pdf in {time() - t2:.2f} sec.')
        finally:
            # Wat er ook gebeurt, verwijder altijd het tijdelijke bestand.
            Path(csv_file).unlink()
