from functools import wraps
from enum import Enum
import traceback
import os

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel

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
            
            if os.getenv("DEBUG") != "True":
                dlg = QDialog()
                dlg.setWindowTitle("Что-то пошло не так :(")
                QBtn = QDialogButtonBox.Ok #| QDialogButtonBox.Cancel
                buttonBox = QDialogButtonBox(QBtn)
                buttonBox.accepted.connect(dlg.accept)

                layout = QVBoxLayout()
                message = QLabel("Ошибка сохранена в файл ERRORS.log\n" + err_str)
                layout.addWidget(message)
                layout.addWidget(buttonBox)
                dlg.setLayout(layout)

                dlg.exec_()

    return wrapper
