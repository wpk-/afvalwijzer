from pathlib import Path
from typing import IO


class open_file(object):
    """Context manager that opens a filename and closes it on exit, but does
    nothing for file-like objects.
    """
    def __init__(self, filename, *args, **kwargs):
        self.closing = kwargs.pop('closing', False)
        try:
            self.fh = open(filename, *args, **kwargs)
        except TypeError:
            self.fh = filename
        else:
            self.closing = True

    def __enter__(self):
        return self.fh

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.closing:
            self.fh.close()

        return False


def file_stem(fileobj: str | Path | IO) -> str:
    """Returns the stem, also for file objects. "x/y/z/abc.d.ef" -> "abc.d".
    """
    try:
        return Path(fileobj).stem
    except TypeError:
        try:
            return Path(fileobj.name).stem
        except AttributeError:
            return 'unknown'
