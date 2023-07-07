from PyQt5.QtCore import QLineF, QPointF, QRectF, Qt
from PyQt5.QtGui import QPen, QColor, QPainter, QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGraphicsView, QHBoxLayout, QGraphicsItem, QPushButton


class ReactionWindow(QWidget):
    def __init__(self, signal, name, save):
        super().__init__()
        self.setWindowTitle(name)
        signal.connect(self.close)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        layout = QHBoxLayout()

        input_layout = QVBoxLayout()
        output_layout = QVBoxLayout()

        self.view_input = QGraphicsView()
        self.view_output = QGraphicsView()
        self.view_reaction = QGraphicsView()
        self.view_reaction.setMaximumHeight(150)
        self.view_reaction.setMaximumWidth(150)

        self.input_save_button = QPushButton()
        self.input_save_button.setText('Save')
        self.input_save_button.setFixedWidth(100)

        self.output_save_button = QPushButton()
        self.output_save_button.setText('Save')
        self.output_save_button.setFixedWidth(100)

        input_layout.addWidget(self.input_save_button)
        input_layout.addWidget(self.view_input)

        output_layout.addWidget(self.output_save_button)
        output_layout.addWidget(self.view_output)

        layout.addLayout(input_layout)
        layout.addWidget(self.view_reaction)
        layout.addLayout(output_layout)

        self.setLayout(layout)

        self.input_save_button.clicked.connect(lambda: save(self.view_input))
        self.output_save_button.clicked.connect(lambda: save(self.view_output))


class ReactionArrowGraphicsItem(QGraphicsItem):
    def __init__(self, reaction_name, black_reaction_rate, gray_reaction_rate):
        QGraphicsItem.__init__(self, parent=None)
        self.reaction_name = reaction_name
        self.black_reaction_rate = black_reaction_rate
        self.gray_reaction_rate = gray_reaction_rate

    def boundingRect(self):
        return QRectF(20, 40, 110, 50)

    def paint(self, painter, option, widget):
        pen = QPen()
        painter.setFont(QFont('Arial', 14, 1))

        painter.drawText(40, 40, self.reaction_name)

        painter.setFont(QFont('Arial', 8, 1))

        painter.drawText(50, 80, str(self.black_reaction_rate))

        pen.setWidth(3)
        painter.setPen(pen)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.drawLine(30, 65, 110, 65)
        arrow = QLineF()
        arrow.setP1(QPointF(110, 65))
        arrow.setAngle(135)
        arrow.setLength(10)
        painter.drawLine(arrow)

        if self.gray_reaction_rate is not None:
            painter.drawText(50, 110, str(self.gray_reaction_rate))

            pen.setColor(QColor('#b9c0bd'))
            painter.setPen(pen)

            painter.drawLine(30, 95, 110, 95)
            arrow = QLineF()
            arrow.setP1(QPointF(30, 95))
            arrow.setAngle(-45)
            arrow.setLength(10)
            painter.drawLine(arrow)
