from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QPushButton


class ProgressWindow(QWidget):
    def __init__(self, optimization_id, signal_close, signal_update, max_progress, max_species, stop, text=""):
        super().__init__()

        self.text = text
        self.max_species = max_species
        self.stop = stop

        self.setWindowTitle(' ')
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        signal_close.connect(self.close)
        signal_update.connect(self.update_progress)

        layout = QVBoxLayout()
        self.setMinimumSize(250, 75)

        self.label = QLabel()
        self.label.setText(self.text)
        layout.addWidget(self.label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.max_progress = max_progress
        self.const = 100 // self.max_progress
        layout.addWidget(self.progress_bar)

        self.stop_button = QPushButton()
        self.stop_button.setText('Stop')
        self.stop_button.clicked.connect(self.close_window)
        layout.addWidget(self.stop_button)

        self.setLayout(layout)

    def update_progress(self, progress, species_no):
        if species_no != -1:
            self.label.setText(self.text+' (' + str(species_no) + '/' + str(self.max_species) + ')')
        self.progress_bar.setValue((self.max_progress - progress) * self.const)

    def close_window(self):
        self.stop()
        self.close()
