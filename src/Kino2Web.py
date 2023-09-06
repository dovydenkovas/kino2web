""" 
    Kino2Web main file.
"""

import datetime
import os
import sys
from time import sleep

from PySide6.QtCore import QThread, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QMainWindow, QApplication, QPushButton, QLabel, \
    QGridLayout, QWidget, QSlider, QScrollArea, QMessageBox
from PySide6 import QtGui

import convertation
from ticketsview import TicketsView
from utils import file_of_format, VIDEO_FORMATS, print_exeption
from videoticket import VideoTicket


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.interrupt_worker = False
        self.initUI()
        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        self.show()

    def initUI(self):
        """ Make GUI interface """
        self.convert_btn = QPushButton("Конвертировать")
        self.convert_btn.clicked.connect(self.start_convertion)
        self.convert_btn.setStyleSheet("margin-left: 100%; margin-right: 100%; padding-top: 5%; padding-bottom: 5%;")
        self.add_ticket_btn = QPushButton("Добавить кину")
        self.add_ticket_btn.clicked.connect(self.add_ticket)
        self.remove_done_tickets_btn = QPushButton("Удалить завершенные")
        self.remove_done_tickets_btn.clicked.connect(self.remove_done_tickets)
        self.reset_done_tickets_btn = QPushButton("Сбросить статус")
        self.reset_done_tickets_btn.clicked.connect(self.reset_all_tickets)

        self.tickets = TicketsView()

        scroll = QScrollArea()

        w2 = QWidget()
        w2.setLayout(self.tickets)
        scroll.setWidget(w2)
        scroll.setWidgetResizable(True)
        scroll.setWidget(w2)

        self._goal_size_slider = QSlider(Qt.Orientation.Horizontal)

        self._goal_size_slider.setRange(1, 2048)
        self._goal_size_slider.setPageStep(1)
        self._goal_size_slider.setValue(2048)
        self._goal_size_slider.valueChanged.connect(self.update_goal_size_lbl)
        self.goal_size_lbl = QLabel()
        self.update_goal_size_lbl()

        wgt = QWidget()
        grid = QGridLayout(wgt)
        grid.addWidget(self.convert_btn, 1, 0, 1, 4)
        grid.addWidget(scroll, 2, 0, 1, 4)
        grid.addWidget(self._goal_size_slider, 4, 1, 1, 3)
        grid.addWidget(self.goal_size_lbl, 4, 0, 1, 1)
        grid.addWidget(self.remove_done_tickets_btn, 3, 0, 1, 1)
        grid.addWidget(self.reset_done_tickets_btn, 3, 1, 1, 1)
        grid.addWidget(self.add_ticket_btn, 3, 2, 1, 2)
        self.setCentralWidget(wgt)
        self.setWindowTitle("Kino2Web converter v1.2.1")
        self.resize(800, 400)

    def add_ticket(self):
        ticket = VideoTicket()
        self.tickets.add_ticket(ticket)

    @print_exeption
    def remove_done_tickets(self, *args):
        i = 0
        while i < len(self.tickets):
            if self.tickets[i].is_done() or self.tickets[i].is_empty():
                self.tickets.delete_ticket(self.tickets[i])
                continue
            i += 1
    @print_exeption
    def reset_all_tickets(self, *args):
        for ticket in self.tickets:
            ticket.reset_done()

    @print_exeption
    def start_convertion(self, *args):
        """ Prepare input data and start thread of convertation data """
        if self.worker:
            self.worker.stop_process()
            self.interrupt_worker = True
            return
        self.interrupt_worker = False
        iterator = self.tickets.__iter__()
        self.convert_ticket(iterator)

    @print_exeption
    def convert_ticket(self, iterator):
        try:
            ticket = iterator.__next__()
            ticket: VideoTicket
        except StopIteration:
            self.interrupt_worker = False
            return

        def next_conversion():
            self.convert_ticket(iterator)

        @print_exeption
        def update_gui_on_end_of_convertation():
            self.convert_btn.setText("Пуск")
            ticket.switch_input_view()
            if not self.interrupt_worker:
                ticket.set_done()
            self.worker = None
            next_conversion()

        if self.interrupt_worker or ticket.is_done():
            next_conversion()
            return

        input_path = ticket.get_input_path()
        output_path = ticket.get_output_path()
        audio_path = ticket.get_audio_path()

        if (not convertation.check_input_path(input_path)) or \
            (not convertation.check_output_path(output_path) and
             output_path != input_path):
            ticket.set_error()
            next_conversion()
            return

        if ticket.is_more_options():
            goal_size = ticket.get_goal_size()
        else:
            goal_size = self._goal_size_slider.value()

        ticket.switch_converting_view()

        self.thread = QThread()
        self.worker = convertation.Worker(input_path, goal_size, output_path, audio_path)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(ticket.progressbar.setValue)

        self.convert_btn.setText("Остановись")
        self.thread.finished.connect(update_gui_on_end_of_convertation)
        self.thread.start()

    def update_goal_size_lbl(self):
        """ Translate number of MiB to number with postfix MiB or GiB """
        goal_size = self._goal_size_slider.value()

        for ticket in self.tickets:
            if ticket.get_goal_size() > goal_size:
                ticket.reset_done()

        if goal_size < 1024:
            self.goal_size_lbl.setText(f"{goal_size} МиБ")
        else:
            self.goal_size_lbl.setText(f"{round(goal_size / 1024 * 10) / 10} ГиБ")

    def dragEnterEvent(self, event):
        event.accept()

    @print_exeption
    def dropEvent(self, event: QtGui.QDropEvent) -> None:
        if event.mimeData().hasUrls():
            files = [u.toLocalFile() for u in event.mimeData().urls()]
            for f in files:
                if file_of_format(f, VIDEO_FORMATS):
                    ticket = VideoTicket()
                    ticket.set_input_path(f)
                    self.tickets.add_ticket(ticket)
        else:
            try:
                widget = event.source()
                y = event.position().y() - self.convert_btn.y() - self.convert_btn.height() + widget.height()//2
                
                for n in range(self.tickets.count()):
                    w = self.tickets.itemAt(n).widget()
                    if w is None:
                        continue

                    y1 = w.y() + w.height() // 2 
                    if y < y1:
                         self.tickets.move_ticket(max(0, n-1), widget)
                         break
                else:
                    self.tickets.move_ticket(self.tickets.count()-2, widget)
            except Exception as e:
                print(e)
        event.accept()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        if self.worker is None:
            a0.accept()
            return
        dialog = QMessageBox(parent=self, text="Вы точно хотите прервать всё и уйти?")
        dialog.setWindowTitle("Вы уверены?")
        dialog.setIcon(QMessageBox.Icon.Question)
        dialog.setStandardButtons(QMessageBox.StandardButton.No |
                               QMessageBox.StandardButton.Ok)
        ret = dialog.exec()

        if ret == QMessageBox.StandardButton.Ok:
            self.worker.stop_process()
            self.interrupt_worker = True
            sleep(1)
            a0.accept()
        else:
            a0.ignore()


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def get_logo_path() -> str:
    """ Return filename of logo by current date. """
    if datetime.datetime.today().month in [1, 12]:  # New year icon in January and December
        return 'data/logo_new_year.svg'
    return 'data/logo.svg'


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    app.setWindowIcon(QIcon(resource_path(get_logo_path())))
    app.exec()
