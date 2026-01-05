import io
import logging
from collections.abc import Iterable, Iterator
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from afvalwijzer.file_tools import file_stem
from afvalwijzer.models import Brongegeven
from afvalwijzer.io.csv import read as read_csv, write as write_csv

logger = logging.getLogger(__name__)


def read(file_in: Path, filters: dict[str, bool | int | str],
         ) -> Iterator[Brongegeven]:
    """Leest de Afvalwijzer brongegevens uit het zip-bestand.
    """
    csv_filename = csv_name(file_in)

    with (
        ZipFile(file_in, 'r', compression=ZIP_DEFLATED) as zip,
        zip.open(csv_filename, 'r') as raw,
        io.TextIOWrapper(raw, encoding='utf-8', newline='') as f_in
    ):
        for record in read_csv(f_in, filters):
            yield record


def write(file_out: str | Path, data: Iterable[Brongegeven],
          filters: dict[str, bool | int | str]) -> None:
    """Schrijft de ruwe Afvalwijzer brongegevens weg naar het zip-bestand.

    :param Path file_out: De naam van het doelbestand.
    :param Iterable[Brongegeven] data: Reeks met records. (Elk record beschrijft
        op 1 adres de regels voor het aanbieden van afval voor 1 fractie.)
    """
    csv_filename = csv_name(file_out)

    with (
        ZipFile(file_out, 'w', compression=ZIP_DEFLATED, compresslevel=9) as zip,
        zip.open(csv_filename, 'w') as raw,
        io.TextIOWrapper(raw, encoding='utf-8', newline='') as f_out
    ):
        write_csv(f_out, data, filters)


def csv_name(zip_name: str | Path) -> str:
    return f'{file_stem(zip_name)}.csv'
