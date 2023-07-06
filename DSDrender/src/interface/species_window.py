from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGraphicsView, QPushButton


class SpeciesWindow(QWidget):
    def __init__(self, signal, name, save):
        super().__init__()
        self.setWindowTitle(name)
        signal.connect(self.close)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        layout = QVBoxLayout()
        self.save_button = QPushButton()
        self.save_button.setText('Save')
        self.save_button.setFixedWidth(100)
        layout.addWidget(self.save_button)

        self.view = QGraphicsView()
        layout.addWidget(self.view)
        self.setLayout(layout)

        self.save_button.clicked.connect(lambda: save(self.view))
