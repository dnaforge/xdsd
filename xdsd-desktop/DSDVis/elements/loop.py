from math import degrees, sin, cos, radians

from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QPen, QPainterPath, QPainter, QFont, QColor
from PyQt5.QtWidgets import QGraphicsItem
from numpy import dot

from DSDVis.elements.element import Element
from DSDVis.utils.config import get_loop_radius, euclidean_dist, DOMAIN_LEN, get_angle, get_global_angle, \
    get_vector_length, get_angle_negative


class Loop(Element):
    def __init__(self, domains):
        self.domains = domains[:]
        self.n = len(self.domains)

        self.r = None
        self.start = None
        self.end = None

        self.domain_len = DOMAIN_LEN    # initial gap between ends
        self.loop_len = sum(domain.domain_len for domain in self.domains)

        self.mass_center = None
        self.flipped = False

        self.loop_center = None
        self.start_angle = None
        self.sweeping_angle = None

    def get_domains(self):
        return self.domains

    def flip_loop(self):
        self.flipped = not self.flipped
        self.r = get_loop_radius(self.n, euclidean_dist(self.start, self.end))
        self.mass_center = None

        self.get_loop_parameters()

        self.place_domains()

    def set_ends(self, start, end):
        self.start = start[:]
        self.end = end[:]
        self.r = get_loop_radius(self.n, euclidean_dist(self.start, self.end))
        self.mass_center = None

        self.get_loop_parameters()

        self.place_domains()

    def get_loop_parameters(self):
        center = [self.start[0] + (self.end[0] - self.start[0]) / 2,
                  self.start[1] + (self.end[1] - self.start[1]) / 2]
        chord_direction = [self.end[0] - self.start[0], self.end[1] - self.start[1]]

        if self.flipped is False:
            vector = [-chord_direction[1], chord_direction[0]]  # vector towards the center of the loop
        else:
            vector = [chord_direction[1], -chord_direction[0]]  # vector towards the center of the loop
        vector_length = get_vector_length(vector)

        factor = 1
        dist = euclidean_dist(self.start, center)
        if self.r < dist:
            self.r = dist ** 2 / self.r
            self.mass_center = center
            factor = -1

        offset = (self.r ** 2 - euclidean_dist(self.start, center) ** 2) ** 0.5
        vector = [vector[0] * offset / vector_length, vector[1] * offset / vector_length]
        self.loop_center = [center[0] + factor * vector[0], center[1] + factor * vector[1]]

        if self.mass_center is None:
            self.mass_center = self.loop_center

        if self.flipped is False:
            center_to_start = [self.start[0] - self.loop_center[0], self.start[1] - self.loop_center[1]]
            center_to_end = [self.end[0] - self.loop_center[0], self.end[1] - self.loop_center[1]]
        else:
            center_to_start = [self.end[0] - self.loop_center[0], self.end[1] - self.loop_center[1]]
            center_to_end = [self.start[0] - self.loop_center[0], self.start[1] - self.loop_center[1]]
        self.sweeping_angle = degrees(get_angle(center_to_end, center_to_start))
        self.start_angle = degrees(get_global_angle(center_to_start))

    def place_domains(self):
        inc_angle = self.sweeping_angle / self.n
        angle = self.start_angle
        prev_center = self.start
        for domain in self.domains:
            center_angle = radians(angle - inc_angle / 2)
            x = self.loop_center[0] + self.r * cos(center_angle)
            y = self.loop_center[1] + self.r * sin(center_angle)
            domain.set_coordinates([x, y], [x - prev_center[0], y - prev_center[1]])
            prev_center = [x, y]

            angle -= inc_angle


class LoopGraphicsItem(QGraphicsItem):
    def __init__(self, loop, prev_domain, next_domain, pseudoknot, color):
        QGraphicsItem.__init__(self, parent=None)

        self.loop = loop
        self.color = color

        # LOOP FLIPPING
        start_to_end = [self.loop.end[0] - self.loop.start[0], self.loop.end[1] - self.loop.start[1]]
        normal = [start_to_end[0] / get_vector_length(start_to_end),
                  start_to_end[1] / get_vector_length(start_to_end)]

        prev_domain_direction = [prev_domain.direction[0],
                                 prev_domain.direction[1]]
        first_loop_domain_direction = [
            self.loop.get_domains()[0].center[0] - self.loop.start[0],
            self.loop.get_domains()[0].center[1] - self.loop.start[1]
        ]
        # reflection formula:
        # r = -d - 2(d (dot) n) * n

        first_reflection = [-first_loop_domain_direction[0] - 2 * dot(
            [-first_loop_domain_direction[0], -first_loop_domain_direction[1]], normal) * normal[0],
                            -first_loop_domain_direction[1] - 2 * dot(
                                [-first_loop_domain_direction[0], -first_loop_domain_direction[1]], normal) * normal[1]]

        next_domain_direction = [-next_domain.direction[0],
                                 -next_domain.direction[1]]
        last_loop_domain_direction = [
            self.loop.get_domains()[-1].center[0] - self.loop.end[0],
            self.loop.get_domains()[-1].center[1] - self.loop.end[1]
        ]
        last_reflection = [
            -last_loop_domain_direction[0] - 2 * dot([-last_loop_domain_direction[0], -last_loop_domain_direction[1]],
                                                     normal) * normal[0],
            -last_loop_domain_direction[1] - 2 * dot([-last_loop_domain_direction[0], -last_loop_domain_direction[1]],
                                                     normal) * normal[1]]

        first_angle = abs(get_angle_negative(first_loop_domain_direction, prev_domain_direction))
        first_angle_reflection = abs(get_angle_negative(first_reflection, prev_domain_direction))

        last_angle = abs(get_angle_negative(next_domain_direction, last_loop_domain_direction))
        last_angle_reflection = abs(get_angle_negative(next_domain_direction, last_reflection))

        if pseudoknot and True:
            if first_angle > first_angle_reflection and last_angle > last_angle_reflection:
                self.loop.flip_loop()

    def boundingRect(self):
        return QRectF(self.loop.loop_center[0] - self.loop.r, -self.loop.loop_center[1] - self.loop.r, 2 * self.loop.r,
                      2 * self.loop.r)

    def paint(self, painter, option, widget):
        pen = QPen()
        pen.setWidth(3)
        pen.setColor(QColor(self.color))
        painter.setPen(pen)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setFont(QFont('Arial', 10, 1))

        rect = QRectF(self.loop.loop_center[0] - self.loop.r, -self.loop.loop_center[1] - self.loop.r, 2 * self.loop.r,
                      2 * self.loop.r)
        path = QPainterPath()

        if self.loop.flipped is False:
            path.moveTo(self.loop.start[0], -self.loop.start[1])
        else:
            path.moveTo(self.loop.end[0], -self.loop.end[1])

        inc_angle = self.loop.sweeping_angle / self.loop.n
        angle = self.loop.start_angle

        for domain in self.loop.domains:
            path.arcTo(rect, angle, -inc_angle)
            painter.drawPath(path)

            text_vector = [-domain.direction[1], domain.direction[0]]
            text_vector = [domain.center[0] + text_vector[0] * 20 / domain.domain_len,
                           domain.center[1] + text_vector[1] * 20 / domain.domain_len]
            pen.setColor(QColor(0, 0, 0))
            painter.setPen(pen)
            painter.drawText(text_vector[0] - 7, -text_vector[1] + 7, domain.name)
            pen.setColor(QColor(self.color))
            painter.setPen(pen)

            angle -= inc_angle

        # draw the connection between loop ends
        # pen = QPen(Qt.DashLine)
        # painter.setPen(pen)
        # painter.drawLine(self.loop.start[0], -self.loop.start[1], self.loop.end[0], -self.loop.end[1])
