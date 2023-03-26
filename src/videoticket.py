import os
import pathlib

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QPushButton, QLabel, QPushButton, \
    QWidget, QProgressBar, QSlider, \
    QFileDialog, QGroupBox, QCheckBox, QHBoxLayout, QComboBox

from PySide6.QtCore import Qt, QMimeData
from PySide6.QtGui import QDrag
from PySide6 import QtGui
import ffmpeg

import convertation
from utils import file_of_format, VIDEO_FORMATS, AUDIO_FORMATS, print_exeption
from audiowidget import AudioWidget


class VideoTicket(QGroupBox):
    delete_ticket = Signal(object)

    @print_exeption
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setMouseTracking(True)

        self.indicator = QWidget()
        self.input_path_btn = QPushButton("Выбрать входной файл")
        self.input_path_btn.clicked.connect(self.select_input_path)
        self.input_path_btn.setMinimumWidth(150)
        self.output_path_btn = QPushButton('Выбрать выходной файл')
        self.output_path_btn.clicked.connect(self.select_output_path)
        self.output_path_btn.setMinimumWidth(150)
        self.more_options = QCheckBox("Ещё")
        self.more_options.clicked.connect(self.show_more_options)

        self._goal_size_slider = QSlider(Qt.Orientation.Horizontal)
        self._goal_size_slider.setFixedWidth(100)
        self._goal_size_slider.setRange(1, 6000)
        self._goal_size_slider.setPageStep(1)
        self._goal_size_slider.setValue(2048)
        self._goal_size_slider.valueChanged.connect(self.update_goal_size_lbl)
        self.goal_size_lbl = QLabel()
        self.update_goal_size_lbl()
        self.input_audio_btn = AudioWidget()
        self.input_audio_btn.setCurrentText("Выбрать дорожку")
        self.input_audio_btn.setMinimumWidth(150)
        self.streams = {}
        self.progressbar = QProgressBar()
        self.progressbar.setFixedWidth(150)

        self.indicator.setFixedSize(15, 15)
        self.delete_task_btn = QPushButton('X')
        self.delete_task_btn.setFixedSize(15, 15)
        self.delete_task_btn.clicked.connect(self.close)
        grid = QHBoxLayout(self)

        grid.addWidget(self.delete_task_btn)
        grid.addWidget(self.input_path_btn)
        grid.addWidget(self.output_path_btn)
        grid.addWidget(self.more_options)
        grid.addWidget(self._goal_size_slider)
        grid.addWidget(self.goal_size_lbl)
        grid.addWidget(self.input_audio_btn)
        grid.addWidget(self.progressbar)
        grid.addWidget(self.indicator)
        self.reset_done()
        self.delete_task_btn.setStyleSheet('background: #711800; color: white; font-weight: bold; border-radius: 5px;')
        self.setStyleSheet('QGroupBox {background: #eaeaea; border-radius: 15px;}')

        self.progressbar.hide()
        self.setFixedHeight(40)
        self.setContentsMargins(0, 0, 0, 0)
        self.show_more_options()

        self._input_path = ''
        self._output_path = ''
        self._audio_path = ''
        self._is_done = False

    def get_input_path(self) -> str:
        return self._input_path

    def is_more_options(self) -> bool:
        return self.more_options.isChecked()

    def set_input_path(self, path: str):
        if convertation.check_input_path(path):
            self._input_path = path
            self.input_path_btn.setText(pathlib.Path(path).name)
            self._set_output_path_by_input_path(path)
            self._set_file_size_range_by_input_file_size(path)
            self.input_audio_btn.load_streams_from_video(path)
            self.reset_done()

    def get_output_path(self) -> str:
        return self._output_path

    def set_output_path(self, path: str):
        self._output_path = path
        self.output_path_btn.setText(pathlib.Path(path).name)
        self.reset_done()

    @print_exeption
    def get_audio_path(self) -> list[str]:
        if self.is_more_options():
            return self.input_audio_btn.get_audio()
        return []

    def get_goal_size(self) -> int:
        return self._goal_size_slider.value()

    def set_audio_path(self, path):
        self.input_audio_btn.append_audio(path)
        self.reset_done()
        # if convertation.check_input_path(path):
        #     if not pathlib.Path(path).name in self.streams:
        #         self.input_audio_btn.insertItem(0, pathlib.Path(path).name)
        #         self.streams[pathlib.Path(path).name] = path
        #         self._audio_path = path
        #     self.reset_done()

    def close(self):
        self.delete_ticket.emit(self)
        super().close()

    def set_done(self):
        self.indicator.setStyleSheet("background: green; border-radius: 5px;")
        self._is_done = True

    def set_error(self):
        self.indicator.setStyleSheet("background: #711800; border-radius:5px;")
        self._is_done = False

    def reset_done(self):
        self.indicator.setStyleSheet("background: #FFC900; border-radius: 5px;")
        self._is_done = False

    def is_done(self):
        return self._is_done

    def switch_converting_view(self):
        self.delete_task_btn.setDisabled(True)
        self.progressbar.show()
        self.input_path_btn.setDisabled(True)
        self.output_path_btn.setDisabled(True)
        self._goal_size_slider.setDisabled(True)
        self.input_audio_btn.setDisabled(True)
        self.more_options.setDisabled(True)

    def switch_input_view(self):
        self.delete_task_btn.setDisabled(False)
        self.progressbar.setValue(0)
        self.progressbar.hide()
        self.input_path_btn.setDisabled(False)
        self.output_path_btn.setDisabled(False)
        self._goal_size_slider.setDisabled(False)
        self.input_audio_btn.setDisabled(False)
        self.more_options.setDisabled(False)

    def show_more_options(self):
        if self.more_options.isChecked():
            self._goal_size_slider.show()
            self.goal_size_lbl.show()
            self.input_audio_btn.show()
        else:
            self._goal_size_slider.hide()
            self.goal_size_lbl.hide()
            self.input_audio_btn.hide()

    def select_input_path(self):
        """ Ask user for filename of input video. """
        video = '*.' + ' *.'.join(VIDEO_FORMATS)
        path = QFileDialog.getOpenFileName(self, 'Open file',
                                           '', f"Киношки ({video})")[0]
        self.set_input_path(path)

    def _set_output_path_by_input_path(self, input_path):
        if input_path.endswith('.mp4'):
            self._output_path = input_path + '.mp4'
        else:
            self._output_path = '.'.join(input_path.split('.')[:-1]) + '.mp4'
        self.output_path_btn.setText(pathlib.Path(self._output_path).name)

    def _set_file_size_range_by_input_file_size(self, input_path):
        """Update slider range. You can't compress file more than 10 times."""
        file_size = os.path.getsize(input_path) // 1024 // 1024  # Input file size in MiB
        self._goal_size_slider.setRange(max(file_size // 10, 1), file_size)

    def select_output_path(self):
        """ Ask user for filename of output video. """
        self.set_output_path(QFileDialog.getSaveFileName(self, 'Save file',
                                                         '', "То что получится (*.mp4)")[0])

    def update_goal_size_lbl(self):
        self.reset_done()
        """ Translate number of MiB to number with postfix MiB or GiB """
        goal_size = self._goal_size_slider.value()
        if goal_size < 1024:
            self.goal_size_lbl.setText(f"{goal_size} МиБ")
        else:
            self.goal_size_lbl.setText(f"{round(goal_size / 1024, 1)} ГиБ")

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    @print_exeption
    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        for f in files:
            if file_of_format(f, VIDEO_FORMATS):
                self.set_input_path(f)
            elif file_of_format(f, AUDIO_FORMATS):
                self.input_audio_btn.append_audio(f)
                self.more_options.setChecked(True)
                self.show_more_options()
        self.reset_done()
        event.accept()

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.buttons() == Qt.MouseButton.LeftButton:
            try:
                drag = QDrag(self)
                mime = QMimeData()
                drag.setMimeData(mime)
                drag.exec(Qt.DropAction.MoveAction)
            except Exception as e:
                print(e.args)
