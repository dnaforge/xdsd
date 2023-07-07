from src.elements.loop import Loop
from src.elements.overhang import Overhang


def set_loops_and_overhangs(species):
    """
    Finds the loops and overhangs in a species and creates classes for them

    :param species: Species object
    :return:
    """
    for strand in species.get_strands():
        bonds = strand.get_bonds()
        old_domains = strand.get_domains()[:]  # only straight domains

        new_domains = []  # straight domains and loops
        new_inside_domains = []
        start = 0
        end = len(bonds) - 1
        oh_begin = []
        oh_end = []

        while start <= end and bonds[start][:2] == "-1":  # delete the overhangs in the beginning
            oh_begin.append(old_domains[start])  # add straight domains at the beginning
            start += 1
        if len(oh_begin) > 0:
            if start > end:
                new_domains.append(Overhang(oh_begin, True, True))
            else:
                oh_begin.reverse()
                new_domains.append(Overhang(oh_begin, True, False))

        while bonds[end][:2] == "-1" and end >= start:  # delete the overhangs in the end
            end -= 1

        if start <= end:
            end += 1
            bonds = bonds[start:end]

            i = 0

            while i < len(bonds):
                if bonds[i][:2] == "-1":
                    j = i + 1
                    old_domains[start + i].loop = True

                    while bonds[j][:2] == "-1":
                        old_domains[start + j].loop = True
                        j += 1

                    loop = Loop(old_domains[start + i:start + j])
                    new_inside_domains.append(loop)
                    i = j - 1
                else:
                    new_inside_domains.append(old_domains[start + i])
                i += 1

            [new_domains.append(domain) for domain in new_inside_domains]
        else:
            end += 1

        [oh_end.append(old_domains[k]) for k in range(end, len(old_domains))]  # add straight domains at the end
        if len(oh_end) > 0:
            new_domains.append(Overhang(oh_end, False, True))
        strand.set_domains(new_domains)
