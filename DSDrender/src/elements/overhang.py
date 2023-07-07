from math import degrees

from PyQt5.QtCore import QRectF, QPointF, QLineF, Qt
from PyQt5.QtGui import QPen, QPainter, QFont, QColor
from PyQt5.QtWidgets import QGraphicsItem

from src.elements.element import Element
from src.utils.config import get_id, get_global_angle, get_color, DOMAIN_LEN, TOEHOLD_LEN


class Overhang(Element):
    """
    Represents a set of unpaired domains in the beginning or the end of the strand.
    """

    def __init__(self, domains, first, last):
        super().__init__(get_id())

        self.domains = domains[:]
        self.n = len(self.domains)
        self.strand_id = domains[0].strand_id
        self.domain_len = 0
        for domain in self.domains:
            self.domain_len += domain.domain_len
        self.bond = -1
        self.name = ''
        self.first = first
        self.last = last


class OverhangGraphicsItem(QGraphicsItem):
    """
    Graphical representation of the Overhang class.
    """

    def __init__(self, oh, start, end):
        QGraphicsItem.__init__(self, parent=None)

        self.oh = oh
        self.start = start
        self.end = end
        self.color = get_color(-1)

        line = QLineF()
        if self.oh.first:
            line.setP1(QPointF(self.end[0], self.end[1]))
            self.dir = [self.start[0] - self.end[0], self.start[1] - self.end[1]]
        else:
            line.setP1(QPointF(self.start[0], self.start[1]))
            self.dir = [self.end[0] - self.start[0], self.end[1] - self.start[1]]
        self.angle = degrees((get_global_angle(self.dir)))
        line.setAngle(self.angle)
        line.setLength(self.oh.domain_len)
        self.p1 = line.p1()
        self.p2 = line.p2()

    # implementation of QGraphicsItem virtual methods

    def boundingRect(self):
        margin = 20
        left = min(self.p1.x(), self.p2.x())
        right = max(self.p1.x(), self.p2.x())
        up = min(self.p1.y(), self.p2.y())
        down = max(self.p1.y(), self.p2.y())

        return QRectF(left - margin, up - margin, right - left + 2 * margin, down - up + 2 * margin)

    def paint(self, painter, option, widget):
        painter.setPen(QPen(QColor(self.color), 4))
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setFont(QFont('Arial', 17, QFont.DemiBold))

        # starting point from previous domain/strand beginning
        # line = QLineF()
        # line.setP1(self.p1)
        # line.setAngle(self.angle)
        # line.setLength(DOMAIN_LEN)

        new_p1 = self.p1

        for domain in self.oh.domains:
            line = QLineF()
            line.setP1(new_p1)
            line.setAngle(self.angle)
            if domain.toehold:
                line.setLength(TOEHOLD_LEN)
            else:
                line.setLength(DOMAIN_LEN)

            painter.setPen(QPen(QColor(self.color), 4))
            new_p1 = line.p2()
            painter.drawLine(line)
            painter.setPen(QPen(Qt.black, 4))
            painter.drawText((line.x1() + line.x2()) / 2 + 7, (line.y1() + line.y2()) / 2 + 7, domain.name)
            # line = QLineF()
            # line.setP1(new_p1)
            # line.setAngle(self.angle)
            # if domain.toehold:
            #     line.setLength(TOEHOLD_LEN)
            # else:
            #     line.setLength(DOMAIN_LEN)

        if self.oh.last:
            painter.setPen(QPen(QColor(self.color), 4))
            arrow = QLineF()
            arrow.setP1(new_p1)
            arrow.setAngle(self.angle - 135)
            arrow.setLength(10)
            painter.drawLine(arrow)
