from functools import wraps
from enum import Enum
import traceback


class AudioType(Enum):
    FILE_AUDIO = [],
    FEW_AUDIOS: list[str]


AUDIO_FORMATS = {'mka', '3gp', 'aa', 'aac', 'aax', 'act', 'aiff', 'alac', 'amr', 'ape', 'au', 'awb', 'dss', 'dvf',
                 'flac', 'gsm', 'iklax', 'ivs', 'm4a', 'm4b', 'm4p', 'mmf', 'mp3', 'mpc', 'msv', 'nmf', 'ogg', 'oga',
                 'mogg', 'opus', 'ra', 'rm', 'raw', 'rf64', 'sln', 'tta', 'voc', 'vox', 'wav', 'wma', 'wv', '8svx',
                 'cda'}
VIDEO_FORMATS = {'mkv', 'mk3d', 'mp4', 'm4v', 'mov', 'qt', 'asf', 'wmv', 'avi', 'mxf', 'm2p', 'ps', 'ts', 'tsv', 'm2ts',
                 'mts', 'vob', 'evo', '3g2', 'f4v', 'flv', 'ogv', 'ogx', 'webm', 'rmvb', 'divx'}


def file_of_format(path: str, formats: set) -> bool:
    for format in formats:
        if path.endswith(format):
            return True
    return False


def print_exeption(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            err_str = f'Ошибка в функции: {wrapper.__name__}\nПараметры: {args}, {kwargs})\nОшибка: {e}\nСтрока: {traceback.format_exc()}'
            print(err_str)

    return wrapper
