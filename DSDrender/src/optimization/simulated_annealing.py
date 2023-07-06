import os
import sys
from math import sqrt
from random import randrange

from PyQt5.QtWidgets import QApplication
from numpy import exp
from numpy.random import uniform

import src.utils.config
from src.optimization.energy_function import E

# from src.utils.config import COOL_CONST, END_TEMP_CONST, INCR_CONST, START_TEMP_CONST, \
#     get_vector_length, DOMAIN_LEN, get_side

# comment for compiling the doc
if len(sys.argv) > 1 and "OGDF_INSTALL_DIR" not in os.environ:
    os.environ["OGDF_INSTALL_DIR"] = sys.argv[1]
elif "OGDF_INSTALL_DIR" not in os.environ:
    os.environ["OGDF_INSTALL_DIR"] = "./src/ogdf/cmake-build-release"

# uncomment for compiling the doc
# os.environ["OGDF_INSTALL_DIR"] = "../ogdf/cmake-build-release"

from ogdf_python import ogdf, cppinclude

cppinclude("ogdf/basic/GraphCopy.h")


def optimize(G, GA, graph_domain_pairs, graph_loops, signals, species_no, stop):
    """
    Performs the main loop of the simulated annealing

    :param G: Graph representation of the species, holds info on the embedding
    :param GA: Graph attributes of G, holds info on the placements of the nodes
    :param graph_domain_pairs: Dictionary with the pairs of domains and their constituent nodes
    :param graph_loops: Dictionary with the endings of the loops in the species and their constituent nodes
    """
    # transfer the graph attributes to the copy so that it can be manipulated
    G_copy = ogdf.GraphCopy(G)
    GA_copy = ogdf.GraphAttributes(G_copy, ogdf.GraphAttributes.all)
    GA.transferToCopy(GA_copy)

    state = (G_copy, GA_copy)
    set_bond_targets(GA_copy, graph_domain_pairs)
    energy_history = [[] for _ in range(4)]
    # total energy, components: loop ends distance, domains lengths, pair placement
    energy, components = E(state, graph_domain_pairs, graph_loops, 1)
    energy_history[0].append(energy)
    energy_history[1].append(components[0])
    energy_history[2].append(components[1])
    energy_history[3].append(components[2])

    best_state = state
    best_energy = energy

    T = src.utils.config.START_TEMP_CONST
    T_end = src.utils.config.END_TEMP_CONST
    iterations_number = src.utils.config.INITIAL_ITER_NO
    increment = src.utils.config.INCR_CONST

    worse_energy = 0
    length_factor = 1

    # main loop of the simulated annealing
    while T >= T_end and not stop[0]:
        state, energy, best_state, best_energy, energy_history = optimize_one_iteration(state, energy, increment, T,
                                                                                        best_state, best_energy,
                                                                                        iterations_number,
                                                                                        graph_domain_pairs,
                                                                                        graph_loops, energy_history,
                                                                                        length_factor)

        # decrease temperature
        T *= src.utils.config.COOL_CONST
        # increase the influence of domain and loop length
        length_factor = 1 + (T-T_end)/(src.utils.config.START_TEMP_CONST-T_end)
        # decrease the number of iterations at the given temperature level
        iterations_number = int(0.935 * iterations_number)

        # restarting the annealing in case of a bad well
        if energy > best_energy:
            worse_energy += 1
        if worse_energy > 10:
            state = best_state
            energy = best_energy
            energy_history[0].append(T)
            worse_energy = 0

        signals.update.emit(T, species_no + 1)
        QApplication.processEvents()

    # transfer the new attributes to the graph (attributes = placements of the nodes)
    state[1].transferToOriginal(GA)

    return energy_history


def optimize_one_iteration(state, energy, increment, T, best_state, best_energy, iterations_number, graph_domain_pairs,
                           graph_loops, energy_history, length_factor):
    """
    Performs state change in the given temperature in simulated annealing

    :param state: Species object to be optimized
    :param energy: Value of the initial state's energy function E
    :param increment: Upper bound on the movement of species' hinges (in pixels)
    :param T: Current temperature value
    :param best_state: Reference value for the best state after the optimization (initially equal to state)
    :param best_energy: Reference value for the energy of the best state  after the optimization (initially equal to energy)
    :param iterations_number: Number of state changes to perform (moves)
    :param graph_domain_pairs: Dictionary with the pairs of domains and their constituent nodes
    :param graph_loops: Dictionary with the endings of the loops in the species and their constituent nodes
    :param energy_history: Array holding the history of all the energy components (for plotting purposes)
    :return:
    """
    for i in range(iterations_number):
        node, dx, dy = move(state, increment)
        set_bond_targets(state[1], graph_domain_pairs)
        # energy components: distance between the ends of the loops, domain lengths, pair placement
        next_energy, components = E(state, graph_domain_pairs, graph_loops, length_factor)
        diff = next_energy - energy

        if diff <= 0 or uniform() < exp(-diff / T):
            energy = next_energy
            energy_history[0].append(energy)
            energy_history[1].append(components[0])
            energy_history[2].append(components[1])
            energy_history[3].append(components[2])

            if energy < best_energy:
                best_energy = energy
                best_state = state
        else:
            unmove(state, node, dx, dy)

    return state, energy, best_state, best_energy, energy_history


def decrease_temperature(T, cool):
    """
    Cooling schedule of the optimization

    :param T: Current temperature
    :param cool: Cooling factor
    :return: New temperature
    """
    T *= cool
    return T


def move(state, increment):
    """
    Performs the state change in the simulated annealing

    :param state: Species object to be changed
    :param increment: Upper bound on the movement of species' hinges (in pixels)
    :return: New Species object after the change
    """
    G, GA = state

    node = G.chooseNode()
    dx = randrange(-increment, increment + 1, 1)
    dy = randrange(-increment, increment + 1, 1)

    GA.x[node] += dx
    GA.y[node] += dy

    return node, dx, dy


def unmove(state, node, dx, dy):
    """
    Undoes the state change in the simulated annealing

    :param state: Species object to be changed
    :param node: Node to be moved back
    :param dx: X increment
    :param dy: Y increment
    :return: New Species object after the change
    """
    G, GA = state

    GA.x[node] -= dx
    GA.y[node] -= dy


def set_bond_targets(GA, graph_domain_pairs):
    """
    Sets the designated placement of the pairs in relation to each other, i.e. the beginning of one domain is at
    DOMAIN/sqrt(2) orthogonal distance from the end of the second domain in a pair

    :param GA: Graph attributes holding info on the nodes. The resulting placements are wrote into nodes' labels in
    the format !bond_id first_place second_place
    :param graph_domain_pairs: Dictionary with all the pair in the species
    """
    # reset the target placements (after the movement)
    for bond, nodes in graph_domain_pairs.items():
        GA.label[nodes[0][0]] = ""
        GA.label[nodes[0][1]] = ""
        GA.label[nodes[1][0]] = ""
        GA.label[nodes[1][1]] = ""

    # add the targets to the nodes' labels
    for bond, nodes in graph_domain_pairs.items():
        first_pair = nodes[0]
        second_pair = nodes[1]

        # 3' and 5' end of the first domain
        first_node1 = [GA.x(first_pair[0]), GA.y(first_pair[0])]
        first_node2 = [GA.x(first_pair[1]), GA.y(first_pair[1])]

        # 3' and 5' end of the second domain
        second_node2 = [GA.x(second_pair[1]), GA.y(second_pair[1])]
        second_node1 = [GA.x(second_pair[0]), GA.y(second_pair[0])]

        # get the candidates for the bond targets and the vectors to them from the domains
        first_candidate, first_perp = get_bond_target_candidate(first_node1, first_node2)
        second_candidate, second_perp = get_bond_target_candidate(second_node1, second_node2)

        # check how many cosines are positive == if the shape between the pairs is a valid quadrilateral
        # (where only one of the angles can be greater than 180 degrees)
        convexity = get_pair_convexity(first_candidate, second_candidate,
                                       first_node1, first_node2, second_node1, second_node2)
        # flip the bond side in both domains
        if convexity < 3:
            first_perp = [-first_perp[0], -first_perp[1]]
            second_perp = [-second_perp[0], -second_perp[1]]

        # write the bond coordinates to the nodes' labels
        write_bond_targets(GA, bond, first_pair, first_perp)
        write_bond_targets(GA, bond, second_pair, second_perp)


def write_bond_targets(GA, bond, pair, perp):
    """
    Writes the coordinates of the bond targets to the nodes' labels which are determined by the perpendicular vector

    :param GA: Graph attributes holding the nodes' labels
    :param bond: Bond id for the pair
    :param pair: Domain for which the bonds are determined
    :param perp: Perpendicular vector to the pair domain
    """
    if len(GA.label[pair[0]]) == 0 or len(GA.label[pair[0]]) > 200:
        GA.label[pair[0]] = "!" + bond + " " + str(perp[0]) + " " + str(perp[1])
    else:
        GA.label[pair[0]] = GA.label[pair[0]] + " " + "!" + bond + " " + str(perp[0]) + " " + str(perp[1])

    if len(GA.label[pair[1]]) == 0 or len(GA.label[pair[1]]) > 200:
        GA.label[pair[1]] = "!" + bond + " " + str(perp[0]) + " " + str(perp[1])
    else:
        GA.label[pair[1]] = GA.label[pair[1]] + " " + "!" + bond + " " + str(perp[0]) + " " + str(perp[1])


def get_pair_convexity(first_candidate, second_candidate, first_node1, first_node2, second_node1, second_node2):
    """
    Check how many cosines of the angles between vector from the node to the paired node and the node to the candidate place for the paired node are positive i.e. if the shape between the pairs is a valid quadrilateral (where only one of the angles can be greater than 180 degrees).

    :param first_candidate: Candidate placement for the bond target for the first domain in the pair
    :param second_candidate: Candidate placement for the bond target for the second domain in the pair
    :param first_node1: Node denoting the beginning of the first domain in the pair
    :param first_node2: Node denoting the end of the first domain in the pair
    :param second_node1: Node denoting the beginning of the second domain in the pair
    :param second_node2: Node denoting the end of the first second in the pair
    :return:
    """
    return get_side_convexity(first_candidate, first_node1, first_node2, second_node1, second_node2) + \
           get_side_convexity(second_candidate, second_node1, second_node2, first_node1, first_node2)


def get_side_convexity(candidate, first_node1, first_node2, second_node1, second_node2):
    """
    Check the sign of the cosine of the angle between vector from the node to the paired node and the node to the candidate place for the paired node

    :param candidate: Candidate placement for the bond target for the domain in the pair
    :param first_node1: Node denoting the beginning of the first domain in the pair
    :param first_node2: Node denoting the end of the first domain in the pair
    :param second_node1: Node denoting the beginning of the second domain in the pair
    :param second_node2: Node denoting the end of the first second in the pair
    :return:
    """
    # the first vector to candidate is the same for both ends of the domain
    return int(src.utils.config.get_cos([candidate[0] - first_node1[0], candidate[1] - first_node1[1]],
                                        [second_node2[0] - first_node1[0], second_node2[1] - first_node1[1]]) > 0) + \
           int(src.utils.config.get_cos([candidate[0] - first_node1[0], candidate[1] - first_node1[1]],
                                        [second_node1[0] - first_node2[0], second_node1[1] - first_node2[1]]) > 0)


def get_bond_target_candidate(node1, node2):
    """
    Get the candidate placement of the bond target for the domain which ends are denoted by the parameters

    :param node1: First end of the considered domain
    :param node2: Second end of the considered domain
    """
    direction = [node2[0] - node1[0], node2[1] - node1[1]]
    direction_len = src.utils.config.get_vector_length(direction)
    direction_norm = [direction[0] / direction_len * src.utils.config.DOMAIN_LEN / sqrt(2),
                      direction[1] / direction_len * src.utils.config.DOMAIN_LEN / sqrt(2)]
    perp = [-direction_norm[1], direction_norm[0]]

    return [node1[0] + perp[0], node1[1] + perp[1]], perp
