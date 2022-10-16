from collections import deque, defaultdict
from copy import deepcopy
from itertools import permutations, combinations


def get_permutation(species, permute, flip_strands, flip_domains):
    """
    Sets the strands of the species in an order which minimizes the required number of flipped domains

    :param species: Species object
    :param permute: Boolean flag set in the ui, denotes if strands should be permuted
    :param flip_strands: Boolean flag set in the ui, denotes if strands should be flipped
    :param flip_domains: Boolean flag set in the ui, denotes if domains should be should be flipped
    :return: True if non crossing permutation is found, False otherwise
    """
    strands = species.get_strands()

    if permute:
        all_permutations = list(permutations(strands))  # return all the permutations of strands in a species
        min_flips = 99999
        min_crossings = 99999

        # check all permutations without any flipping (non-pseudoknot cases)
        for p in all_permutations:
            flips, crossings, crossing_bonds = check_permutation(species, p)
            if flips == 0:
                species.set_strands(deepcopy(p), flip_domains)
                return True
            else:
                if crossings < min_crossings or (crossings == min_crossings and flips < min_flips):
                    min_flips = flips
                    min_crossings = crossings
                    final_strands = deepcopy(p)
                    final_crossing = deepcopy(species.crossing_bonds)

                species.crossing_bonds = defaultdict(list)

        # check all the permutations with flipping of the strands
        if flip_strands:
            for p in all_permutations:
                for i in range(1, len(strands) // 2 + 1):
                    strands_to_flip_list = list(combinations(range(len(strands)), i))
                    for strands_to_flip in strands_to_flip_list:
                        for strand_idx in strands_to_flip:
                            p[strand_idx].flipped = True

                        flips, crossings, crossing_bonds = check_permutation(species, p)
                        if flips == 0:
                            species.pseudoknot = True
                            species.set_strands(deepcopy(p), flip_domains)
                            return True
                        else:
                            # if flips < min_flips or (flips == min_flips and crossings < min_crossings):
                            if crossings < min_crossings or (crossings == min_crossings and flips < min_flips):
                                min_flips = flips
                                min_crossings = crossings
                                final_strands = deepcopy(p)
                                final_crossing = deepcopy(species.crossing_bonds)

                            for strand_idx in strands_to_flip:  # reset the strands
                                p[strand_idx].flipped = False
                            species.crossing_bonds = defaultdict(list)

        # pseudoknotted case
        species.pseudoknot = True
        species.set_strands_and_crossing(final_strands, final_crossing, flip_domains)

        return False
    else:
        flips, crossings, crossing_bonds = check_permutation(species, strands)
        min_flips = flips
        min_crossings = crossings
        final_strands = deepcopy(strands)
        final_crossing = deepcopy(species.crossing_bonds)

        # check this single permutations with flipping of the strands
        if flip_strands:
            for i in range(1, len(strands) // 2 + 1):
                strands_to_flip_list = list(combinations(range(len(strands)), i))
                for strands_to_flip in strands_to_flip_list:
                    for strand_idx in strands_to_flip:
                        strands[strand_idx].flipped = True

                    flips, crossings, crossing_bonds = check_permutation(species, strands)
                    if flips == 0:
                        species.pseudoknot = True
                        species.set_strands(deepcopy(strands), flip_domains)
                        return True
                    else:
                        if flips < min_flips or (flips == min_flips and crossings < min_crossings):
                            min_flips = flips
                            min_crossings = crossings
                            final_strands = deepcopy(strands)
                            final_crossing = deepcopy(species.crossing_bonds)

                        for strand_idx in strands_to_flip:  # reset the strands
                            strands[strand_idx].flipped = False
                        species.crossing_bonds = defaultdict(list)

        if min_crossings != 0:
            species.pseudoknot = True
        species.set_strands_and_crossing(final_strands, final_crossing, flip_domains)
        return True


def check_permutation(species, strands):
    """
    Checks if this permutation of strands does not result in crossings in a circle diagram

    :param species: Species object
    :param strands: Strand object to be checked
    :return: Number of domain flips, number of crossings, crossing pairs
    """
    stack = deque()
    for strand in strands:
        strand_bonds = []
        [strand_bonds.append(bond) for bond in strand.get_bonds() if bond != -1]
        if strand.flipped:
            strand_bonds.reverse()

        for bond in strand_bonds:  # traverse the bonds and use stack to check for crossings
            stack.append(bond)
            for j in range(len(stack) - 2, -1, -1):  # look for complementary bond in the stack
                if stack[j] == bond:
                    crossings_number = len(stack) - 2 - j
                    stack.pop()
                    stack.remove(bond)
                    for k in range(len(stack) - 1, len(stack) - 1 - crossings_number, -1):  # add crossing bonds
                        species.crossing_bonds[bond].append(stack[k])  # (outside, inside)
                    break

    crossings_count = 0
    for crossing in species.crossing_bonds.values():
        crossings_count += len(crossing)

    return len(species.crossing_bonds.keys()), crossings_count, species.get_crossing_bonds()
