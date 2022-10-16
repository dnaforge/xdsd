from math import cos, sin, radians

from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtWidgets import QGraphicsItem

from DSDVis.elements.element import Element
from DSDVis.utils.config import DOMAIN_LEN, get_id, get_vector_length, euclidean_dist


class Hinge(Element):
    def __init__(self, strand_id, position, prev_domain, next_domain):
        super().__init__(get_id())
        self.strand_id = strand_id
        self.prev_domain = prev_domain
        self.next_domain = next_domain
        self.position = position[:]
        self.new_position = None

    def move_first_hinge(self, move_vector):
        new_position = [self.position[0] + move_vector[0], self.position[1] + move_vector[1]]
        self.new_position = new_position[:]

        if self.prev_domain.__class__.__name__ == 'Loop':
            self.prev_domain.set_ends(self.prev_domain.start, self.new_position)
        elif self.next_domain.__class__.__name__ == 'Loop':
            self.next_domain.set_ends(self.new_position, self.next_domain.end)

    def move_hinge(self, old_move_position, new_move_position, anchor, side, factor):
        """
        Response move to the movement of the neighboring, leading hinge
        :param old_move_position: Old position of the leading hinge
        :param new_move_position: New position of the leading hinge
        :param anchor: Position of the anchor of the vector determining the new position
        :param side: 1 if this hinge is a next one with respect to the leading hinge,
                    -1 if it is the previous one
        :param factor: Multiplication factor determining the strength of the move
        :return:
        """
        move_vector = [factor * (new_move_position[0] - old_move_position[0]),
                       factor * (new_move_position[1] - old_move_position[1])]
        moved_position = [self.position[0] + move_vector[0], self.position[1] + move_vector[1]]
        move_vector = [moved_position[0] - anchor[0], moved_position[1] - anchor[1]]
        vector_length = get_vector_length(move_vector)

        if (side == 1 and self.prev_domain.__class__.__name__ != 'Loop') or \
                (side == -1 and self.next_domain.__class__.__name__ != 'Loop'):
            # if the domain closer to the leading hinge is not a part of a loop
            if side == 1:
                move_vector = [move_vector[0] * self.prev_domain.domain_len / vector_length, move_vector[1] * self.prev_domain.domain_len / vector_length]
            else:
                move_vector = [move_vector[0] * self.next_domain.domain_len / vector_length, move_vector[1] * self.next_domain.domain_len / vector_length]

            new_position = [anchor[0] + move_vector[0], anchor[1] + move_vector[1]]
            self.new_position = new_position[:]

            new_direction = [side * move_vector[0] / 2, side * move_vector[1] / 2]
            new_center = [anchor[0] + side * new_direction[0], anchor[1] + side * new_direction[1]]

            if side == 1:
                self.prev_domain.set_coordinates(new_center, new_direction)
                if self.next_domain.__class__.__name__ == 'Loop':
                    self.next_domain.set_ends(self.new_position, self.next_domain.end)
            else:
                self.next_domain.set_coordinates(new_center, new_direction)
                if self.prev_domain.__class__.__name__ == 'Loop':
                    self.prev_domain.set_ends(self.prev_domain.start, self.new_position)
        else:
            # if it is a part of a loop
            # check if the distance between the hinges does not exceed  the maximum
            if self.prev_domain.__class__.__name__ == 'Loop':
                max_gap_length = self.prev_domain.loop_len
            else:
                max_gap_length = self.next_domain.loop_len
            # shorten the vector if necessary
            if vector_length > max_gap_length:
                move_vector = [move_vector[0] * max_gap_length / vector_length,
                               move_vector[1] * max_gap_length / vector_length]

            new_position = [anchor[0] + move_vector[0], anchor[1] + move_vector[1]]
            self.new_position = new_position[:]

            if self.prev_domain.__class__.__name__ == 'Loop':
                self.prev_domain.set_ends(self.prev_domain.start, self.new_position)
            else:
                self.next_domain.set_ends(self.new_position, self.next_domain.end)

    def rotate(self, angle, pivot, side, anchor):
        angle = radians(angle)

        x = (self.position[0] - pivot[0]) * cos(angle) - (self.position[1] - pivot[1]) * sin(angle) + pivot[0]
        y = (self.position[0] - pivot[0]) * sin(angle) + (self.position[1] - pivot[1]) * cos(angle) + pivot[1]

        self.new_position = [x, y]

        move_vector = [x - anchor[0], y - anchor[1]]

        new_direction = [side * move_vector[0] / 2, side * move_vector[1] / 2]
        new_center = [anchor[0] + side * new_direction[0], anchor[1] + side * new_direction[1]]

        if (side == 1 and self.prev_domain.__class__.__name__ != 'Loop') or \
                (side == -1 and self.next_domain.__class__.__name__ != 'Loop'):
            # if the domain closer to the leading hinge is not a part of a loop
            if side == 1:
                self.prev_domain.set_coordinates(new_center, new_direction)
                if self.next_domain.__class__.__name__ == 'Loop':
                    self.next_domain.set_ends(self.new_position, self.next_domain.end)
            else:
                self.next_domain.set_coordinates(new_center, new_direction)
                if self.prev_domain.__class__.__name__ == 'Loop':
                    self.prev_domain.set_ends(self.prev_domain.start, self.new_position)
        else:
            # if it is a part of a loop
            if self.prev_domain.__class__.__name__ == 'Loop':
                self.prev_domain.set_ends(anchor, self.new_position)
            else:
                self.next_domain.set_ends(self.new_position, anchor)

    def get_next_center(self):
        return self.next_domain.get_center()

    def get_prev_center(self):
        return self.prev_domain.get_center()

    def set_new_position(self, position):
        self.new_position = position[:]

    def get_new_position(self):
        return self.new_position

    def set_position(self, position):
        self.position = position[:]

    def get_position(self):
        return self.position

    def get_strand_id(self):
        return self.strand_id

    def get_prev_domain(self):
        return self.prev_domain

    def get_next_domain(self):
        return self.next_domain


class HingeGraphicsItem(QGraphicsItem):
    def __init__(self, hinge):
        QGraphicsItem.__init__(self, parent=None)

        self.hinge = hinge

    def boundingRect(self):
        return QRectF(self.hinge.position[0] - 2, -self.hinge.position[1] - 2, self.hinge.position[0] + 2,
                      -self.hinge.position[1] + 2)

    def paint(self, painter, option, widget):
        painter.setBrush(Qt.black)
        painter.drawEllipse(self.hinge.position[0], -self.hinge.position[1], 4, 4)
