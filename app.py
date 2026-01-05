import logging
from argparse import ArgumentParser
from pathlib import Path
from typing import Optional

from afvalwijzer.azure import get_access_token
from afvalwijzer.io import db, read, write

logger = logging.getLogger(__name__)


def convert(file_in: str | Path, file_out: str | Path,
            filters: dict[str, bool | int | str]) -> Optional[str]:
    try:
        data = read(file_in, filters)
        write(file_out, data, filters)
    except db.TokenExpiredError:
        logger.debug('Het wachtwoord voor de databaseverbinding is verlopen.'
                    ' Een nieuw wachtwoord wordt automatisch aangevraagd...')
        db.update_params(file_in, password=get_access_token())
        data = read(file_in, filters)
        write(file_out, data, filters)
    except db.ConnectionFailedError as err:
        return err.args[0]


def main() -> Optional[str]:
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('fontTools').setLevel(logging.WARN)
    logging.getLogger('fpdf').setLevel(logging.WARN)
    logging.getLogger('pikepdf').setLevel(logging.WARN)
    logging.getLogger('PIL').setLevel(logging.WARN)

    parser = ArgumentParser(
        prog='app.py',
        description='Maakt backups en uitdraaien van gegevens in de afvalwijzer',
    )
    parser.add_argument('file_in', help='Leest de gegevens uit dit bestand.')
    parser.add_argument('file_out', help='Schrijft de gegevens naar dit bestand.')
    parser.add_argument('--stadsdeel', help='Verwerkt alleen de regels voor dit stadsdeel.')
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument('--bewoners', action='store_true', help='Verwerkt alleen de regels voor bewoners.')
    group.add_argument('--bedrijven', action='store_true', help='Verwerkt alleen de regels voor bedrijven.')
    args = parser.parse_args()

    filters = {}

    if args.bewoners:
        filters['woonfunctie'] = True
    elif args.bedrijven:
        filters['woonfunctie'] = False
    if args.stadsdeel:
        filters['stadsdeel'] = args.stadsdeel

    return convert(args.file_in, args.file_out, filters)


if __name__ == '__main__':
    import sys
    sys.exit(main())
