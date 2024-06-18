import os
import sys
from collections import defaultdict

from matplotlib import pyplot as plt

from src.elements.domain import Domain
from src.elements.graph_exception import GraphException
from src.elements.loop import Loop
from src.optimization.simulated_annealing import optimize
import src.utils.config

# comment for compiling the doc
if len(sys.argv) > 1 and "OGDF_INSTALL_DIR" not in os.environ:
    os.environ["OGDF_INSTALL_DIR"] = sys.argv[1]
elif "OGDF_INSTALL_DIR" not in os.environ:
    os.environ["OGDF_INSTALL_DIR"] = "./ogdf/cmake-build-release"

# uncomment for compiling the doc
# os.environ["OGDF_INSTALL_DIR"] = "../ogdf/cmake-build-release"

from ogdf_python import ogdf, cppinclude

cppinclude("ogdf/planarlayout/PlanarDrawLayout.h")
cppinclude("ogdf/planarity/PlanarizationLayout.h")
cppinclude("ogdf/misclayout/BertaultLayout.h")
cppinclude("ogdf/fileformats/GraphIO.h")
cppinclude("ogdf/planarlayout/PlanarStraightLayout.h")
cppinclude("ogdf/upward/UpwardPlanarizationLayout.h")
cppinclude("ogdf/energybased/TutteLayout.h")
cppinclude("ogdf/orthogonal/OrthoLayout.h")
cppinclude("ogdf/planarlayout/SchnyderLayout.h")
cppinclude("ogdf/basic/extended_graph_alg.h")
cppinclude("ogdf/basic/simple_graph_alg.h")
cppinclude("ogdf/planarity/EmbedderMinDepthMaxFace.h")
cppinclude("ogdf/planarity/EmbedderMaxFace.h")


class Graph:
    """
    Creates a graph representation of a species. Every domain is denoted by two vertices (in the ebginning and the end of the domain) denoting the 3' and 5' end. The edges represent both covalent and hydrogen bonds.
    """

    def __init__(self, species, signals, species_no, stop):
        self.species = species
        # key is domain value is a list of points
        self.points = defaultdict(list)
        self.g = None
        self.ga = None
        self.errors = []

        self.fig, self.ax = plt.subplots()

        self.signals = signals
        self.species_no = species_no
        self.stop = stop

        if not os.path.exists("plots"):
            os.makedirs("plots")

        self.build_graph_from_species()

    def build_graph_from_species(self):
        """
        Creates a graph representation of self.species, checks if the resulting graph is planar. If it is, a planar layout is chosen, an embedding with minimum depth and maximum face is fixed, the lengths of the edges are adjusted and the planar graph is drawn. In the case that graph is not planar, or if the prevoius algorithm failed to draw  the graph without crossings, an orthogonal layout is chosen and the process repeated.
        """
        self.g = ogdf.Graph()
        # label the edges
        # hydrogen bonds: !bond_name
        # covalent bonds: $bond_name$element_id
        self.ga = ogdf.GraphAttributes(self.g, ogdf.GraphAttributes.all)
        self.errors = []

        # same as domain pairs but with lists of graph nodes instead of lists of domain objects
        graph_domain_pairs = defaultdict(list)

        # holds nodes of the loops
        graph_loops = dict()

        # create a node for each domain and connect it with the neighbors in the same strand
        for strand in self.species.get_strands():
            domains = strand.get_domains()
            prev_node = self.g.newNode()
            for i, domain in enumerate(domains):
                node = self.g.newNode()
                # add domain bonding to the graph_domain_pairs
                if type(domain) is Domain and domain.bond[:2] != "-1":
                    graph_domain_pairs[domain.bond].append((prev_node, node))
                elif type(domain) is Loop:
                    graph_loops[domain] = (prev_node, node)
                # connect with neighbors
                edge = self.g.newEdge(prev_node, node)
                self.ga.label[edge] = (
                    "$" + str(domain.bond) + "$" + str(domain.get_id())
                )
                prev_node = node

        # connect the bounded domains
        for bond, nodes in graph_domain_pairs.items():
            first_pair = nodes[0]
            second_pair = nodes[1]
            edge = self.g.searchEdge(first_pair[0], second_pair[1])
            if not edge:
                edge = self.g.newEdge(first_pair[0], second_pair[1])
                self.ga.label[edge] = "!" + str(bond)
            else:
                self.ga.label[edge] += "!" + str(bond)
            edge = self.g.searchEdge(first_pair[1], second_pair[0])
            if not edge:
                edge = self.g.newEdge(first_pair[1], second_pair[0])
                self.ga.label[edge] = "!" + str(bond)
            else:
                self.ga.label[edge] += "!" + str(bond)

        # PlanarDrawLayout accepts only planar graphs, crashes in other case
        # PlanarizationLayout accepts non-planar graphs, but works with the orthogonal layout, so crossings possible
        # check if planar and then embed
        planar = ogdf.isPlanar(self.g)
        try:
            if not planar:
                raise (GraphException(self.species.name + " is not planar"))
            if not src.utils.config.STRAIGHT_LINES:
                raise (GraphException("Non-default layout chosen"))

            # try to minimize the topological depth and maximize the external face
            pl = ogdf.PlanarDrawLayout()
            emb = ogdf.EmbedderMinDepthMaxFace()
            emb.__python_owns__ = False
            pl.setEmbedder(emb)
            pl.call(self.ga)

            # ogdf.GraphIO.write(self.g, "example_oh.gml")
            # ogdf.GraphIO.write(self.ga, "example.svg", ogdf.GraphIO.drawSVG)

            if self.g.numberOfNodes() > 1 and not self.species.is_overhang():
                bl = ogdf.BertaultLayout()
                bl.reqlength(src.utils.config.DOMAIN_LEN / 2.5)
                bl.call(self.ga)
                cross_after = bl.edgeCrossings(self.ga)
                if cross_after != 0:
                    raise GraphException(
                        str(cross_after) + " edge(s) crossing in " + self.species.name
                    )
                energy_history = optimize(
                    self.g,
                    self.ga,
                    graph_domain_pairs,
                    graph_loops,
                    self.signals,
                    self.species_no,
                    self.stop,
                )
            #     self.save_energy_plot(self.species.name, energy_history)
        except GraphException as ge:
            # try to only maximize the external face
            self.errors.append(ge)
            pl = ogdf.PlanarizationLayout()
            orth = ogdf.OrthoLayout()
            orth.bendBound(0)
            orth.__python_owns__ = False
            pl.setPlanarLayouter(orth)
            emb = ogdf.EmbedderMinDepthMaxFace()
            emb.__python_owns__ = False
            pl.setEmbedder(emb)
            pl.call(self.ga)

            if self.g.numberOfNodes() > 1 and not self.species.is_overhang():
                bl = ogdf.BertaultLayout()
                bl.reqlength(src.utils.config.DOMAIN_LEN / 2.5)
                bl.call(self.ga)
                cross_after = bl.edgeCrossings(self.ga)
                self.errors.append(
                    GraphException(
                        "Retry the embedding. "
                        + str(cross_after)
                        + " edge(s) crossing in "
                        + self.species.name
                    )
                )
                energy_history = optimize(
                    self.g,
                    self.ga,
                    graph_domain_pairs,
                    graph_loops,
                    self.signals,
                    self.species_no,
                    self.stop,
                )
                # self.save_energy_plot(self.species.name, energy_history)

    def save_energy_plot(self, name, energy_history):
        """
        Plots the simulated annealing energy optimisation (decomposed into components, see: definition of E) and saves it to the /plots folder

        :param name: Name of the species
        :param energy_history: Array holding the history of all the energy components (for plotting purposes)
        """
        self.ax.margins(0, 0)
        self.ax.set_title(name)
        self.ax.set_xlabel("iterations")
        self.ax.set_ylabel("energy")
        self.ax.set_yscale("log")
        self.ax.plot(energy_history[0], label="total")
        self.ax.plot(energy_history[1], label="loops")
        self.ax.plot(energy_history[2], label="domains")
        self.ax.plot(energy_history[3], label="pairs")
        self.ax.legend(
            bbox_to_anchor=(0, 1.02, 1, 0.2), loc="lower left", borderaxespad=0
        )
        self.fig.savefig(
            "./plots/energy_function_" + str(name) + ".png",
            dpi=200,
            pad_inches=0.1,
            bbox_inches="tight",
        )
        plt.cla()
