from math import exp

from src.utils.config import euclidean_dist, DOMAIN_LEN, TOEHOLD_LEN


def E(state, graph_domain_pairs, graph_loops, length_factor):
    """
    Energy function for a single species. Computes the following components:  deviation from the desired distance between the ends of each loop, deviation from the desired length of each domain, deviation from the correct placements of domains withing each pair.

    :param state: Tuple with G (graph) and GA (graph attributes)
    :param graph_domain_pairs: Dictionary with the pairs of domains and their constituent nodes
    :param graph_loops: Dictionary with the endings of the loops in the species and their constituent nodes
    :return: Sum of all the components and tuple with the constituent components (for plotting purposes)
    """
    G, GA = state
    diff = 0

    loops = 0
    domain_lengths = 0
    pairs = 0

    # loop gaps
    for name, loop in graph_loops.items():
        first_node = [GA.x(loop[0]), GA.y(loop[0])]
        second_node = [GA.x(loop[1]), GA.y(loop[1])]
        length = euclidean_dist(first_node, second_node)

        diff += length_factor * abs(DOMAIN_LEN - length)
        loops += length_factor * abs(DOMAIN_LEN - length)

    for bond, nodes in graph_domain_pairs.items():
        first_pair = nodes[0]
        second_pair = nodes[1]

        first_node1 = [GA.x(first_pair[0]), GA.y(first_pair[0])]
        first_node2 = [GA.x(first_pair[1]), GA.y(first_pair[1])]

        second_node2 = [GA.x(second_pair[1]), GA.y(second_pair[1])]
        second_node1 = [GA.x(second_pair[0]), GA.y(second_pair[0])]

        # domain lengths
        length1 = euclidean_dist(first_node1, first_node2)
        length2 = euclidean_dist(second_node1, second_node2)
        # diff += length_factor * (abs(DOMAIN_LEN - length1) + abs(DOMAIN_LEN - length2))

        if bond.find("^") != -1:
            diff += length_factor * (abs(TOEHOLD_LEN - length1) + abs(TOEHOLD_LEN - length2))
            domain_lengths += length_factor * (abs(TOEHOLD_LEN - length1) + abs(TOEHOLD_LEN - length2))
        else:
            diff += length_factor * (abs(DOMAIN_LEN - length1) + abs(DOMAIN_LEN - length2))
            domain_lengths += length_factor * (abs(DOMAIN_LEN - length1) + abs(DOMAIN_LEN - length2))

        # beginning and end of pair
        first_labels = str(GA.label(first_pair[0]))
        second_labels = str(GA.label(second_pair[1]))
        if 0 < len(first_labels) < 200 and 0 < len(second_labels) < 200:
            first_labels = first_labels.split(" ")
            second_labels = second_labels.split(" ")
            # search for the right connection
            for i in range(0, len(first_labels), 3):
                for j in range(0, len(second_labels), 3):
                    if first_labels[i] in second_labels[j]:
                        first_dx = float(first_labels[i + 1])
                        first_dy = float(first_labels[i + 2])

                        second_dx = float(second_labels[j + 1])
                        second_dy = float(second_labels[j + 2])

                        dist1 = euclidean_dist(second_node2, [first_node1[0] + first_dx, first_node1[1] + first_dy])
                        dist2 = euclidean_dist(first_node1, [second_node2[0] + second_dx, second_node2[1] + second_dy])

                        pairs += dist1
                        pairs += dist2

                        # diff += 2 * DOMAIN_LEN * exp(-dist1 / DOMAIN_LEN) + 1
                        # diff += 2 * DOMAIN_LEN * exp(-dist2 / DOMAIN_LEN) + 1

                        diff += dist1
                        diff += dist2

                        break

        # end and beginning of pair
        first_labels = str(GA.label(first_pair[1]))
        second_labels = str(GA.label(second_pair[0]))
        if 0 < len(first_labels) < 200 and 0 < len(second_labels) < 200:
            first_labels = first_labels.split(" ")
            second_labels = second_labels.split(" ")
            for i in range(0, len(first_labels), 3):
                for j in range(0, len(second_labels), 3):
                    if first_labels[i] in second_labels[j]:
                        first_dx = float(first_labels[i + 1])
                        first_dy = float(first_labels[i + 2])

                        second_dx = float(second_labels[j + 1])
                        second_dy = float(second_labels[j + 2])

                        dist1 = euclidean_dist(second_node1, [first_node2[0] + first_dx, first_node2[1] + first_dy])
                        dist2 = euclidean_dist(first_node2, [second_node1[0] + second_dx, second_node1[1] + second_dy])

                        pairs += dist1
                        pairs += dist2

                        # diff += 2 * DOMAIN_LEN * exp(-dist1/DOMAIN_LEN)+1
                        # diff += 2 * DOMAIN_LEN * exp(-dist2 / DOMAIN_LEN) + 1

                        diff += dist1
                        diff += dist2

                        break

    return diff, (loops, domain_lengths, pairs)
