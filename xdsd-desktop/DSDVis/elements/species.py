from collections import defaultdict

from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QGraphicsItemGroup

from DSDVis.elements.element import Element
from DSDVis.utils.config import get_id
from DSDVis.utils.pair_detection import set_domain_pairs
from DSDVis.utils.strand_modifier import set_loops_and_flip_domains


class Species(Element):
    def __init__(self, strands=[]):
        super().__init__(get_id())
        self.strands = strands[:]
        self.domain_pairs = defaultdict(list)
        self.crossing_bonds = defaultdict(list)
        self.pseudoknot = False
        self.render_height = None
        self.height_inc = None

    def get_strands(self):
        return self.strands

    def get_strand_by_id(self, id):
        for strand in self.strands:
            if strand.get_id() == id:
                return strand

    def flip_strands(self):
        for strand in self.strands:
            if strand.flipped:
                for domain in strand.get_domains():
                    # if the domain is paired and has not been yet flipped (in the case both domains are in the flipped
                    # strands)
                    if domain.get_bond() != -1 and not domain.flipped:
                        # choose the current domain from the pair
                        if domain == self.domain_pairs[domain.get_bond()][0]:
                            # flip the current domain and keep the same bounding site on the other paired domain
                            # (heuristic)
                            self.domain_pairs[domain.get_bond()][0].flipped = not self.domain_pairs[domain.get_bond()][
                                0].flipped
                            self.domain_pairs[domain.get_bond()][1].flipped = self.domain_pairs[domain.get_bond()][
                                0].flipped
                        else:
                            self.domain_pairs[domain.get_bond()][1].flipped = not self.domain_pairs[domain.get_bond()][
                                1].flipped
                            self.domain_pairs[domain.get_bond()][0].flipped = self.domain_pairs[domain.get_bond()][
                                1].flipped

    def set_strands(self, new_strands, flip_domains):
        self.strands = new_strands
        set_domain_pairs(self)
        self.flip_strands()
        set_loops_and_flip_domains(self, flip_domains)

    def set_strands_and_crossing(self, new_strands, new_crossing_bonds, flip_domains):
        self.crossing_bonds = new_crossing_bonds
        self.set_strands(new_strands, flip_domains)

    def get_crossing_bonds(self):
        return self.crossing_bonds

    def get_domains(self):
        domains = []
        for strand in self.strands:
            for domain in strand.get_domains():
                domains.append(domain)

        return domains

    def get_hinges(self):
        hinges = []
        for strand in self.strands:
            for hinge in strand.get_hinges():
                hinges.append(hinge)

        return hinges

    def get_bonds(self):
        bonds = []
        [bonds.append(bond) for strand in self.strands for bond in strand.get_bonds()]

        return bonds

    def get_domain_hinges(self, domain):
        """
        :param domain:
        :return: List of the hinges adjacent to the domain
        """
        hinges = self.get_hinges()
        for idx in range(len(hinges)):
            if hinges[idx].next_domain is not None and hinges[idx].get_next_domain().get_id() == domain.get_id():
                return [hinges[idx], hinges[idx + 1]]
        return None

    def get_domain_pairs(self):
        return self.domain_pairs

    def get_bond_id(self, bond_name):
        if bond_name == -1:
            return -1
        return list(self.domain_pairs.keys()).index(bond_name)


class SpeciesGraphicsItem(QGraphicsItemGroup):
    def __init__(self, name):
        QGraphicsItemGroup.__init__(self, parent=None)
        self.name = name

    def boundingRect(self):
        rect = super().boundingRect()
        margin = 10
        return QRectF(rect.left() - margin - 56, rect.top() - margin - 14, rect.width() + margin + 56,
                      rect.height() + margin + 14)

    def paint(self, painter, option, widget):
        painter.setFont(QFont('Arial', 14, 1))
        x = self.boundingRect().left()
        y = self.boundingRect().top() + 16
        painter.drawText(int(x), int(y), self.name)
