from pathlib import Path
import datetime


def get_file_name(number, path=None, ext='jpg'):
    if path is None:
        path = Path(__file__).parent
    if isinstance(path, str):
        path = Path(path)
    if ext.startswith('.'):
        ext = ext[1:]
    dt = datetime.datetime.today().timetuple()
    year = f'{dt.tm_year}'[2:]
    month = f'{dt.tm_mon}'.zfill(2)
    day = f'{dt.tm_mday}'.zfill(2)
    hour = f'{dt.tm_hour}'.zfill(2)
    minutes = f'{dt.tm_min}'.zfill(2)
    sec = f'{dt.tm_sec}'.zfill(2)
    return path / f'{day}{month}{year}-{hour}{minutes}{sec}-{number}.{ext}'


def read_settings(filename):
    ...





