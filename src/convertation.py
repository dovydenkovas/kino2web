import os
import pathlib
import subprocess
from multiprocessing import cpu_count

import ffmpeg
from PySide6.QtCore import QObject, Signal, Slot

from utils import print_exeption


def check_input_path(path: str) -> bool:
    if not path:
        return False
    file = pathlib.Path(path)
    return file.is_file()


def check_output_path(path: str) -> bool:
    file = pathlib.Path(path)
    if not path.endswith('.mp4'):
        return False
    return pathlib.Path(file.parent).is_dir()


class Worker(QObject):
    """ Called in new QThread to convert video without freezing window. """
    finished = Signal()
    progress = Signal(int)

    def __init__(self, input_path, goal_size, output_path, audio_path):
        super(Worker, self).__init__()
        self.input_path = input_path
        self.goal_size = goal_size
        self.output_path = output_path
        self.audio_path = audio_path
        self.stop_process_signal = False
        self.duration = 0

    @Slot()
    def stop_process(self):
        self.stop_process_signal = True

    def run(self):
        """Long-running task."""
        self.convert_video()
        self.finished.emit()

    @print_exeption
    def convert_video(self):
        """ Calculate bitrate and convert video by goal_size. """
        if os.name == "nt":  # if windows
            command = 'ffmpeg.exe'
        else: # linux or macos
            command = 'ffmpeg'
       

        self.duration = float(ffmpeg.probe(self.input_path)['format']['duration'])
        n_threads = cpu_count()
        self.total = self.duration
        base_args = [command, ]

        # See offial documentation of ffmpeg:
        # https://trac.ffmpeg.org/wiki/Encode/H.264#Two-PassExample 
        bitrate = int(self.goal_size * 8192 / self.duration - 128)
        if len(self.audio_path) > 0:
            args = [command, '-y', '-threads', str(n_threads), '-i', self.input_path]
            args_inputs = []
            args_merge = []
            i = 1
            for audio in self.audio_path:
                if isinstance(audio, int):
                    args_merge += ['-map', f'0:a:{audio-1}']
                else:
                    args_inputs += ['-i', str(audio)]
                    args_merge += ['-map', f'{i}:a:0']
                    i += 1
            args += args_inputs
            args += args_merge
            args += ['-c:v', 'mpeg4', '-map', '0:v:0', '-c:a','aac', '-preset:v', 'veryhigh', '-ac', '2','-b:a', '128k', '-b:v', f'{bitrate}k',
                     self.output_path, '-progress', 'pipe:1']

        else: # Default audio
            args = [command, '-y', '-progress', 'pipe:1', '-threads', str(n_threads), '-i',
                    str(self.input_path), '-c:v', 'mpeg4', '-c:a', 'aac','-preset:v',
                    'veryhigh', '-ac', '2', '-b:a', '128k', '-b:v', f'{bitrate}k', str(self.output_path), ]

        
        if not os.name == "nt":
            res = []
            for arg in args:
                if ' ' in arg:
                    res.append(f"'{arg}'")
                else:
                    res.append(arg)

            args = [' '.join(res)]

        print(*args)
        print()
        with subprocess.Popen(args, stdout=subprocess.PIPE,
                              bufsize=1, stdin=subprocess.PIPE,
                              universal_newlines=True, shell=True) as proc:
            self.mainloop(proc)

    @print_exeption
    def mainloop(self, proc):
        while True:
            line = proc.stdout.readline()
            if self.parse_line(proc, line):
                break

    @print_exeption
    def parse_line(self, proc, line):
        parts = line.rstrip().split('=')
        key = parts[0] if len(parts) > 0 else None
        value = parts[1] if len(parts) > 1 else 0

        if key == 'out_time_ms':
            time = max(round(float(value) / 10000., 2), 0)
            self.progress.emit(round(time / round(self.duration, 2)))
            if self.stop_process_signal:
                proc.stdin.write('q')
                proc.terminate()
                self.progress.emit(100)
                return True

        elif key == 'progress' and value == 'end' or key == '':
            self.progress.emit(100)
            return True


