import os
import pathlib

from PySide6 import QtCore
from PySide6.QtWidgets import QPushButton, QLabel, \
    QWidget, QProgressBar, QSlider, \
    QFileDialog, QGroupBox, QCheckBox, QHBoxLayout, QComboBox


from PySide6.QtGui import QStandardItemModel
from PySide6.QtCore import Qt, QMimeData
from PySide6.QtGui import QDrag
from PySide6 import QtGui
import ffmpeg
import sys

from utils import AUDIO_FORMATS, print_exeption



# n = ''
# count = 0
# for i in item_list:
#     if count == 0:
#         n += ' % s' % i
#     else:
#         n += ', % s' % i
#     count += 1
#
# for i in range(self.count()):
#     text_label = self.model().item(i, 0).text()
#     if text_label.find('-') >= 0:
#         text_label = text_label.split('-')[0]
#     item_new_text_label = text_label + ' - selected index: ' + n





class AudioWidget(QComboBox):
    def __init__(self):
        super().__init__()
        #super(QComboBox, self).__init__()
        self.view().pressed.connect(self.handle_item_pressed)
        self.setModel(QStandardItemModel(self))
        self.addItem("Добавить дорожку")
        self.streams = {}

    @print_exeption
    def handle_item_pressed(self, index):
        item = self.model().itemFromIndex(index)
        if item.text() == "Добавить дорожку":
            self.select_audio_path()
            return

        if item.checkState() == Qt.CheckState.Checked:
            item.setCheckState(Qt.CheckState.Unchecked)
        else:
            item.setCheckState(Qt.CheckState.Checked)
        self.check_items()

    @print_exeption
    def item_checked(self, index):
        item = self.model().item(index, 0)
        return item.checkState() == Qt.CheckState.Checked

    @print_exeption
    def check_items(self):
        checkedItems = []
        for i in range(self.count()):
            if self.item_checked(i):
                checkedItems.append(self.itemText(i))
        self.update_labels(checkedItems)

    @print_exeption
    def update_labels(self, item_list):
        if len(item_list) == 1:
            return self.setCurrentText(' '.join(map(str, item_list)))
        self.setCurrentText("item_list")

    def select_audio_path(self):
        """ Ask user for filename of input video. """
        audio = '*.' + ' *.'.join(AUDIO_FORMATS)
        path = QFileDialog.getOpenFileName(self, 'Open file',
                                           '', f"Дорожки ({audio})")[0]
        if path:
            self.append_audio(path)

    def get_audio(self) -> list[str]:
        checkedItems = []
        for i in range(self.count()):
            if self.item_checked(i):
                checkedItems.append(self.streams[self.itemText(i)])
        self.update_labels(checkedItems)
        return checkedItems

    def append_audio(self, path, title=None):
        title = title or pathlib.Path(path).name
        self.streams[title] = path
        self.addItem(title)

    def load_streams_from_video(self, video_path):
        probe = ffmpeg.probe(video_path)
        for audio in (probe['streams']):
            if (audio['codec_type'] == 'audio'):

                title = audio.get('tags').get('title')
                if title is None:
                    title = 'Дорожка ' + str(len(self.streams) + 1)

                if (lang := audio.get('tags').get('language')) is not None:
                    title += f' ({lang})'
                self.append_audio(audio.get('index'), title)

    # sys.stdout.flush()
