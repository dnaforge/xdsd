def get_element(id):
    return Element.elements.get(int(id), None)


def clear_elements():
    Element.elements = {}


class Element:
    """
    Base class for all the elements necessary for rendering: Species, Strand, Domain, Loop, Overhang
    """

    elements = {}

    def __init__(self, id):
        self._id = id
        Element.elements[self._id] = self

    def get_id(self):
        return self._id
