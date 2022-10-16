from time import time

from PyQt5.QtCore import QRunnable, pyqtSignal, QObject, pyqtSlot
from PyQt5.QtWidgets import QApplication

from DSDVis.optimization.energy_function import E
from DSDVis.optimization.simulated_annealing import optimize_one_iteration
from DSDVis.utils.config import INITIAL_ITER_NO


class OptimizationSignals(QObject):
    finished = pyqtSignal()
    update = pyqtSignal(float, int)
    rendered_species = pyqtSignal(dict)


class OptimizationWorker(QRunnable):
    """
    Class extending QRunnable for running a single species rendering optimization in a separate thread of the main QThreadpool
    """
    def __init__(self, *args, **kwargs):
        super(OptimizationWorker, self).__init__()
        self.id = args[1]
        self.species_dict = args[2]
        self.parameters = args[3]
        self.optimizing = args[4]
        self.optimization_speed = args[5]
        self.signals = OptimizationSignals()

    def optimize(self, species_instance, start_temp, end_temp, increment, cool, species_no):
        """
        Performs the main loop of the simulated annealing

        :param species_instance: Species object to optimize
        :param start_temp: Start temperature of the simulated annealing
        :param end_temp: End temperature of the simulated annealing
        :param increment: Upper bound on the movement of species' hinges (in pixels)
        :param cool: The temperature is decreased by multiplying the cool factor and the current temperature
        :param species_no: Which species in the complex the species_instance is
        :return: Name of the species, optimized Species object
        """
        name = species_instance[0]
        state = species_instance[1]
        energy, sums = E(state)

        T = start_temp

        best_state = state
        best_energy = energy

        iterations_number = INITIAL_ITER_NO

        if len(state.get_domain_pairs()) != 0:  # if there are no bonds in strand
            # main loop of the simulated annealing
            while T >= end_temp and self.optimizing[self.id] is True:
                if self.optimization_speed == 1 or (self.optimization_speed == -1 and state.pseudoknot):
                    iterations_number = int((T / start_temp) * INITIAL_ITER_NO)
                elif self.optimization_speed == 2 or (self.optimization_speed == -1 and not state.pseudoknot):
                    iterations_number = int(INITIAL_ITER_NO ** (T/start_temp))

                state, energy, best_state, best_energy = optimize_one_iteration(state, energy, increment, T,
                                                                                best_state, best_energy,
                                                                                iterations_number)
                self.signals.update.emit(T, species_no + 1)
                QApplication.processEvents()
                T *= cool

        return name, best_state

    @pyqtSlot()
    def run(self):
        """
        Main function of the OptimizationWorker that performs the optimization of the whole species complex

        :return:
        """
        start_temp = self.parameters[0]
        end_temp = self.parameters[1]
        if self.optimization_speed == 0:
            end_temp = 1
        cool = self.parameters[2]
        increment = self.parameters[3]

        species = list(self.species_dict.items())
        args = [(species_instance, start_temp, end_temp, increment, cool) for species_instance in
                species]

        for i, arg in enumerate(args):
            name, state = self.optimize(*arg, i)
            self.species_dict[name] = state

        self.signals.rendered_species.emit(self.species_dict)
        self.signals.finished.emit()
