import os

import matplotlib.pyplot as plt
import networkx as nx
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtSvg import QGraphicsSvgItem
from numpy import linspace

from DSDVis.utils.config import euclidean_dist


class Network:
    """
    Class for generating and storing information on the chemical reaction network
    """
    def __init__(self, parent=None, graph=None, species_ids=None, width=10, height=10, dpi=96, render_option='Tree',
                 init_species_no=0):
        self.graph = graph
        self.fig_width = width
        self.fig_height = height

        self.fig = plt.Figure(figsize=(width, height), dpi=dpi, tight_layout=True)
        self.fig.clf()
        self.fig.gca().margins(0)
        self.fig.gca().set_frame_on(False)

        self.species_ids = species_ids
        self.init_species_no = init_species_no

        self.error = None
        if render_option == 'Tree':
            self.pos = nx.drawing.nx_agraph.graphviz_layout(self.graph, prog='dot')
        elif render_option == 'Kamada-Kawai':
            self.pos = nx.kamada_kawai_layout(self.graph, scale=10)
        elif render_option == 'Planar':
            try:
                self.pos = nx.planar_layout(graph)
            except nx.exception.NetworkXException:
                self.error = "Network is not planar!"
        elif render_option == 'Spring':
            self.pos = nx.spring_layout(graph, k=0.8)

        if self.error is None:
            reactions_ids = list(range(len(species_ids) + 1, len(self.graph.nodes) + 1))
            nodes_labels = nx.get_node_attributes(self.graph, 'text')

            edges_colors = nx.get_edge_attributes(graph, 'color').values()

            nx.draw_networkx_nodes(self.graph, pos=self.pos, nodelist=species_ids[:init_species_no], ax=self.fig.gca(),
                                   node_size=1800, node_color=linspace(0.7, 0.7, init_species_no),
                                   cmap=plt.cm.Oranges, vmin=0, vmax=1)
            nx.draw_networkx_nodes(self.graph, pos=self.pos, nodelist=species_ids[init_species_no:], ax=self.fig.gca(),
                                   node_size=1400, node_color=linspace(0.6, 0.2, len(species_ids) - init_species_no),
                                   cmap=plt.cm.Oranges, vmin=0, vmax=1)
            nx.draw_networkx_nodes(self.graph, pos=self.pos, nodelist=reactions_ids, node_color='#689bbb',
                                   node_shape='H',
                                   node_size=1800, ax=self.fig.gca())
            nx.draw_networkx_labels(self.graph, pos=self.pos, ax=self.fig.gca(), labels=nodes_labels)
            nx.draw_networkx_edges(self.graph, pos=self.pos, ax=self.fig.gca(), node_size=2400,
                                   connectionstyle='arc3, rad = 0.075', edge_color=edges_colors)

            if not os.path.exists('tmp'):
                os.mkdir('tmp')
            self.fig.savefig('tmp/network.svg')
            self.map_coords_to_pix()

            self.species_nodes = {}
            self.reactions_nodes = {}
            for species_id in species_ids:
                self.species_nodes[nodes_labels[species_id]] = self.pos[species_id]
            for reaction_id in reactions_ids:
                self.reactions_nodes[reaction_id] = (nodes_labels[reaction_id], self.pos[reaction_id])

    def get_size(self):
        return self.fig_width * self.fig.dpi, self.fig_height * self.fig.dpi

    def map_coords_to_pix(self):
        for name, position in self.pos.items():
            position = self.fig.gca().transData.transform((position[0], position[1]))
            position[1] = self.fig.dpi * self.fig_height - position[1]
            self.pos[name] = position

    def get_species_nodes_positions(self):
        return self.species_nodes

    def get_reactions_nodes_positions(self):
        return self.reactions_nodes

    def get_adjacent_species(self, reaction_id):
        reaction_name = self.reactions_nodes[reaction_id][0]
        black_edges_in = []
        black_edges_out = []
        black_reaction_rate = None
        # gray_edges_in = []
        # gray_edges_out = []
        gray_reaction_rate = None

        for in_edge in self.graph.in_edges(reaction_id):
            if self.graph.get_edge_data(*in_edge)[0]['color'] == 'black':
                black_edges_in.append(self.graph.nodes[in_edge[0]]['text'])
            # else:
            #     gray_edges_in.append(self.graph.nodes[in_edge[0]]['text'])

        for out_edge in self.graph.out_edges(reaction_id):
            if self.graph.get_edge_data(*out_edge)[0]['color'] == 'black':
                black_edges_out.append(self.graph.nodes[out_edge[1]]['text'])
                black_reaction_rate = self.graph.get_edge_data(*out_edge)[0]['edge_text']
            else:
                #     gray_edges_out.append(self.graph.nodes[out_edge[1]]['text'])
                gray_reaction_rate = self.graph.get_edge_data(*out_edge)[0]['edge_text']

        return reaction_name, \
               black_edges_in, black_edges_out, black_reaction_rate, \
               gray_reaction_rate


def parse_network(species_list, reactions_list, init_species_no):
    """
    Creates a chemical reaction network

    :param species_list: List of all species in the network
    :param reactions_list: List of all reactions in the network with their reactants and products
    :param init_species_no: Number of input species
    :return: networkx graph, list of all species
    """
    G = nx.MultiDiGraph()

    species_ids = [species.id for species in species_list]

    for i, species_id in enumerate(species_ids, 1):
        if i <= init_species_no:
            prefix = "ss"
        else:
            prefix = "sp_"
        G.add_node(i, text=prefix + str(species_id))

    reactions_start = i + 1

    for j, reaction in enumerate(reactions_list, reactions_start):
        add_node = True
        rule = reaction.rule
        input = set()
        output = set()
        for reactant in reaction.reactants:
            input.add(reactant.id)
        for product in reaction.products:
            output.add(product.id)

        for k in range(reactions_start, len(G.nodes) + 1):
            if (rule == 'R3' or rule == 'R4' and G.nodes[k]['text'] == rule) or (
                    rule == 'RB' and G.nodes[k]['text'] == 'RU') or (rule == 'RU' and G.nodes[k]['text'] == 'RB'):
                i_edges = set()
                o_edges = set()
                for i_e in G.in_edges(k):
                    i_edges.add(i_e[0])
                for o_e in G.out_edges(k):
                    o_edges.add(o_e[1])
                if input == o_edges and output == i_edges:
                    for input in reaction.reactants:
                        G.add_edge(input.id, k, color='gray', edge_text=reaction.rate)
                    for output in reaction.products:
                        G.add_edge(k, output.id, color='gray', edge_text=reaction.rate)
                    add_node = False
                    if rule == 'RB' or rule == 'RU':
                        G.nodes[k]['text'] = 'RB/RU'

        if add_node:
            nodes_end = len(G.nodes) + 1
            G.add_node(nodes_end, text=reaction.rule)
            for input in reaction.reactants:
                G.add_edge(input.id, nodes_end, color='black', edge_text=reaction.rate)
            for output in reaction.products:
                G.add_edge(nodes_end, output.id, color='black', edge_text=reaction.rate)

    return G, species_ids


class NetworkSvg(QGraphicsSvgItem):
    """
    Class for holding the svg and the meta data of the network
    """
    def __init__(self, path=None, network=None):
        QGraphicsSvgItem.__init__(self, path, parent=None)
        self._network = network

        svg_width = self.renderer().defaultSize().width()
        width = self._network.fig_width * self._network.fig.dpi
        factor = width / svg_width
        self.svg_height = self._network.get_size()[0]
        self.svg_width = self._network.get_size()[1]
        self.setScale(factor)


class NetworkViewer(QtWidgets.QGraphicsView):
    """
    Class for viewing the network
    Panning and zooming based on:
    https://stackoverflow.com/questions/35508711/how-to-enable-pan-and-zoom-in-a-qgraphicsview
    """
    species_node_clicked = QtCore.pyqtSignal(str)
    reaction_node_clicked = QtCore.pyqtSignal(tuple)

    def __init__(self, parent):
        super(NetworkViewer, self).__init__(parent)
        self._zoom = 0
        self._empty = True

        self._scene = None
        self._network = None
        self._svg = None

        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(255, 255, 255)))
        self.setFrameShape(QtWidgets.QFrame.NoFrame)

    def has_network(self):
        return not self._empty

    def fitInView(self, scale=True):
        if self._svg is not None:
            rect = QtCore.QRectF(0, 0, self._svg.svg_width, self._svg.svg_height)
            self.setSceneRect(rect)
            if self.has_network():
                unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height())
                self.scale(factor, factor)
                self._zoom = 0

    def set_network(self, graph, species_ids, render_option, init_species_no):
        if graph is not None and species_ids is not None:
            self._empty = False
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
            self._scene = QtWidgets.QGraphicsScene(self)
            self._network = Network(graph=graph, species_ids=species_ids, width=1.3 * len(species_ids),
                                    height=1.3 * len(species_ids), render_option=render_option,
                                    init_species_no=init_species_no)
            if self._network.error is not None:
                self.setScene(self._scene)
                return self._network.error
            self._svg = NetworkSvg(path='tmp/network.svg', network=self._network)
            # self._scene.addWidget(self._network)
            self._scene.addItem(self._svg)
            self.setScene(self._scene)
        else:
            self._empty = True
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self._scene = QtWidgets.QGraphicsScene(self)
            self._network = None
            self.setScene(self._scene)
        self.fitInView()

        return None

    def change_network_layout(self, layout_name):
        if layout_name is not None and self.has_network():
            graph = self._network.graph
            species_ids = self._network.species_ids
            init_species_no = self._network.init_species_no
            self.set_network(graph, species_ids, layout_name, init_species_no)
            if self._network.error is not None:
                return self._network.error

    def wheelEvent(self, event):
        if self.has_network():
            if event.angleDelta().y() > 0:
                factor = 1.15
                self._zoom += 1
            else:
                factor = 0.9
                self._zoom -= 1
            if self._zoom > 0:
                self.scale(factor, factor)
            elif self._zoom == 0:
                self.fitInView()
            else:
                self.fitInView()
                self._zoom = 0

    def toggleDragMode(self):
        if self.dragMode() == QtWidgets.QGraphicsView.ScrollHandDrag:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        elif self._network is not None:
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

    def mouseDoubleClickEvent(self, event):
        if not self._empty and self._network.error is None:
            point = self.mapToScene(event.pos()).toPoint()

            species_nodes = self._network.get_species_nodes_positions()
            for node_name, node_position in species_nodes.items():
                dist = euclidean_dist(node_position, [point.x(), point.y()])
                if dist < 20:
                    self.species_node_clicked.emit(node_name)
                    super(NetworkViewer, self).mouseDoubleClickEvent(event)
                    return

            reactions_nodes = self._network.get_reactions_nodes_positions()
            for node_id, node_info in reactions_nodes.items():
                dist = euclidean_dist(node_info[1], [point.x(), point.y()])
                if dist < 20:
                    adjacent_species = self._network.get_adjacent_species(node_id)
                    self.reaction_node_clicked.emit(adjacent_species)
                    super(NetworkViewer, self).mouseDoubleClickEvent(event)
                    return
