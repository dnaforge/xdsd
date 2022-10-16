from DSDVis.elements.element import Element
from DSDVis.elements.hinge import Hinge
from DSDVis.utils.config import get_id


class Strand(Element):
    def __init__(self, domains=[]):
        super().__init__(get_id())
        self.domains = domains[:]
        self.hinges = None
        self.flipped = False

    def add_domain(self, domain):
        self.domains.append(domain)

    def set_domains(self, domains):
        self.domains = domains[:]

    def get_bonds(self):
        bonds = []
        [bonds.append(domain.bond) for domain in self.domains if domain.__class__.__name__ != 'Loop']

        return bonds

    def get_domains(self):
        return self.domains

    def flip_domains(self):
        self.domains.reverse()

    def set_hinges(self):
        hinges = []
        hinges.append(Hinge(super().get_id(), [self.domains[0].center[0] - self.domains[0].direction[0],
                                               self.domains[0].center[1] - self.domains[0].direction[1]],
                            None, self.domains[0]))
        for i in range(1, len(self.domains)):
            # do not create hinges for domains with both ends in the loop
            if self.domains[i - 1].__class__.__name__ != 'Loop' or self.domains[i].__class__.__name__ != 'Loop':
                if self.domains[i - 1].__class__.__name__ == 'Loop':
                    position = self.domains[i - 1].end[:]
                elif self.domains[i].__class__.__name__ == 'Loop':
                    position = self.domains[i].start[:]
                else:
                    position = [self.domains[i].center[0] - self.domains[i].direction[0],
                                self.domains[i].center[1] - self.domains[i].direction[1]]

                hinges.append(Hinge(super().get_id(), position, self.domains[i - 1], self.domains[i]))

        hinges.append(
            Hinge(super().get_id(),
                  [self.domains[len(self.domains) - 1].center[0] + self.domains[len(self.domains) - 1].direction[0],
                   self.domains[len(self.domains) - 1].center[1] + self.domains[len(self.domains) - 1].direction[1]],
                  self.domains[len(self.domains) - 1], None))

        self.hinges = hinges

    def get_hinges(self):
        return self.hinges

    def get_hinge_neighbors(self, hinge):
        idx = self.hinges.index(hinge)
        prev = next = None
        if idx > 0:
            prev = self.hinges[idx - 1]
        if idx < len(self.hinges) - 1:
            next = self.hinges[idx + 1]

        return prev, next
