from math import degrees

from PyQt5.QtCore import QRectF, QPointF, QLineF
from PyQt5.QtGui import QPen, QPainter, QFont, QColor
from PyQt5.QtWidgets import QGraphicsItem

from DSDVis.elements.element import Element
from DSDVis.utils.config import get_id, BOND_DIST, DOMAIN_LEN, TOEHOLD_LEN, get_vector_length, get_global_angle


class Domain(Element):
    def __init__(self, name, strand_id, bond, last, toehold):
        Element.__init__(self, get_id())

        self.name = name
        self.bond = bond  # bond id, -1 in the case of an unbounded domain
        self.strand_id = strand_id

        self.center = None
        self.direction = None
        if toehold:
            self.domain_len = TOEHOLD_LEN
        else:
            self.domain_len = DOMAIN_LEN

        self.last = last  # if the last in the strand
        self.goal_bond = None  # place of the center of the bounded domain

        self.loop = False

        self.flipped = False

        self.color = None

    def set_coordinates(self, center, direction):
        """
        Sets the center of the domain in the space with direction vector s.t.:
        domain start = center - direction
        domain end = center + direction
        :param center:
        :param direction:
        :return:
        """
        self.center = center[:]
        self.direction = direction[:]

        if self.bond != -1:
            self.set_goal()

    def set_goal(self):
        if not self.loop:
            if self.flipped is False:
                goal_vector = [self.direction[1], -self.direction[0]]
            else:
                goal_vector = [-self.direction[1], self.direction[0]]
            goal_length = get_vector_length(goal_vector)
            goal_vector = [goal_vector[0] * BOND_DIST / goal_length, goal_vector[1] * BOND_DIST / goal_length]
            goal = [self.center[0] + goal_vector[0], self.center[1] + goal_vector[1]]

            self.goal_bond = goal

        else:
            self.goal_bond = self.center

    def set_center(self, center):
        self.center = center[:]

    def set_direction(self, direction):
        self.direction = direction[:]

    def get_bond(self):
        return self.bond

    def get_center(self):
        return self.center

    def get_direction(self):
        return self.direction


class DomainGraphicsItem(QGraphicsItem):
    def __init__(self, domain, color, show_dot):
        QGraphicsItem.__init__(self, parent=None)

        self.domain = domain
        self.start = [self.domain.center[0] - self.domain.direction[0],
                      self.domain.center[1] - self.domain.direction[1]]
        self.end = [self.domain.center[0] + self.domain.direction[0], self.domain.center[1] + self.domain.direction[1]]

        self.color = color
        self.show_dot = show_dot

    # implementation of QGraphicsItem virtual methods

    def boundingRect(self):
        margin = 25
        left = min(self.start[0], self.end[0])
        right = max(self.start[0], self.end[0])
        up = max(self.start[1], self.end[1])
        down = min(self.start[1], self.end[1])

        if self.domain.goal_bond is not None:
            left = min(left, self.domain.goal_bond[0])
            right = max(right, self.domain.goal_bond[0])
            up = max(up, self.domain.goal_bond[1])
            down = min(down, self.domain.goal_bond[1])

        return QRectF(left - margin, - up - margin, right - left + 2 * margin, up - down + 2 * margin)

    def paint(self, painter, option, widget):
        pen = QPen()
        pen.setWidth(3)
        pen.setColor(QColor(self.color))
        painter.setPen(pen)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setFont(QFont('Arial', 10, 1))

        painter.drawLine(self.start[0], -self.start[1], self.end[0], -self.end[1])
        if self.domain.last:
            arrow = QLineF()
            arrow.setP1(QPointF(self.end[0], -self.end[1]))
            angle = degrees(get_global_angle(self.domain.direction))
            arrow.setAngle(angle - 135)
            arrow.setLength(10)
            painter.drawLine(arrow)
        if self.domain.goal_bond is not None and self.show_dot:
            painter.drawEllipse(self.domain.goal_bond[0], -self.domain.goal_bond[1], 3, 3)
        if self.domain.flipped is False:
            text_vector = [-self.domain.direction[1], self.domain.direction[0]]
        else:
            text_vector = [self.domain.direction[1], -self.domain.direction[0]]
        text_vector = [self.domain.center[0] + text_vector[0] * 20 / self.domain.domain_len,
                       self.domain.center[1] + text_vector[1] * 20 / self.domain.domain_len]
        pen.setColor(QColor(0, 0, 0))
        painter.setPen(pen)
        painter.drawText(text_vector[0] - 7, -text_vector[1] + 7, self.domain.name)
