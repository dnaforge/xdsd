from PyQt5.QtCore import QObject, pyqtSignal


class ParsingSignals(QObject):
    finished = pyqtSignal()
    update = pyqtSignal(float, int)