import operator
import queue

from ...src.basics import lexical_analyzer as lex
from ...src.util import util


class Species:
    """
    Species (DNA Complexes) consists of one or more strands
    """

    id = -1
    '''species id'''

    colormap = {}
    '''map colors to nodes'''

    colorset = {}
    '''set of colors'''

    nodes = []
    '''strand ids in the species'''

    canonicalform = ''
    '''canonical form'''

    strands = []
    '''strands'''

    parsingseq = []
    ''' parsing sequence for deriving canonical form'''

    def __init__(self, nodes, colorset, colormap, strandgraph):
        self.nodes = nodes
        self.colormap = colormap
        self.colorset = colorset
        self.derive_canonical_form(strandgraph)
        self.construct_strands()

    def set_id(self, id):
        self.id = id

    @staticmethod
    def derive_rootmap(nodes):
        rootmap = {}
        for i in nodes:
            rootmap[i] = i
        return rootmap

    def get_starting_vertex(self, strandgraph):
        """
        find the starting vertex to do derive canonical function

        :param strandgraph: a StrandGraph object
        :return: starting vertex id(strand id)
        """
        minlen = 100000
        minc = -1
        for i in self.colorset:
            curlen = len(self.colormap[i])
            if curlen < minlen:
                minlen = curlen
                minc = i
            elif curlen == minlen:
                if minc > i:
                    minc = i
        '''
        minlen = 100000
        minv = -1
        for v in self.colormap[minc]:
            curlen = len(strandgraph.bondgraph.adj[v])
            if curlen < minlen:
                minlen = curlen
                minv = v
        '''

        if len(self.colormap[minc]) == 1:
            return list(self.colormap[minc])[0]

        startingvertex = self.prune(list(self.colormap[minc]), strandgraph)
        '''
        startingvertex = self.prune_starting_vertices(
            self.derive_rootmap(self.colormap[minc]),
            set(),
            self.colormap[minc],
            strandgraph.bondgraph,
            set(strandgraph.V))
        '''
        return startingvertex

    def prune(self, nodes, strandgraph):
        """
        Pruning algorithm for selecting starting vertex
        :param nodes: candidate nodes
        :param strandgraph:
        :return:
        """
        q = [queue.Queue() for _ in range(len(nodes))]
        visited = [[False for i in range(len(strandgraph.V))] for j in range(len(nodes))]
        labelling = ['' for _ in range(len(nodes))]
        bondnum = [0 for _ in range(len(nodes))]
        pendingbond = [[] for _ in range(len(nodes))]

        for i in range(len(nodes)):
            q[i].put(nodes[i])

        while len(nodes) != 1 and not q[0].empty():
            minv = 0
            labelling = ['' for _ in range(len(nodes))]
            delete = []
            kept = [0]
            for i in range(len(nodes)):
                curv = q[i].get()
                visited[i][curv] = True
                labelling[i], q[i], bondnum[i], pendingbond[i] = self.traverse(strandgraph,
                                                                            curv,
                                                                            q[i],
                                                                            bondnum[i],
                                                                            pendingbond[i],
                                                                            '',
                                                                            visited[i])
                if i == minv:
                    continue
                else:
                    if labelling[i] < labelling[minv]:
                        delete = kept
                        kept = [i]
                        minv = i
                    elif labelling[i] == labelling[minv]:
                        kept.append(i)
                        continue
                    else:
                        delete.append(i)
            delete.sort(reverse=True)
            for i in delete:
                nodes.pop(i)
                q.pop(i)
                bondnum.pop(i)
                pendingbond.pop(i)
                visited.pop(i)

        return nodes[0]

    @staticmethod
    def refresh_for_pruning(v, d, n2, c2, d2):
        """
        deprecated
        :param v:
        :param d:
        :param n2:
        :param c2:
        :param d2:
        :return:
        """
        return [v], [d], [n2], [c2], [d2]

    def prune_starting_vertices(self, rootv, prevnodes, nodes, bondgraph, notvisited):
        """
        deprecated
        prune starting vertices (strands) when there are more than one instances of one strand type

        :param rootv: rootmap for nodes (map current nodes to their root nodes)
        :param prevnodes: previous layer of nodes
        :param nodes: current layer of nodes
        :param bondgraph: a BondGraph object
        :param notvisited: list of not visited nodes
        :return: starting vertex
        """
        notvisited = notvisited - prevnodes

        if len(nodes) == 1 or len(notvisited) == 0:
            return rootv[nodes[0]]

        minc = 10000
        curv = []
        nextc = []
        nextv = []
        curd = []
        nextd = []

        for v in nodes:
            bondlen = 0
            info = []

            bonds = bondgraph.merge_bonds_ignoring_nodes(v, prevnodes)
            # TODO: if len(bond)=0
            for i in bonds:
                bondlen += len(i.dom)
                for j in range(0, len(i.dom)):
                    info.append((i.dom[j], i.node2, bondgraph.color[i.node2], i.dom2[j]))

            info.sort(key=operator.itemgetter(0))
            d, n2, c2, d2 = list(zip(*info))

            if bondlen < minc:
                minc = bondlen
                curv, curd, nextv, nextc, nextd = self.refresh_for_pruning(v, d, n2, c2, d2)
            elif bondlen == minc:
                res1 = util.compare(d, curd[0])
                res2 = util.compare(c2, nextc[0])
                res3 = util.compare(d2, nextd[0])
                if res1 == -1:
                    curv, curd, nextv, nextc, nextd = self.refresh_for_pruning(v, d, n2, c2, d2)
                elif res1 == 0:
                    if res2 == -1:
                        curv, curd, nextv, nextc, nextd = self.refresh_for_pruning(v, d, n2, c2, d2)
                    elif res2 == 0:
                        if res3 == -1:
                            curv, curd, nextv, nextc, nextd = self.refresh_for_pruning(v, d, n2, c2, d2)
                        elif res3 == 0:
                            curv.append(v)
                            curd.append(d)
                            nextc.append(c2)
                            nextv.append(n2)
                            nextd.append(d2)

        rootmap = {}
        for i in range(0, len(nextv)):
            rootmap[nextv[i]] = rootv[curv[i]]

        if not isinstance(nodes, set):
            tmpset = set()
            for i in nodes:
                tmpset = tmpset | set(i)
            nodes = tmpset

        return self.prune_starting_vertices(rootmap, nodes, nextv, bondgraph, notvisited)

    @staticmethod
    def check_pendingbond(b, pending):
        """
        check if b is in pending bonds

        :param b: domain
        :param pending: pending bonds
        :return: the bond number if b is in pending bond, -1 otherwise
        """

        for i in range(0, len(pending)):
            if pending[i][0] == b:
                return i
        return -1

    def traverse(self, strandgraph, curv, q, bondnum, pendingbond, canonical, visited):
        """
        traverse the strand and produce a canonical form

        :param strandgraph: a StrandGraph object
        :param curv: current vertex in strandgraph
        :param q: queue for determining if all nodes in species has been encountered
        :param bondnum: number of bonds
        :param pendingbond: list of bonds (in domain level) that are pending to add
        :param canonical: canonical form
        :param visited: boolean list for visiting vertices in species
        :return: canonical form for one strand
        """
        string = '<'
        bondgraph = strandgraph.bondgraph

        E = []
        flag = False
        domlen = len(strandgraph.strands[curv].domains)

        for i in bondgraph.adj[curv]:
            E += i.transform_E()
        E.sort(key=util.sort_e_by_domain)
        cursor = 0

        for i in range(0, domlen):
            domain = strandgraph.strands[curv].domains[i]

            string += domain.name

            if domain.toehold:
                string += '^'

            if domain.comp:
                string += '*'

            if flag:
                if i != domlen - 1:
                    string += ' '
                continue

            if len(E) > 0:
                pos = self.check_pendingbond((curv, i), pendingbond)
                if pos != -1:
                    string += '!' + str(pendingbond[pos][1])
                    pendingbond.pop(pos)
                    E.pop(cursor)
                    if cursor >= len(E):
                        flag = True
                elif not flag and (curv, i) == E[cursor][0]:
                    bondnum += 1
                    string += '!' + str(bondnum)
                    pendingbond.append((E[cursor][1], bondnum))
                    if not visited[E[cursor][1][0]] and not E[cursor][1][0] in q.queue:
                        q.put(E[cursor][1][0])
                    cursor += 1
                    if cursor >= len(E):
                        flag = True
            if i != domlen - 1:
                string += ' '

        string += '>'
        canonical += string
        return canonical, q, bondnum, pendingbond

    def derive_canonical_form(self, strandgraph):
        """
        derive a canonical form for the species

        :param strandgraph: a StrandGraph object
        """
        startingv = self.get_starting_vertex(strandgraph)
        bondnum = 0

        parsingseq = []
        canonical = ''
        pendingbond = []
        q = queue.Queue()
        visited = [False for i in range(0, len(strandgraph.V))]

        q.put(startingv)

        while not q.empty():
            curv = q.get()
            parsingseq.append(curv)
            visited[curv] = True
            canonical, q, bondnum, pendingbond = self.traverse(strandgraph, curv, q, bondnum, pendingbond, canonical, visited)
            if not q.empty():
                canonical += '|'

        self.canonicalform = canonical
        self.parsingseq = parsingseq

    def construct_strands(self):
        """
        reverse construction of strands: canonical form -> strands
        """
        recolormap = {}
        for key, vals in self.colormap.items():
            for val in vals:
                recolormap[val] = key

        strands = []
        l = self.canonicalform.split('|')
        for i in range(0, len(l)):
            strand = lex.lexer_strand(l[i], 0)
            strand.add_color(recolormap[self.parsingseq[i]])
            strands.append(strand)
        self.strands = strands

    def generate_output(self):
        """
        supporting function for txt output

        :return: string of canonical form
        """
        string = ''
        string += str(self.id) + '\n'
        l = self.canonicalform.split('|')
        for i in range(0, len(l)):
            string += l[i] + '\n'
        return string

    '''
    def generate_sites(self):
        sites = []
        
        l = self.canonicalform.split('|')
        for i in range(0, len(l)):
            sites += lex.lexer_site(l[i])
        
        return sites
    '''

