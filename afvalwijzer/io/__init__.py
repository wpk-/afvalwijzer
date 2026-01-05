from collections.abc import Iterable, Iterator
from pathlib import Path

from afvalwijzer.models import Brongegeven


def read(file_in: str | Path, filters: dict[str, bool | int | str],
         ) -> Iterator[Brongegeven]:
    """Leest de Afvalwijzer data-export vanuit PowerBI (xlsx).
    """
    format = Path(file_in).suffix.lower()

    if format == '.csv':
        from .csv import read as _read
    elif format == '.docx':
        from .docx import read as _read
    elif format == '.pdf':
        from .pdf import read as _read
    elif format == '.xlsx':
        from .xlsx import read as _read
    elif format == '.yaml':
        from .db import read as _read
    elif format == '.zip':
        from .zip import read as _read
    else:
        raise ValueError(f'Unsupported file format: {format!r}')

    return _read(file_in, filters)



def write(file_out: str | Path, data: Iterable[Brongegeven],
          filters: dict[str, bool | int | str]) -> None:
    """Schrijft de regels uit de Afvalwijzer naar het bestand.

    Afhankelijk van het gekozen bestandsformaat worden de regels weggeschreven
    als ruwe data (dit geldt onder andere voor csv en xlsx) of in samengevatte
    menselijk leesbare vorm (onder andere pdf).
    """
    format = Path(file_out).suffix.lower()

    if format == '.csv':
        from .csv import write as _write
    elif format == '.docx':
        from .docx import write as _write
    elif format == '.pdf':
        from .pdf import write as _write
    elif format == '.xlsx':
        from .xlsx import write as _write
    elif format == '.yaml':
        from .db import write as _write
    elif format == '.zip':
        from .zip import write as _write
    else:
        raise ValueError(f'Unsupported file format: {format!r}')

    return _write(file_out, data, filters)
