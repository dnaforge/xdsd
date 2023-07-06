import shutil
from threading import Event

import matplotlib.pyplot as plt
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import pyqtSignal, QThreadPool, QSize, Qt, QRectF, QPoint, QLineF, QPointF
from PyQt5.QtGui import QTransform, QPainter, QPen, QColor, QFont, QPainterPath
from PyQt5.QtSvg import QSvgGenerator
from PyQt5.QtWidgets import QGraphicsScene, QFileDialog, QVBoxLayout, QGraphicsItemGroup, QGraphicsSimpleTextItem, \
    QGraphicsItem, QGraphicsEllipseItem, QGraphicsLineItem, QApplication, QGraphicsPathItem
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from DSDPy.src.basics import graph_processor, output
from DSDPy.src.util.cexception import SpeciesError
from DSDPy.src.util.model import Model
from src.elements.element import get_element
from src.elements.overhang import Overhang, OverhangGraphicsItem
from src.interface.progress_window import ProgressWindow

try:
    from PyQt5 import sip
except ImportError:
    import sip

from src.elements.domain import DomainGraphicsItem, BondGraphicsItem, Domain
from src.elements.loop import LoopGraphicsItem, Loop
from src.interface.processor_thread import ProcessorThread
from src.interface.reaction_window import ReactionWindow, ReactionArrowGraphicsItem
from src.interface.species_window import SpeciesWindow
from src.interface.ui import Ui_MainWindow
from src.model.ui_model import UiModel
import src.utils.config
from src.utils.network_generation import parse_network, NetworkViewer


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
        self.setWindowTitle('DSDrender')
        self.ui_model = UiModel()

        # add a network viewer for network generating
        layout = QVBoxLayout()
        self.network_viewer = NetworkViewer(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.network_viewer)
        self.network_view.setLayout(layout)
        self.network_view.setStyleSheet("background-color:white;")

        self.optimizing = {}
        self.current_rendering = 0
        self.optimization_thread_pool = QThreadPool()
        self.init_species_no = None
        self.species_detached_windows = []
        self.progress_window = [None]
        self.bond_colors = {}

        self.canvas_view.setScene(QGraphicsScene())

        # bindings for ui elements
        self.open_button.clicked.connect(self.open_file)
        self.save_button.clicked.connect(lambda: self.save_file(self.code_text))
        self.text_output_save.clicked.connect(lambda: self.save_file(self.text_output))
        self.canvas_save.clicked.connect(lambda: self.save_img_file(self.canvas_view))
        self.canvas_save_2.clicked.connect(lambda: self.save_img_file(self.canvas_view_2))
        self.canvas_save_3.clicked.connect(self.save_svg_file)
        self.threshold_slider.valueChanged.connect(self.set_slider_value)
        self.threshold_slider2.valueChanged.connect(self.set_slider_value2)
        self.show_button.clicked.connect(self.show_species_clicked)
        self.show_button2.clicked.connect(self.show_species_clicked)
        self.network_viewer.species_node_clicked.connect(self.network_species_clicked)
        self.network_viewer.reaction_node_clicked.connect(self.network_reaction_clicked)
        self.network_viewer.viewport_moved.connect(self.reset_species_combo)
        self.network_combo.currentIndexChanged.connect(self.change_network_layout)
        self.species_combo.currentIndexChanged.connect(self.change_viewed_species)
        # self.straight_checkbox.stateChanged.connect(self.change_layout)
        self.straight_radio.toggled.connect(lambda: self.change_layout(self.straight_radio.isChecked()))
        self.ortho_radio.toggled.connect(lambda: self.change_layout(self.straight_radio.isChecked()))

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
        self.simulate_combo.setEnabled(False)

        # bindings for ui elements
        self.generate_button.clicked.connect(self.generate)
        self.simulate_button.clicked.connect(self.simulate)
        self.simulate_combo.currentIndexChanged.connect(self.change_simulation_mode)
        self.generate_stop_button.clicked.connect(self.generate_stop)

        self.generate_block()
        self.simulate_lock()

        self.showMaximized()

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
        self.procthread = ProcessorThread(event, int(self.threshold_slider.value()), self.progress_window, self.generate_stop, args=info)
        self.procthread.setDaemon(True)
        self.lock = self.procthread.get_lock()
        self.paused = False
        self.thread_stopped = False

        self.generate_lock()
        self.simulate_lock()
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
        self.open_button.setEnabled(True)

        self.show_output_species()
        graph, species_ids = parse_network(specieslist, reactionlist, self.init_species_no)
        self.set_species_combo(species_ids)
        self.show_network(graph, species_ids)

    def set_species_combo(self, species_ids):
        for i, species_id in enumerate(species_ids, 1):
            if i <= self.init_species_no:
                prefix = "ss"
            else:
                prefix = "sp_"
            self.species_combo.addItem(prefix + str(species_id))

    def change_network_layout(self):
        error = self.network_viewer.change_network_layout(self.network_combo.currentText())

        if error is not None:
            self.print_error(error)

    def change_viewed_species(self):
        error = self.network_viewer.change_focus_species(self.species_combo.currentText())

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
        self.simulate_combo.setEnabled(False)

    def generate_unlock(self):
        self.generate_button.setEnabled(True)
        self.generate_stop_button.setEnabled(False)

    def simulate_unlock(self):
        if not self.thread_stopped:
            self.simulate_button.setEnabled(True)
            self.simulate_combo.setEnabled(True)

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
        self.print_log('Simulation plot finished')

    def change_simulation_mode(self):
        mode = self.simulate_combo.currentText()
        if mode == 'Stochastic':
            self.simumode = 'bng'
        else:
            self.simumode = 'scipy'
        self.print_log('Simulation mode set to ' + mode)

    def generate_stop(self):
        if not self.procthread:
            return
        if not self.paused:
            self.lock.acquire()
        self.generate_unlock()
        # self.optimization_unlock()
        self.open_button.setEnabled(True)
        self.procthread.raise_exception()
        self.procthread.stop()
        self.thread_stopped = True
        self.print_log("Generating species stopped")

    ############
    # DSDrender
    ############

    def build_path(self, points):
        # https://stackoverflow.com/a/63019853
        factor = 0.1
        path = QPainterPath(points[0])
        cp1 = points[0]
        for p, current in enumerate(points[1:-1], 1):
            # previous segment
            source = QLineF(points[p - 1], current)
            # next segment
            target = QLineF(current, points[p + 1])
            targetAngle = target.angleTo(source)
            if targetAngle > 180:
                angle = (source.angle() + source.angleTo(target) / 2) % 360
            else:
                angle = (target.angle() + target.angleTo(source) / 2) % 360

            revTarget = QLineF.fromPolar(source.length() * factor, angle + 180).translated(current)
            cp2 = revTarget.p2()

            if p == 1:
                path.quadTo(cp2, current)
            else:
                # use the control point "cp1" set in the *previous* cycle
                path.cubicTo(cp1, cp2, current)

            revSource = QLineF.fromPolar(target.length() * factor, angle).translated(current)
            cp1 = revSource.p2()

        # the final curve, that joins to the last point
        path.quadTo(cp1, points[-1])
        return path

    def add_graph_to_scene_curve(self, view, species_dict, scene):
        """
        Renders species on the given view

        :param view: QGraphicsView object where the species will be rendered
        :param species_dict: species to be rendered
        :return:
        """
        height = 0

        for name, species in species_dict.items():
            self.print_log("Loaded species: " + name)
            graph_group = QGraphicsItemGroup()
            graph = species.graph
            covalent_bonded = {}
            mid_connection = None

            points = []

            for i, edge in enumerate(graph.g.edges):
                node1 = edge.source()
                node2 = edge.target()
                point1 = (graph.ga.x(node1), graph.ga.y(node1))
                point2 = (graph.ga.x(node2), graph.ga.y(node2))

                if i == 0:
                    points.append(QPointF(point1[0], point1[1]))

                connection_id = str(graph.ga.label(edge))
                # hydrogen connection
                hydrogen_marker = connection_id.find('!')
                covalent_marker = connection_id.find('$')
                # covalent connection
                if covalent_marker != -1:
                    idx = connection_id.find('$', connection_id.find('$') + 1) + 1
                    if hydrogen_marker != -1 and hydrogen_marker > covalent_marker:
                        connection = get_element(connection_id[idx:hydrogen_marker])
                    else:
                        connection = get_element(connection_id[idx:])
                    if type(connection) is Loop:
                        mid_connection = [connection, point1, point2, prev_point]
                    elif type(connection) is Domain:
                        if mid_connection:
                            # item = LoopGraphicsItem(mid_connection[0], mid_connection[1], mid_connection[2],
                            #                         mid_connection[3], point2)
                            # graph_group.addToGroup(item)
                            pass
                        if connection.bond in covalent_bonded:
                            item = BondGraphicsItem(covalent_bonded[connection.bond], [point1, point2],
                                                    connection.bond)
                            graph_group.addToGroup(item)
                            pass
                        else:
                            covalent_bonded[connection.bond] = [point1, point2]
                        mid_connection = None
                        color = QColor()
                        color.setNamedColor(self.ui_model.colors[connection.get_name_stem()])
                        points.append(QPointF(point2[0], point2[1]))
                        # item = DomainGraphicsItem(point1, point2, color, connection.name, connection.last)
                    elif type(connection) is Overhang:
                        mid_connection = None
                        # item = OverhangGraphicsItem(connection, point1, point2)
                        points.append(QPointF(point2[0], point2[1]))

                # graph_group.addToGroup(item)
                prev_point = point1

            path = self.build_path(points)
            path_item = QGraphicsPathItem()
            path_item.setPath(path)
            graph_group.addToGroup(path_item)

            # add species' name
            name_item = QGraphicsSimpleTextItem(species.name)
            name_item.setPos(graph_group.boundingRect().left() - 20, graph_group.boundingRect().top() - 20)
            name_item.setPen(QPen(Qt.black))
            name_item.setFont(QFont('Arial', 18, QFont.Bold))
            graph_group.addToGroup(name_item)

            # move the species to the right height
            translate = QTransform()
            dx = -graph_group.boundingRect().left()
            dy = -graph_group.boundingRect().top()
            dy += height
            translate.translate(dx, dy)
            graph_group.setTransform(translate)
            height += 1.25 * graph_group.boundingRect().height()

            # add species
            scene.addItem(graph_group)

        view.setScene(scene)

    def add_graph_to_scene(self, view, species_dict, scene):
        """
        Renders species on the given view

        :param view: QGraphicsView object where the species will be rendered
        :param species_dict: species to be rendered
        :return:
        """
        height = 0

        for name, species in species_dict.items():
            self.print_log("Loaded species: " + name)
            graph_group = QGraphicsItemGroup()
            graph = species.graph
            prev_point = mid_connection = None
            covalent_bonded = {}

            for edge in graph.g.edges:
                node1 = edge.source()
                node2 = edge.target()
                point1 = (graph.ga.x(node1), graph.ga.y(node1))
                point2 = (graph.ga.x(node2), graph.ga.y(node2))

                connection_id = str(graph.ga.label(edge))
                # hydrogen connection
                hydrogen_marker = connection_id.find('!')
                covalent_marker = connection_id.find('$')
                # if hydrogen_marker != -1:
                #     item = BondGraphicsItem(point1, point2, connection_id)
                #     graph_group.addToGroup(item)
                # covalent connection
                if covalent_marker != -1:
                    idx = connection_id.find('$', connection_id.find('$') + 1) + 1
                    if hydrogen_marker != -1 and hydrogen_marker > covalent_marker:
                        connection = get_element(connection_id[idx:hydrogen_marker])
                    else:
                        connection = get_element(connection_id[idx:])
                    if type(connection) is Loop:
                        mid_connection = [connection, point1, point2, prev_point]
                    elif type(connection) is Domain:
                        if mid_connection:
                            item = LoopGraphicsItem(mid_connection[0], mid_connection[1], mid_connection[2],
                                                    mid_connection[3], point2)
                            graph_group.addToGroup(item)
                        if connection.bond in covalent_bonded:
                            item = BondGraphicsItem(covalent_bonded[connection.bond], [point1, point2],
                                                    connection.bond)
                            graph_group.addToGroup(item)
                            # pass
                        else:
                            covalent_bonded[connection.bond] = [point1, point2]
                        mid_connection = None
                        color = QColor()
                        color.setNamedColor(self.ui_model.colors[connection.get_name_stem()])
                        item = DomainGraphicsItem(point1, point2, color, connection.name, connection.last)
                    elif type(connection) is Overhang:
                        mid_connection = None
                        item = OverhangGraphicsItem(connection, point1, point2)

                graph_group.addToGroup(item)
                prev_point = point1

            # vertices for the ends of the domains
            # for node in graph.g.nodes:
            #     item = QGraphicsEllipseItem(graph.ga.x(node)-3, graph.ga.y(node)-3, 6, 6)
            #     brush = QBrush()
            #     item.setBrush(Qt.black)
            #     graph_group.addToGroup(item)

            # desired position of the paired domains
            # for node in graph.g.nodes:
            #     pair_locations = graph.ga.label(node).split(" ")
            #
            #     i = 0
            #     while i < len(pair_locations)-1:
            #         if len(pair_locations[i]) == 0 or pair_locations[i][0] == '!':
            #             i += 1
            #             pass
            #         item = QGraphicsEllipseItem(float(graph.ga.x(node))+float(pair_locations[i]), float(graph.ga.y(node))+float(pair_locations[i+1]), 6, 6)
            #         item.setBrush(Qt.black)
            #         graph_group.addToGroup(item)
            #         item = QGraphicsLineItem(float(graph.ga.x(node)), float(graph.ga.y(node)),
            #                                  float(graph.ga.x(node)) + float(pair_locations[i]),
            #                                     float(graph.ga.y(node)) + float(pair_locations[i + 1]))
            #         graph_group.addToGroup(item)
            #         i += 2

            # add species' name
            name_item = QGraphicsSimpleTextItem(species.name)
            name_item.setPos(graph_group.boundingRect().left() - 20, graph_group.boundingRect().top() - 20)
            name_item.setPen(QPen(Qt.black))
            name_item.setFont(QFont('Arial', 18, QFont.Bold))
            graph_group.addToGroup(name_item)

            # move the species to the right height
            translate = QTransform()
            dx = -graph_group.boundingRect().left()
            dy = -graph_group.boundingRect().top()
            dy += height
            translate.translate(dx, dy)
            graph_group.setTransform(translate)
            height += 1.25 * graph_group.boundingRect().height()

            # add species
            scene.addItem(graph_group)

        view.setScene(scene)

    def show_species(self, view, species_dict):
        scene = QGraphicsScene()
        self.add_graph_to_scene(view, species_dict, scene)

    def show_input_species(self):
        log, errors, graph_errors = self.ui_model.parse_input_species(self.code_text.toPlainText(),
                                                                      self.progress_window)
        if len(errors) == 0:
            if len(log) > 0:
                self.print_log(log[0])
            self.current_rendering = 0
            self.show_species(self.canvas_view, self.ui_model.input_species_dict)
            if len(graph_errors) > 0:
                self.print_errors(graph_errors)
            return True
        else:
            self.print_errors(errors)
            if len(graph_errors) > 0:
                self.print_errors(graph_errors)
            return False

    def show_output_species(self):
        if self.init_species_no:
            log, errors, graph_errors = self.ui_model.parse_output_species(self.text_output.toPlainText(),
                                                                           self.init_species_no, self.progress_window)
            if len(errors) == 0:
                if len(log) > 0:
                    self.print_log(log[0])
                self.current_rendering = 1
                self.show_species(self.canvas_view_2, self.ui_model.output_species_dict)
                if len(graph_errors) > 0:
                    self.print_errors(graph_errors)
                return True
            else:
                self.print_errors(errors)
                if len(graph_errors) > 0:
                    self.print_errors(graph_errors)
                return False
        else:
            self.print_error('Generate the output first!')
            return False

    def show_species_clicked(self):
        self.reset_all()
        self.generate_unlock()
        # self.optimization_unlock()
        self.show_input_species()

    def open_file(self):
        file_dir, _ = QFileDialog.getOpenFileName(self, "Select File", "./res",
                                                  "All Files (*);;Text Files (*.txt)")
        if file_dir:
            self.print_log("Reading file: " + file_dir)
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
        src.utils.config.reset_color()
        self.species_combo.clear()
        self.species_combo.addItem("Choose species")

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
        file_name, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "./res",
                                                   "All Files (*)")
        if file_name:
            file = open(file_name, 'w+')
            file.write(text)
            file.close()

    def save_img_file(self, view):
        file_name, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", ".",
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
        file_name, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", ".",
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

    def print_logs(self, logs):
        for log in logs:
            self.terminal_output_text.append(str(log))
        self.terminal.setCurrentIndex(0)

    def print_output(self, text):
        self.text_output.setText(text)

    def reset_view(self):
        if self.current_rendering == 0:
            if self.canvas_view.scene() is not None:
                self.canvas_view.scene().clear()

            self.input_final_species_render = None
        else:
            if self.canvas_view_2.scene() is not None:
                self.canvas_view_2.scene().clear()

            self.output_final_species_render = None

    def reset_model(self):
        self.ui_model.reset_species()

    def reset_current_model(self, i):
        self.ui_model.reset_species(i)

    def network_species_clicked(self, name):
        self.species_detached_windows.append(SpeciesWindow(self.close_detached_windows, name, self.save_img_file))
        species_dict = {name: self.ui_model.output_species_dict[name]}
        self.species_detached_windows[-1].show()
        self.current_rendering = -1
        self.optimization_finished(species_dict, self.species_detached_windows[-1].view)

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
            input_species_dict[int_species_name] = self.ui_model.output_species_dict[int_species_name]

        for out_species_name in black_edges_out:
            output_species_dict[out_species_name] = self.ui_model.output_species_dict[out_species_name]

        scene = QGraphicsScene()
        arrows = ReactionArrowGraphicsItem(reaction_name, black_reaction_rate, gray_reaction_rate)
        scene.addItem(arrows)

        self.species_detached_windows[-1].view_reaction.setScene(scene)
        self.species_detached_windows[-1].show()

        self.current_rendering = -1

        self.optimization_finished(input_species_dict, self.species_detached_windows[-1].view_input)
        self.optimization_finished(output_species_dict, self.species_detached_windows[-1].view_output)

    def optimization_finished(self, species_dict, view=None):
        self.show_species(view, species_dict)

        self.print_log("Optimization finished")
        self.stop()

    def change_optimization_button(self):
        flag = True
        for flag_value in self.optimizing.values():
            if flag_value:
                flag = False
                break
        self.open_button.setEnabled(flag)

    def stop(self, id=None):
        self.change_optimization_button()
        self.generate_unlock()
        self.simulate_unlock()

    def set_slider_value(self, value):
        if value == 1:
            self.slider_value_label.setText(str(value) + ' iteration')
        else:
            self.slider_value_label.setText(str(value) + ' iterations')

    def set_slider_value2(self, value):
        src.utils.config.INITIAL_ITER_NO = value
        self.slider_value_label2.setText(str(value))

    def change_layout(self, value):
        src.utils.config.STRAIGHT_LINES = value

    def closeEvent(self, a0: QtGui.QCloseEvent):
        for flag_id in self.optimizing.keys():
            self.optimizing[flag_id] = False
        try:
            shutil.rmtree('tmp')
        except OSError:
            pass
        self.close_detached_windows.emit()
        a0.accept()

    def reset_species_combo(self):
        self.species_combo.setCurrentIndex(0)


class QGraphicsDoubleLineItem(QGraphicsItem):
    def __init__(self, start, end, color1, color2):
        QGraphicsItem.__init__(self, parent=None)

        self.mid = [(start[0] + end[0]) / 2, (start[1] + end[1]) / 2]
        self.start = start
        self.end = end
        self.color1 = color1
        self.color2 = color2

    # implementation of QGraphicsItem virtual methods

    def boundingRect(self):
        left = min(self.start[0], self.end[0])
        right = max(self.start[0], self.end[0])
        up = max(self.start[1], self.end[1])
        down = min(self.start[1], self.end[1])

        return QRectF(left, up, right - left, up - down)

    def paint(self, painter, option, widget):
        pen = QPen()
        pen.setWidth(4)
        pen.setColor(QColor(self.color1))
        painter.setPen(pen)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.drawLine(self.start[0], self.start[1], self.mid[0], self.mid[1])

        pen.setColor(QColor(self.color2))
        painter.setPen(pen)
        painter.drawLine(self.mid[0], self.mid[1], self.end[0], self.end[1])
