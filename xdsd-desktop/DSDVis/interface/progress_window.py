from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QPushButton


class ProgressWindow(QWidget):
    def __init__(self, optimization_id, signal_close, signal_update, max_progress, max_species, stop):
        super().__init__()
        self.setWindowTitle(' ')
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        signal_close.connect(self.close)
        signal_update.connect(self.update_progress)

        layout = QVBoxLayout()
        self.setMinimumSize(250, 75)

        self.label = QLabel()
        self.max_species = max_species
        self.label.setText('Rendering in progress... (0/' + str(self.max_species) + ')')
        layout.addWidget(self.label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.max_progress = max_progress
        self.const = 100 // self.max_progress
        layout.addWidget(self.progress_bar)

        self.stop_button = QPushButton()
        self.stop_button.setText('Stop')
        self.stop_button.clicked.connect(lambda: stop(optimization_id))
        layout.addWidget(self.stop_button)

        self.setLayout(layout)

    def update_progress(self, progress, species_no):
        self.label.setText('Rendering in progress... (' + str(species_no) + '/' + str(self.max_species) + ')')
        self.progress_bar.setValue((self.max_progress - progress) * self.const)
