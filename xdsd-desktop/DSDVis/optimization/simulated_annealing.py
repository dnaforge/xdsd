from collections import deque
from copy import deepcopy

from PyQt5.QtWidgets import QApplication
from numpy import exp
from numpy.random import uniform, choice

from DSDVis.optimization.energy_function import E


def optimize_one_iteration(state, energy, increment, T, best_state, best_energy, iterations_number):
    """
    Performs state change in the given temperature in simulated annealing

    :param state: Species object to be optimized
    :param energy: Value of the initial state's energy function E
    :param increment: Upper bound on the movement of species' hinges (in pixels)
    :param T: Current temperature value
    :param best_state: Reference value for the best state after the optimization (initially equal to state)
    :param best_energy: Reference value for the energy of the best state  after the optimization (initially equal to energy)
    :param iterations_number: Number of state changes to perform (moves)
    :return:
    """
    for i in range(iterations_number):
        QApplication.processEvents()
        next_state = move(state, increment)
        # energy components: attraction, repulsion
        next_energy, energy_components = E(next_state)
        diff = next_energy - energy

        if diff <= 0 or uniform() < exp(-diff / T):
            state = next_state
            energy = next_energy

            if energy < best_energy:
                best_energy = energy
                best_state = state

    return state, energy, best_state, best_energy


def decrease_temperature(T, cool):
    """
    Cooling schedule of the optimization

    :param T: Current temperature
    :param cool: Cooling factor
    :return: New temperature
    """
    T *= cool
    return T


def move(initial_specie, increment):
    """
    Performs the state change in the simulated annealing

    :param initial_specie: Species object to be changed
    :param increment: Upper bound on the movement of species' hinges (in pixels)
    :return: New Species object after the change
    """
    specie = deepcopy(initial_specie)

    hinges = specie.get_hinges()
    start_hinge = choice(hinges)

    strand = specie.get_strand_by_id(start_hinge.get_strand_id())

    queue = deque()
    visited = {}
    for hinge in hinges:
        visited[hinge.get_id()] = False

    if uniform() < 0.4:  # rotation
        rotation = True
    else:
        rotation = False

    dx, dy = uniform(low=-increment, high=increment, size=2).T
    start_hinge.move_first_hinge([dx, dy])

    factor = 1

    queue.append(start_hinge)
    visited[start_hinge.get_id()] = True

    while len(queue) > 0:
        # pop the leading hinge from the queue, which move affects the neighbors
        # find both neighbors of the leading hinge
        # move both neighbors
        # add the neighbors to the queue
        hinge = queue.popleft()
        prev_hinge, next_hinge = strand.get_hinge_neighbors(hinge)

        if rotation is True:
            if prev_hinge is not None and (next_hinge is None or uniform() < 0.5):
                hinge.move_hinge(hinge.get_position(), hinge.get_new_position(), prev_hinge.get_position(), 1,
                                 factor)
                visited[prev_hinge.get_id()] = True
            else:
                hinge.move_hinge(hinge.get_position(), hinge.get_new_position(), next_hinge.get_position(), -1,
                                 factor)
                visited[next_hinge.get_id()] = True
            visited[hinge.get_id()] = True
            rotation = False

        factor *= 0.5

        if prev_hinge is not None:  # not the first hinge in a strand
            if visited[prev_hinge.get_id()] is False:
                # moving the neighboring hinge in the same direction to the leading hinge move
                prev_hinge.move_hinge(hinge.get_position(), hinge.get_new_position(), hinge.get_new_position(), -1,
                                      factor)
                queue.append(prev_hinge)
                visited[prev_hinge.get_id()] = True

        if next_hinge is not None:  # not the last hinge
            if visited[next_hinge.get_id()] is False:
                next_hinge.move_hinge(hinge.get_position(), hinge.get_new_position(), hinge.get_new_position(), 1,
                                      factor)
                queue.append(next_hinge)
                visited[next_hinge.get_id()] = True

        hinge.set_position(hinge.get_new_position())

    return specie
