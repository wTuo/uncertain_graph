import networkx as nx

class Randomgraph(object):

    def __init__(self, s, d, nodes, existingedges, undetected):
        self.ubound = nx.Graph()  # Upperbound, in which all
        # undetected edges are considerred connected.
        self.lbound = nx.Graph()  # Lowerbound, in which \
        # all undetected edges are considerred unconnected.
        self.dubound = nx.DiGraph()
        self.dlbound = nx.DiGraph()
        self.src = s
        self.dst = d  # The connectivity is detected between
        # source and destination.
        for n in nodes:
            self.ubound.add_node(n)
            self.lbound.add_node(n)
            self.dubound.add_node(n)
            self.dlbound.add_node(n)
        for e in existingedges:
            self.ubound.add_edge(e[0], e[1])
            self.lbound.add_edge(e[0], e[1])
            self.dubound.add_edge(e[0], e[1])
            self.dlbound.add_edge(e[0], e[1])
        for e in undetected:
            self.ubound.add_edge(e[0], e[1])
            self.dubound.add_edge(e[0], e[1])

    def __del__(self):
        self.src = -1
        self.dst = -1
        self.ubound.clear()
        self.lbound.clear()
        self.dubound.clear()
        self.dlbound.clear()

    def addedge(self, e):
        self.ubound.add_edge(e[0], e[1])
        self.lbound.add_edge(e[0], e[1])
        self.dubound.add_edge(e[0], e[1])
        self.dlbound.add_edge(e[0], e[1])

    def removeedge(self, e):
        if (self.ubound.has_edge(e[0], e[1])):
            self.ubound.remove_edge(e[0], e[1])
        if (self.dubound.has_edge(e[0], e[1])):
            self.dubound.remove_edge(e[0], e[1])
        if (self.lbound.has_edge(e[0], e[1])):
            self.lbound.remove_edge(e[0], e[1])
        if (self.dlbound.has_edge(e[0], e[1])):
            self.dlbound.remove_edge(e[0], e[1])

    def resetedge(self, e):
        self.ubound.add_edge(e[0], e[1])
        self.dubound.add_edge(e[0], e[1])
        if (self.lbound.has_edge(e[0], e[1])):
            self.lbound.remove_edge(e[0], e[1])
            self.dlbound.remove_edge(e[0], e[1])
