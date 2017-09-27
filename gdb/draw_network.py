import pydot
import pickledb

def nodes_from_edgelist(edgelist):
    nodes=[]
    for e in edgelist:
        if e[0] not in nodes:
            nodes.append(e[0])
        if e[1] not in nodes:
            nodes.append(e[1])
    return nodes


if __name__== "__main__":
    # edgelist = [(0,1),(1,3),(3,5),(5,8),(3,8),(3,9),(9,10),(10,8),(0,2),(2,4),(4,8)] #_1, s=0, d=8
    # edgelist =[(0,1),(1,2),(2,4),(4,5),(0,3),(3,4),(3,5)] #_2, s=0, d=5
    # edgelist =[(0,1),(0,2),(1,3),(3,7),(3,6),(6,7),(3,4),(4,7),(2,5),(5,7)] #_3, s=0, d=7
    # edgelist =[(0,1),(1,6),(6,7),(7,8),(1,8),(1,3),(3,8),(0,2),(2,4),(4,8),(2,8),(2,5),(5,8)] #_4, s=0, d=8
    # edgelist =[(0,1),(1,8),(0,2),(2,4),(4,5),(5,6),(6,8),(0,3),(3,4),(5,7),(7,8)] #_5, s=0, d=8
    # edgelist = [(0,1),(1,3),(3,4),(0,2),(2,4),(1,2),(2,3)] #_6, s=0, d=4
    edgelist = [(0,1),(1,3),(3,6),(1,6),(0,2),(2,6),(2,4),(4,5),(5,6)] #_7, s=0, d=6

    s=0
    d=6
    tp='_7'

    network = pydot.Dot(graph_type='digraph')
    for e in edgelist:
        na = pydot.Node(str(e[0]),label=str(e[0]),fontsize="7", shape = "circle", width= "0.2", fixedsize="true",style="none" if s != e[0] else "filled",fillcolor="none" if s != e[0] else "green")
        nb = pydot.Node(str(e[1]),label=str(e[1]),fontsize="7", shape = "circle", width= "0.2", fixedsize="true", style="none" if d != e[1] else "filled",fillcolor="none" if d != e[1] else "red")
        network.add_node(na)
        network.add_node(nb)
        network.add_edge( pydot.Edge(na, nb))
        network.write_pdf(str(tp)+".pdf")

    db= pickledb.load("networks.db", True)
    db.set(tp,(edgelist, s, d))
