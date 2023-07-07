from math import degrees

from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QPen, QPainterPath, QPainter, QFont, QColor
from PyQt5.QtWidgets import QGraphicsItem
from numpy import dot

from src.elements.element import Element
from src.utils.config import get_loop_radius, euclidean_dist, DOMAIN_LEN, get_angle, get_global_angle, \
    get_vector_length, get_angle_negative, get_id, get_color


class Loop(Element):
    """
    Represents a set of unpaired domains between paired domains.
    """

    def __init__(self, domains):
        super().__init__(get_id())

        self.domains = domains[:]
        self.n = len(self.domains)
        self.strand_id = domains[0].strand_id
        self.bond = -2
        self.name = ''
        self.first = self.last = False

        self.domain_len = DOMAIN_LEN  # initial gap between ends
        self.loop_len = sum(domain.domain_len for domain in self.domains)

    def get_domains(self):
        return self.domains


class LoopGraphicsItem(QGraphicsItem):
    """
    Graphical representation of the Loop class.
    """

    # TODO cleanup
    def __init__(self, loop, start, end, prev, next):
        QGraphicsItem.__init__(self, parent=None)

        self.loop = loop
        self.start = start
        self.end = end
        self.r = get_loop_radius(self.loop.n, euclidean_dist(self.start, self.end))

        center = [(self.end[0] + self.start[0]) / 2,
                  (self.end[1] + self.start[1]) / 2]

        chord_direction = [self.end[0] - self.start[0], self.end[1] - self.start[1]]

        vector = [-chord_direction[1], chord_direction[0]]
        self.loop_center = [center[0] + vector[0], center[1] + vector[1]]

        # LOOP FLIPPING
        normal = [chord_direction[0] / get_vector_length(chord_direction),
                  chord_direction[1] / get_vector_length(chord_direction)]

        prev_domain_direction = [self.start[0] - prev[0],
                                 self.start[1] - prev[1]]
        first_loop_domain_direction = [
            self.loop_center[0] - self.start[0],
            self.loop_center[1] - self.start[1]
        ]
        # reflection formula:
        # r = -d - 2(d (dot) n) * n

        first_reflection = [-first_loop_domain_direction[0] - 2 * dot(
            [-first_loop_domain_direction[0], -first_loop_domain_direction[1]], normal) * normal[0],
                            -first_loop_domain_direction[1] - 2 * dot(
                                [-first_loop_domain_direction[0], -first_loop_domain_direction[1]], normal) * normal[1]]

        next_domain_direction = [self.end[0] - next[0],
                                 self.end[1] - next[1]]
        last_loop_domain_direction = [
            self.loop_center[0] - self.end[0],
            self.loop_center[1] - self.end[1]
        ]
        last_reflection = [
            -last_loop_domain_direction[0] - 2 * dot([-last_loop_domain_direction[0], -last_loop_domain_direction[1]],
                                                     normal) * normal[0],
            -last_loop_domain_direction[1] - 2 * dot([-last_loop_domain_direction[0], -last_loop_domain_direction[1]],
                                                     normal) * normal[1]]

        first_angle = abs(get_angle_negative(prev_domain_direction, first_loop_domain_direction))
        first_angle_reflection = abs(get_angle_negative(prev_domain_direction, first_reflection))

        last_angle = abs(get_angle_negative(next_domain_direction, last_loop_domain_direction))
        last_angle_reflection = abs(get_angle_negative(next_domain_direction, last_reflection))

        if first_angle - first_angle_reflection + last_angle - last_angle_reflection > 0:
            self.flip = True
        else:
            self.flip = False
        # END LOOP FLIPPING

        if self.flip is False:
            vector = [-chord_direction[1], chord_direction[0]]
        else:
            vector = [chord_direction[1], -chord_direction[0]]

        vector_length = get_vector_length(vector)

        factor = 1
        dist = euclidean_dist(self.start, center)
        if self.r < dist:
            self.r = dist ** 2 / self.r
            factor = -1

        offset = (self.r ** 2 - euclidean_dist(self.start, center) ** 2) ** 0.5
        vector = [vector[0] * offset / vector_length, vector[1] * offset / vector_length]
        self.loop_center = [center[0] + factor * vector[0], center[1] + factor * vector[1]]

        if self.flip is False:
            center_to_start = [self.start[0] - self.loop_center[0], self.start[1] - self.loop_center[1]]
            center_to_end = [self.end[0] - self.loop_center[0], self.end[1] - self.loop_center[1]]
        else:
            center_to_start = [self.end[0] - self.loop_center[0], self.end[1] - self.loop_center[1]]
            center_to_end = [self.start[0] - self.loop_center[0], self.start[1] - self.loop_center[1]]

        self.sweeping_angle = degrees(get_angle(center_to_end, center_to_start))
        self.start_angle = degrees(get_global_angle(center_to_start))

    def boundingRect(self):
        margin = 20
        return QRectF(self.loop_center[0] - self.r - margin, self.loop_center[1] - self.r - margin,
                      2 * self.r + 2 * margin,
                      2 * self.r + 2 * margin)

    def paint(self, painter, option, widget):
        pen = QPen()
        pen.setWidth(4)
        pen.setColor(QColor(get_color(-1)))
        painter.setPen(pen)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setFont(QFont('Arial', 17, QFont.DemiBold))

        rect = QRectF(self.loop_center[0] - self.r, self.loop_center[1] - self.r, 2 * self.r, 2 * self.r)
        path = QPainterPath()

        if self.flip is False:
            path.moveTo(self.start[0], self.start[1])
        else:
            path.moveTo(self.end[0], self.end[1])

        inc_angle = self.sweeping_angle / self.loop.n
        angle = self.start_angle
        prev_position = path.currentPosition()

        for domain in self.loop.domains:
            path.arcTo(rect, angle, inc_angle)
            painter.drawPath(path)
            curr_position = path.currentPosition()

            text_vector = [(prev_position.x() + curr_position.x()) / 2, (prev_position.y() + curr_position.y()) / 2]
            painter.setPen(QPen(Qt.black, 4))
            painter.drawText(text_vector[0] - 7, text_vector[1] + 7, domain.name)
            painter.setPen(QPen(QColor(get_color(-1)), 4))

            angle += inc_angle
            prev_position = curr_position
