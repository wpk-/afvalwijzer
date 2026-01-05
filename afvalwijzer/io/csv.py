import csv
import logging
from collections.abc import Iterable, Iterator, Callable
from operator import itemgetter
from pathlib import Path
from typing import TextIO

from afvalwijzer.file_tools import open_file
from afvalwijzer.models import Brongegeven

logger = logging.getLogger(__name__)

DELIMITER = ','
QUOTECHAR = '"'


def read(file_in: str | Path | TextIO, filters: dict[str, bool | int | str],
         ) -> Iterator[Brongegeven]:
    """Leest de Afvalwijzer brongegevens uit het csv-bestand.
    """
    def filters_fcn() -> Callable[[list[str]], bool]:
        """Filtert rijen uit de csv op basis van `filters`.
        """
        key = itemgetter(*(
            Brongegeven._fields.index(fld)
            for fld in filters.keys()
        ))
        val = tuple(map(str, filters.values()))

        def func(x: list[str]) -> bool: return key(x) == val

        return func

    def parse_line(line: list[str | bool | int]) -> Brongegeven:
        """Zet een csv regel om in een `Brongegeven`.
        """
        line[woonfunctie_index] = line[woonfunctie_index] != 'False'
        line[huisnummer_index] = int(line[huisnummer_index])
        return Brongegeven(*line)

    woonfunctie_index = Brongegeven._fields.index('woonfunctie')
    huisnummer_index = Brongegeven._fields.index('huisnummer')

    with open_file(file_in, 'r', encoding='utf-8', newline='') as f_in:
        reader = csv.reader(f_in, delimiter=DELIMITER, quotechar=QUOTECHAR)

        header = tuple(s.lower() for s in next(reader))

        if header != Brongegeven._fields:
            try:
                index = [header.index(fld) for fld in Brongegeven._fields]
            except ValueError:
                logger.warning(header)
                logger.warning(Brongegeven._fields)
                raise ValueError('De header van het csv-bestand wordt niet herkend.')
            else:
                reader = map(itemgetter(*index), reader)

        if filters:
            reader = filter(filters_fcn(), reader)

        for record in map(parse_line, reader):
            yield record


def write(file_out: str | Path | TextIO, data: Iterable[Brongegeven],
          filters: dict[str, bool | int | str]) -> None:
    """Schrijft de ruwe Afvalwijzer brongegevens weg naar het csv-bestand.

    :param Path file_out: De naam van het doelbestand.
    :param Iterable[Brongegeven] data: Reeks met records. (Elk record beschrijft
        op 1 adres de regels voor het aanbieden van afval voor 1 fractie.)
    :param dict filters: Filters die reeds toegepast zijn op de data. Dit
        argument wordt hier niet gebruikt. Het kan in andere bestandsformaten
        gebruikt worden om bijvoorbeeld informatie over de toegepaste filters
        op te nemen in een veld zoals de titel.
    """
    with open_file(file_out, 'w', newline='', encoding='utf-8') as f_out:
        writer = csv.writer(f_out, delimiter=DELIMITER, quotechar=QUOTECHAR)
        writer.writerow(tuple(s.capitalize() for s in Brongegeven._fields))
        writer.writerows(data)
