from collections import defaultdict

from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QGraphicsItemGroup

from src.elements.element import Element
from src.elements.graph import Graph
from src.elements.overhang import Overhang
from src.utils.config import get_id
from src.utils.pair_detection import set_domain_pairs
from src.utils.strand_modifier import set_loops_and_overhangs


class Species(Element):
    """
    Represents the Species concept in DSDPy. Holds information on all the strands, domains and pairings belonging to this species.
    """

    def __init__(self, name, strands=[]):
        super().__init__(get_id())
        self.name = name
        self.strands = strands[:]
        self.domain_pairs = defaultdict(list)
        self.crossing_bonds = defaultdict(list)
        self.pseudoknot = False
        self.render_height = None
        self.height_inc = None
        self.bond_colors = {}

        set_domain_pairs(self)

        set_loops_and_overhangs(self)
        self.graph = None

    def create_graph(self, signals, species_no, stop):
        self.graph = Graph(self, signals, species_no, stop)

    def get_strands(self):
        return self.strands

    def get_strand_by_id(self, id):
        for strand in self.strands:
            if strand.get_id() == id:
                return strand

    def get_domains(self):
        domains = []
        for strand in self.strands:
            for domain in strand.get_domains():
                domains.append(domain)

        return domains

    def get_bonds(self):
        bonds = []
        [bonds.append(bond) for strand in self.strands for bond in strand.get_bonds()]

        return bonds

    def get_domain_pairs(self):
        return self.domain_pairs

    def get_bond_id(self, bond_name):
        if bond_name[:2] == "-1":
            return -1
        return list(self.domain_pairs.keys()).index(bond_name)

    def is_overhang(self):
        return len(self.strands) == 1 and len(self.strands[0].domains) == 1 and type(
            self.strands[0].domains[0]) is Overhang


class SpeciesGraphicsItem(QGraphicsItemGroup):
    """
    Groups all the graphical representations of this species.
    """

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
