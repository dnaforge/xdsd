from src.elements.element import Element
from src.utils.config import get_id


class Strand(Element):
    """
    Represents the Strand concept in DSDPy. Holds information on all the domains and pairings in this strand.
    """

    def __init__(self, domains=[]):
        super().__init__(get_id())
        self.domains = domains[:]

    def add_domain(self, domain):
        self.domains.append(domain)

    def set_domains(self, domains):
        self.domains = domains[:]
        # self.max_degree = (max(self.domains, key=lambda x: x.degree)).degree

    def get_bonds(self):
        bonds = []
        [bonds.append(domain.bond) for domain in self.domains if domain.__class__.__name__ != 'Loop']

        return bonds

    def get_domains(self):
        return self.domains
