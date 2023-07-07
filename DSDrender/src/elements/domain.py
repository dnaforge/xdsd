from math import degrees

from PyQt5.QtCore import QRectF, QPointF, QLineF, Qt
from PyQt5.QtGui import QPen, QPainter, QFont, QColor
from PyQt5.QtWidgets import QGraphicsItem

from src.elements.element import Element
from src.utils.config import get_id, DOMAIN_LEN, TOEHOLD_LEN, get_vector_length, get_global_angle


class Domain(Element):
    """
    Represents a DSDPy Domain, rendered ad a straight line/covalent bond.
    """

    def __init__(self, name, strand_id, bond, first, last, toehold):
        super().__init__(get_id())

        self.name = name
        self.bond = str(bond)  # bond id, -1 in the case of an unbounded domain
        self.strand_id = strand_id
        self.toehold = toehold

        if self.toehold:
            self.domain_len = TOEHOLD_LEN
            self.bond += "^"
        else:
            self.domain_len = DOMAIN_LEN

        self.first = first
        self.last = last  # if the last in the strand
        self.loop = False
        self.color = None
        self.bond_target_vector = None

    def get_bond(self):
        return self.bond

    def get_name_stem(self):
        pair_idx = self.name.find('*')
        if pair_idx != -1:
            return self.name[:pair_idx]
        return self.name


class DomainGraphicsItem(QGraphicsItem):
    """
    Graphical representation of the covalent bond.
    """

    def __init__(self, start, end, color, name, last):
        QGraphicsItem.__init__(self, parent=None)

        self.start = start
        self.end = end
        self.dir = [self.end[0] - self.start[0], self.end[1] - self.start[1]]
        dir_len = get_vector_length(self.dir)
        self.dir = [self.dir[0] / dir_len, self.dir[1] / dir_len]
        self.color = color
        self.name = name
        self.last = last

    # implementation of QGraphicsItem virtual methods

    def boundingRect(self):
        margin = 20
        left = min(self.start[0], self.end[0])
        right = max(self.start[0], self.end[0])
        up = min(self.start[1], self.end[1])
        down = max(self.start[1], self.end[1])

        return QRectF(left - margin, up - margin, right - left + 2 * margin, down - up + 2 * margin)

    def paint(self, painter, option, widget):
        pen = QPen()
        pen.setWidth(4)
        pen.setColor(QColor(self.color))
        painter.setPen(pen)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setFont(QFont('Arial', 17, QFont.DemiBold))

        painter.drawLine(self.start[0], self.start[1], self.end[0], self.end[1])
        if self.last:
            arrow = QLineF()
            arrow.setP1(QPointF(self.end[0], self.end[1]))
            angle = degrees((get_global_angle(self.dir)))
            arrow.setAngle(angle - 135)
            arrow.setLength(10)
            painter.drawLine(arrow)
        text_vector = [(self.start[0] + self.end[0]) / 2,
                       (self.start[1] + self.end[1]) / 2]
        pen.setColor(QColor(0, 0, 0))
        painter.setPen(pen)
        painter.drawText(text_vector[0] - 15, text_vector[1] + 15, self.name)


class BondGraphicsItem(QGraphicsItem):
    """
    Graphical representation of the hydrogen bond between domains.
    """

    def __init__(self, domain1, domain2, name):
        QGraphicsItem.__init__(self, parent=None)

        self.start = [(domain1[0][0] + domain1[1][0]) / 2, (domain1[0][1] + domain1[1][1]) / 2]
        self.end = [(domain2[0][0] + domain2[1][0]) / 2, (domain2[0][1] + domain2[1][1]) / 2]
        # self.start = domain1
        # self.end = domain2
        self.name = name

    # implementation of QGraphicsItem virtual methods

    def boundingRect(self):
        left = min(self.start[0], self.end[0])
        right = max(self.start[0], self.end[0])
        up = min(self.start[1], self.end[1])
        down = max(self.start[1], self.end[1])

        return QRectF(left, up, right - left, down - up)

    def paint(self, painter, option, widget):
        painter.setPen(QPen(Qt.black, 1, Qt.DashLine, Qt.RoundCap, Qt.RoundJoin))
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setFont(QFont('Arial', 17, QFont.DemiBold))

        painter.drawLine(self.start[0], self.start[1], self.end[0], self.end[1])
        text_vector = [(self.start[0] + self.end[0]) / 2,
                       (self.start[1] + self.end[1]) / 2]
        painter.setPen(QPen(Qt.black, 1))
        painter.drawText(text_vector[0] - 15, text_vector[1] + 15, self.name)
