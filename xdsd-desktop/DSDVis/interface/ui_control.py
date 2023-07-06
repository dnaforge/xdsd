import shutil
from copy import deepcopy
from threading import Event

import matplotlib.pyplot as plt
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import pyqtSignal, QThreadPool, QSize, QUrl
from PyQt5.QtGui import QTransform, QImage, QPainter
from PyQt5.QtSvg import QSvgGenerator
from PyQt5.QtWidgets import QGraphicsScene, QFileDialog, QVBoxLayout
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from DSDPy.src.basics import graph_processor, output
from DSDPy.src.util.cexception import SpeciesError
from DSDPy.src.util.model import Model

try:
    from PyQt5 import sip
except ImportError:
    import sip

from DSDVis.elements.domain import DomainGraphicsItem
from DSDVis.elements.loop import LoopGraphicsItem
from DSDVis.elements.species import SpeciesGraphicsItem
from DSDVis.interface.processor_thread import ProcessorThread
from DSDVis.interface.progress_window import ProgressWindow
from DSDVis.interface.reaction_window import ReactionWindow, ReactionArrowGraphicsItem
from DSDVis.interface.species_window import SpeciesWindow
from DSDVis.interface.ui import Ui_MainWindow
from DSDVis.model.ui_model import UiModel
from DSDVis.optimization.optimization_worker import OptimizationWorker
from DSDVis.utils.config import get_default_optimization_parameters, get_color, reset_color, get_id
from DSDVis.utils.network_generation import parse_network, NetworkViewer


class UiControl(QtWidgets.QMainWindow, Ui_MainWindow):
    """
    Controller class for managing the user interaction with the view
    """
    close_detached_windows = pyqtSignal()

    def __init__(self, *args, obj=None, **kwargs):
        ############
        # DSDrender
        ############
        super(UiControl, self).__init__()
        self.setupUi(self)
        self.setWindowTitle('XDSD')
        self.ui_model = UiModel()

        # add a network viewer for network generating
        layout = QVBoxLayout()
        self.network_viewer = NetworkViewer(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.network_viewer)
        self.network_view.setLayout(layout)
        self.network_view.setStyleSheet("background-color:white;")

        self.input_species_render = None
        self.input_initial_species_render = None
        self.input_final_species_render = None

        self.output_species_render = None
        self.output_initial_species_render = None
        self.output_final_species_render = None

        self.optimizing = {}
        self.current_rendering = 0
        self.optimization_thread_pool = QThreadPool()
        self.init_species_no = None
        self.species_detached_windows = []
        self.progress_windows = []
        self.bond_colors = {}

        self.canvas_view.setScene(QGraphicsScene())
        self.change_speed()

        # bindings for ui elements
        self.open_button.clicked.connect(self.open_file)
        self.save_button.clicked.connect(lambda: self.save_file(self.code_text))
        self.text_output_save.clicked.connect(lambda: self.save_file(self.text_output))
        self.canvas_save.clicked.connect(lambda: self.save_img_file(self.canvas_view))
        self.canvas_save_2.clicked.connect(lambda: self.save_img_file(self.canvas_view_2))
        self.canvas_save_3.clicked.connect(self.save_svg_file)
        self.optimization_start.clicked.connect(self.start_optimization_all_species)
        self.optimization_start_2.clicked.connect(self.start_optimization_all_species)
        self.optimization_start_3.clicked.connect(self.start_optimization_all_species)
        self.optimization_finish.clicked.connect(lambda: self.stop_optimizing(None))
        self.threshold_slider.valueChanged.connect(self.set_slider_value)
        self.show_button.clicked.connect(self.show_species_clicked)
        self.canvas_combo.currentIndexChanged.connect(self.change_input_view)
        self.canvas_combo_2.currentIndexChanged.connect(self.change_output_view)
        self.network_viewer.species_node_clicked.connect(self.network_species_clicked)
        self.network_viewer.reaction_node_clicked.connect(self.network_reaction_clicked)
        self.network_combo.currentIndexChanged.connect(self.change_network_layout)
        self.enable_speed_box.stateChanged.connect(self.change_speed)

        ############
        # DSDPy
        ############

        self.model = Model()
        self.procthread = None
        self.lock = None
        self.simuarg = None
        self.simumode = 'bng'
        self.paused = False
        self.canvas = None
        self.network = None
        self.thread_stopped = True

        self.simulate_button.setEnabled(False)
        # self.simulate_combo.setEnabled(False)

        # bindings for ui elements
        self.generate_button.clicked.connect(self.generate)
        self.simulate_button.clicked.connect(self.simulate)
        self.simulate_stochastic.toggled.connect(self.stochastic_simulation_mode)
        self.simulate_deterministic.toggled.connect(self.deterministic_simulation_mode)
        self.generate_stop_button.clicked.connect(self.generate_stop)

        self.generate_block()
        self.simulate_lock()
        self.optimization_lock()

        # self.showMaximized()

    ############
    # DSDPy
    ############

    def generate(self):
        """
        Callback for Generate button click

        :return:
        """
        text = self.code_text.toPlainText()
        try:
            info, initnames, concentrations, outdir, simupara, initlen = graph_processor.initiation(text=text)
        except TypeError:
            self.print_error('Incorrect input')
            return
        except SpeciesError:
            self.print_error('Processing error')
            return
        self.simuarg = (initnames, concentrations, outdir, simupara, initlen)

        event = Event()
        self.procthread = ProcessorThread(event, int(self.threshold_slider.value()), args=info)
        self.procthread.setDaemon(True)
        self.lock = self.procthread.get_lock()
        self.paused = False
        self.thread_stopped = False

        self.generate_lock()
        self.simulate_lock()
        self.optimization_lock()
        self.open_button.setEnabled(False)

        self.procthread.start()

        # show results when finished
        self.init_species_no = len(initnames)
        self.procthread.pp.my_signal.connect(self.show_generate_results)

    def show_generate_results(self):
        if not self.procthread:
            return
        specieslist, speciesidmap, reactionlist, kinetics, indexlist, cursor, visited = self.procthread.get_arg_info()
        try:
            text = graph_processor.post_enumeration(specieslist, reactionlist)
        except:
            self.print_error('Generation Error')
            return
        self.print_output(text)

        self.print_log('Generation finished')
        self.output_toolbar.setCurrentIndex(2)
        self.generate_unlock()
        self.simulate_unlock()
        self.optimization_unlock()
        self.open_button.setEnabled(True)

        self.show_output_species()
        graph, species_ids = parse_network(specieslist, reactionlist, self.init_species_no)
        self.show_network(graph, species_ids)

    def change_network_layout(self):
        error = self.network_viewer.change_network_layout(self.network_combo.currentText())

        if error is not None:
            self.print_error(error)

    def show_network(self, graph, species_ids):
        error = self.network_viewer.set_network(graph, species_ids, self.network_combo.currentText(),
                                                self.init_species_no)
        if error is not None:
            self.print_error(error)

    def generate_lock(self):
        self.generate_button.setEnabled(False)
        self.generate_stop_button.setEnabled(True)

    def generate_block(self):
        self.generate_button.setEnabled(False)
        self.generate_stop_button.setEnabled(False)

    def simulate_lock(self):
        self.simulate_button.setEnabled(False)
        # self.simulate_combo.setEnabled(False)

    def optimization_lock(self):
        self.show_button.setEnabled(False)
        self.optimization_start.setEnabled(False)
        self.optimization_start_2.setEnabled(False)
        self.optimization_start_3.setEnabled(False)
        self.optimization_finish.setEnabled(False)

    def generate_unlock(self):
        self.generate_button.setEnabled(True)
        self.generate_stop_button.setEnabled(False)

    def simulate_unlock(self):
        if not self.thread_stopped:
            self.simulate_button.setEnabled(True)
            # self.simulate_combo.setEnabled(True)

    def optimization_unlock(self):
        self.show_button.setEnabled(True)
        self.optimization_start.setEnabled(True)
        self.optimization_start_2.setEnabled(True)
        self.optimization_start_3.setEnabled(True)
        self.optimization_finish.setEnabled(True)

    def simulate(self):
        """
        Callback for Simulate button click

        :return:
        """
        if not self.procthread:
            return
        specieslist, speciesidmap, reactionlist, kinetics, indexlist, cursor, visited = self.procthread.get_arg_info()
        initnames, concentrations, outdir, simupara, initlen = self.simuarg
        try:
            x, y, obs = graph_processor.simulation(specieslist, reactionlist, initlen, initnames, concentrations,
                                                   outdir, simupara, self.simumode)
        except:
            self.print_error('Simulation error')
            return
        self.display_output_img(x, y, obs, option=self.simumode)

    def display_output_img(self, x, y, obs, colormap='tab10', option='bng'):
        obslen = len(obs)
        if self.canvas is None:
            sc = output.Canvas(self, width=5, height=6, dpi=96)
            self.canvas = sc
            toolbar = NavigationToolbar(sc, self)

            layout = QtWidgets.QVBoxLayout()
            layout.addWidget(toolbar)
            layout.addWidget(sc)

            self.graph_widget.setLayout(layout)
        else:
            sc = self.canvas
            sc.axes.cla()

        cmap = plt.cm.get_cmap(colormap, obslen)

        for i in range(0, obslen):
            label = obs[i].name[3:]
            if option == 'bng':
                sc.axes.plot(x, y[:, i], label=label, c=cmap(i))
            elif option == 'scipy':
                sc.axes.plot(x, y[obs[i].name], label=label, c=cmap(i))

        sc.axes.set_xlabel("Time (s)")
        sc.axes.set_ylabel("Complexes")
        sc.axes.legend(bbox_to_anchor=(1.01, 1))
        sc.axes.set_xmargin(0.5)

        sc.draw()

        self.output_toolbar.setCurrentIndex(3)
        self.print_log('Time course plot finished')

    def stochastic_simulation_mode(self, checked):
        if checked:
            self.simumode = 'bng'
            self.print_log('Simulation mode set to stochastic')

    def deterministic_simulation_mode(self, checked):
        if checked:
            self.simumode = 'scipy'
            self.print_log('Simulation mode set to deterministic')

    def generate_stop(self):
        if not self.procthread:
            return
        if not self.paused:
            self.lock.acquire()
        self.generate_unlock()
        self.optimization_unlock()
        self.open_button.setEnabled(True)
        self.procthread.raise_exception()
        self.procthread.stop()
        self.thread_stopped = True
        self.print_log("Generating species stopped")

    ############
    # DSDrender
    ############

    def add_species_to_scene(self, view, species_dict):
        """
        Renders species on the given view

        :param view: QGraphicsView object where the species will be rendered
        :param species_dict: species to be rendered
        :return:
        """
        scene = QGraphicsScene()

        for name, species in species_dict.items():
            self.print_log("Loaded species: " + name)
            species_group = SpeciesGraphicsItem(name)
            for strand in species.get_strands():
                domains = strand.get_domains()
                for i in range(len(domains)):
                    if domains[i].__class__.__name__ != 'Loop':
                        if domains[i].get_bond() == -1:
                            color = get_color(domains[i].get_bond())
                        else:
                            name_key = domains[i].name
                            idx = domains[i].name.find('*')
                            if idx != -1:
                                name_key = name_key[:idx]
                            color = self.bond_colors[name_key]
                        item = DomainGraphicsItem(domains[i], color, self.show_dot.isChecked())
                    else:
                        color = get_color(-1)
                        item = LoopGraphicsItem(domains[i], domains[i - 1], domains[i + 1],
                                                species.pseudoknot, color)
                    species_group.addToGroup(item)
            scene.addItem(species_group)

            # move the species to the right height
            translate = QTransform()
            dx = -species_group.boundingRect().left()
            dy = -(species_group.boundingRect().top() - species.render_height)
            translate.translate(dx, dy)
            species_group.setTransform(translate)

        view.setScene(scene)

    def show_species(self, final, initial, view, species_dict):
        self.add_species_to_scene(view, species_dict)
        # save the initial/final rendered views of all input/output species
        if final:
            if self.current_rendering == 0:
                self.input_final_species_render = self.canvas_view.scene()
                self.canvas_combo.setCurrentIndex(1)
            else:
                self.output_final_species_render = self.canvas_view_2.scene()
                self.canvas_combo_2.setCurrentIndex(1)
        if initial:
            if self.current_rendering == 0:
                self.input_initial_species_render = self.canvas_view.scene()
                self.canvas_combo.setCurrentIndex(0)
            else:
                self.output_initial_species_render = self.canvas_view_2.scene()
                self.canvas_combo_2.setCurrentIndex(0)

    def show_input_species(self):
        log, errors = self.ui_model.parse_input_species(self.code_text.toPlainText(),
                                                        self.permute_chbox.isChecked(),
                                                        self.flip_strands_chbox.isChecked(),
                                                        self.flip_domains_chbox.isChecked(),
                                                        self.bond_colors)
        self.ui_model.place_species(self.ui_model.input_species_dict)
        if len(errors) == 0:
            if len(log) > 0:
                self.print_log(log[0])
            self.current_rendering = 0
            self.show_species(False, True, self.canvas_view, self.ui_model.input_species_dict)
            return True
        else:
            self.print_errors(errors)
            return False

    def show_output_species(self):
        if self.init_species_no:
            log, errors = self.ui_model.parse_output_species(self.text_output.toPlainText(),
                                                             self.permute_chbox.isChecked(),
                                                             self.flip_strands_chbox.isChecked(),
                                                             self.flip_domains_chbox.isChecked(),
                                                             self.init_species_no)
            self.ui_model.place_species(self.ui_model.output_species_dict)
            if len(errors) == 0:
                if len(log) > 0:  # pseudoknot
                    self.print_log(log[0])
                self.current_rendering = 1
                self.show_species(False, True, self.canvas_view_2, self.ui_model.output_species_dict)
                return True
            else:
                self.print_errors(errors)
                return False
        else:
            self.print_error('Generate the output first!')
            return False

    def change_input_view(self):
        if self.canvas_combo.currentIndex() == 0:  # initial view
            self.canvas_view.setScene(self.input_initial_species_render)
        else:  # optimized view
            self.canvas_view.setScene(self.input_final_species_render)

    def change_output_view(self):
        if self.canvas_combo_2.currentIndex() == 0:  # initial view
            self.canvas_view_2.setScene(self.output_initial_species_render)
        else:  # optimized view
            self.canvas_view_2.setScene(self.output_final_species_render)

    def show_species_clicked(self):
        self.reset_all()
        self.generate_unlock()
        self.optimization_unlock()
        self.show_input_species()

    def open_file(self):
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.AnyFile)
        # dialog.setNameFilter("Text files (*.txt)")
        dialog.setDirectory("./examples")
        dialog.setWindowTitle("Select File")
        # file_dir, _ = QFileDialog.getOpenFileName(self, "Select File", "./examples",
        #                                           "All Files (*);;Text Files (*.txt)")

        urls = [QUrl.fromLocalFile("./examples"), QUrl.fromLocalFile("~/workspace")]
        dialog.setSidebarUrls(urls)

        if dialog.exec_():
            file_dir = dialog.selectedFiles()[0]
            self.print_log("Reading file")
            self.file_label.setText(file_dir)
            text, log, error = self.ui_model.read_file(file_dir)
            self.code_text.setPlainText(text)
            self.print_log(log)

            if error == "":
                self.show_species_clicked()
            else:
                self.print_error(error)

    def reset_all(self):
        self.reset_model()
        self.current_rendering = 0
        self.reset_view()
        self.current_rendering = 1
        self.reset_view()
        self.text_output.clear()
        self.canvas = None
        self.init_species_no = None
        self.species_detached_windows = []
        self.delete_layout(self.graph_widget.layout())
        self.network_viewer.set_network(None, None, None, None)
        self.bond_colors = {}
        reset_color()

    def delete_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.deleteLayout(item.layout())
            sip.delete(layout)

    def save_file(self, text_input):
        text = text_input.toPlainText()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save file", "~/workspace",
                                                   "All Files (*)")
        if file_name:
            file = open(file_name, 'w+')
            file.write(text)
            file.close()

    def save_img_file(self, view):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save file", "~/workspace",
                                                   "SVG Files (*.svg)")
        if file_name:
            svg = QSvgGenerator()
            svg.setFileName(file_name)
            svg.setSize(QSize(view.sceneRect().width(), view.sceneRect().height()))
            svg.setViewBox(view.sceneRect())
            painter = QPainter(svg)
            view.scene().render(painter)
            painter.end()

    def save_svg_file(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save file", "~/workspace",
                                                   "SVG Files (*.svg")
        if file_name:
            try:
                shutil.copy('tmp/network.svg', file_name)
            except OSError:
                self.print_error('Cannot save the network')

    def print_errors(self, errors):
        for error in errors:
            self.terminal_error_text.append(str(error))
        self.terminal.setCurrentIndex(1)

    def print_error(self, text):
        self.terminal_error_text.append(text)
        self.terminal.setCurrentIndex(1)

    def print_log(self, text):
        self.terminal_output_text.append(text)
        self.terminal.setCurrentIndex(0)

    def print_output(self, text):
        self.text_output.setText(text)

    def reset_view(self):
        if self.current_rendering == 0:
            if self.canvas_view.scene() is not None:
                self.canvas_view.scene().clear()

            self.input_species_render = None
            self.input_initial_species_render = None
            self.input_final_species_render = None
        else:
            if self.canvas_view_2.scene() is not None:
                self.canvas_view_2.scene().clear()

            self.output_species_render = None
            self.output_initial_species_render = None
            self.output_final_species_render = None

    def reset_model(self):
        self.ui_model.reset_species()

    def reset_current_model(self, i):
        self.ui_model.reset_species(i)

    def get_optimization_speed(self):
        if self.enable_speed_box.isChecked():
            if self.constant_button.isChecked():
                return 0
            elif self.linear_button.isChecked():
                return 1
            else:
                return 2
        else:
            return -1

    def start_optimization_all_species(self):
        self.current_rendering = self.output_toolbar.currentIndex()
        if self.current_rendering == 0:
            self.reset_current_model(self.current_rendering)
            self.reset_view()
            if self.show_input_species():
                view = self.canvas_view
                self.start_optimization(view, self.ui_model.input_species_dict, False)
        elif self.current_rendering == 1:
            self.reset_current_model(self.current_rendering)
            self.reset_view()
            if self.show_output_species():
                view = self.canvas_view_2
                self.start_optimization(view, self.ui_model.output_species_dict, False)
        else:
            self.print_error("Navigate to the view to be rendered!")
            return

    def start_optimization(self, view, species_dict, detach):
        """
        Gets the optimization parameters, start the OptimizationWorker that generates the species placement

        :param view: QGraphicsView object where the species will be rendered
        :param species_dict: species to be optimized
        :param detach: flag denoting if the optimization was started by clicking on network node (the species is rendered onto a detached window)
        :return:
        """
        id = get_id()
        self.optimizing[id] = True
        parameters = get_default_optimization_parameters()
        self.change_optimization_button()
        self.generate_block()
        self.simulate_lock()
        self.print_log("Rendering the species...")
        species_to_optimize = deepcopy(species_dict)

        optimization_worker = OptimizationWorker(self, id, species_to_optimize, parameters, self.optimizing,
                                                 self.get_optimization_speed())
        optimization_worker.signals.rendered_species.connect(
            lambda rendered_species: self.optimization_finished(id, rendered_species, view=view, detach=detach))
        self.progress_windows.append(
            ProgressWindow(id, optimization_worker.signals.finished, optimization_worker.signals.update,
                           parameters[0], len(species_dict.keys()), self.stop_optimizing))
        self.optimization_thread_pool.start(optimization_worker)

        self.progress_windows[-1].show()

    def network_species_clicked(self, name):
        self.species_detached_windows.append(SpeciesWindow(self.close_detached_windows, name, self.save_img_file))
        species_dict = {name: self.ui_model.output_species_dict[name]}
        self.ui_model.recalculate_render_height(species_dict)
        self.species_detached_windows[-1].show()
        self.current_rendering = -1
        self.start_optimization(self.species_detached_windows[-1].view, species_dict, True)

    def network_reaction_clicked(self, data):
        reaction_name = data[0]
        black_edges_in = data[1]
        black_edges_out = data[2]
        black_reaction_rate = data[3]
        gray_reaction_rate = data[4]

        self.species_detached_windows.append(
            ReactionWindow(self.close_detached_windows, reaction_name, self.save_img_file))

        input_species_dict = {}
        output_species_dict = {}

        for int_species_name in black_edges_in:
            input_species_dict[int_species_name] = deepcopy(self.ui_model.output_species_dict[int_species_name])

        for out_species_name in black_edges_out:
            output_species_dict[out_species_name] = deepcopy(self.ui_model.output_species_dict[out_species_name])

        self.ui_model.recalculate_render_height(input_species_dict)
        self.ui_model.recalculate_render_height(output_species_dict)

        scene = QGraphicsScene()
        arrows = ReactionArrowGraphicsItem(reaction_name, black_reaction_rate, gray_reaction_rate)
        scene.addItem(arrows)

        self.species_detached_windows[-1].view_reaction.setScene(scene)
        self.species_detached_windows[-1].show()

        self.current_rendering = -1
        self.start_optimization(self.species_detached_windows[-1].view_input, input_species_dict, True)
        self.start_optimization(self.species_detached_windows[-1].view_output, output_species_dict, True)

    def optimization_finished(self, id, species_dict, view=None, detach=False):
        if not detach:
            self.show_species(True, False, view, species_dict)
        else:
            self.show_species(False, False, view, species_dict)

        self.print_log("Optimization finished")
        self.stop(id)

    def change_optimization_button(self):
        flag = True
        for flag_value in self.optimizing.values():
            if flag_value:
                flag = False
                break
        self.optimization_start.setEnabled(flag)
        self.optimization_start_2.setEnabled(flag)
        self.optimization_start_3.setEnabled(flag)
        self.open_button.setEnabled(flag)

        if self.current_rendering == 0:
            self.canvas_combo.setEnabled(flag)
            self.canvas_combo.setCurrentIndex(1)
        elif self.current_rendering == 1:
            self.canvas_combo_2.setEnabled(flag)
            self.canvas_combo_2.setCurrentIndex(1)

    def stop_optimizing(self, id=None):
        if id is None:
            for _id in self.optimizing.keys():
                self.optimizing[_id] = False
        else:
            self.optimizing[id] = False

    def stop(self, id=None):
        self.stop_optimizing(id)
        self.change_optimization_button()
        self.generate_unlock()
        self.simulate_unlock()

    def set_slider_value(self, value):
        if value == 1:
            self.slider_value_label.setText(str(value) + ' iteration')
        else:
            self.slider_value_label.setText(str(value) + ' iterations')

    def change_speed(self):
        self.exponential_button.setEnabled(self.enable_speed_box.isChecked())
        self.linear_button.setEnabled(self.enable_speed_box.isChecked())
        self.constant_button.setEnabled(self.enable_speed_box.isChecked())

    def closeEvent(self, a0: QtGui.QCloseEvent):
        for flag_id in self.optimizing.keys():
            self.optimizing[flag_id] = False
        try:
            shutil.rmtree('tmp')
        except OSError:
            pass
        self.close_detached_windows.emit()
        a0.accept()
