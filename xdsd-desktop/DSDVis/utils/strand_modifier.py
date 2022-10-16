from DSDVis.elements.loop import Loop


def set_loops_and_flip_domains(species, flip_domains):
    """
    Finds the loops in a strand and flips the domains

    :param species: Species object
    :param flip_domains: Boolean flag set in the ui, denotes if the domains should be flipped
    :return:
    """
    domain_pairs = species.get_domain_pairs()
    crossings = species.get_crossing_bonds()
    for strand in species.get_strands():
        bonds = strand.get_bonds()
        old_domains = strand.get_domains()[:]  # only straight domains

        if strand.flipped is True:
            bonds.reverse()
            old_domains.reverse()

        new_domains = []  # straight domains and loops
        new_inside_domains = []
        start = 0
        end = len(bonds) - 1

        while bonds[start] == -1 and start < end:  # delete the overhangs in the beginning
            new_domains.append(old_domains[start])  # add straight domains at the beginning
            start += 1

        while bonds[end] == -1 and end > start:  # delete the overhangs in the end
            end -= 1

        if start != end:
            end += 1
            bonds = bonds[start:end]

            i = 0

            while i < len(bonds):
                if bonds[i] == -1:
                    j = i + 1
                    old_domains[start + i].loop = True

                    while bonds[j] == -1:
                        old_domains[start + j].loop = True
                        j += 1

                    loop = Loop(old_domains[start + i:start + j])
                    new_inside_domains.append(loop)
                    i = j - 1
                else:
                    if flip_domains:
                        flip_pairings(crossings, bonds[i], domain_pairs)
                    new_inside_domains.append(old_domains[start + i])
                i += 1

            if strand.flipped is True:
                new_inside_domains.reverse()
            [new_domains.append(domain) for domain in new_inside_domains]

            [new_domains.append(old_domains[k]) for k in
             range(end, len(old_domains))]  # add straight domains at the end
            strand.set_domains(new_domains)


def flip_pairings(crossings, bond, domain_pairs):
    if bond in crossings:
        for inside_bond in crossings[bond]:
            domain_pairs[inside_bond][0].flipped = not domain_pairs[inside_bond][0].flipped
            domain_pairs[inside_bond][1].flipped = not domain_pairs[inside_bond][1].flipped

            for inside_bond_list in crossings.values():
                try:
                    inside_bond_list.remove(inside_bond)
                except ValueError:
                    pass
            if inside_bond in crossings:
                crossings[inside_bond] = list()
