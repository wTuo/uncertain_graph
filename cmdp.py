import networkx as nx
from networkx.algorithms.connectivity import minimum_st_edge_cut
from networkx.algorithms.flow import build_residual_network, edmonds_karp

import decimal
import copy
import pickle
import os
from collections import deque
import random
import pickle
import itertools
import numpy as np
import pydot

import randomgraph

def gengraph(edgelist, s, d, p):
    g=nx.DiGraph(edgelist)
    # print minimum_st_edge_cut(g,s,d)
    # print nx.minimum_st_edge_cut(g,s,d)
    graphinfo = []
    undetected = []
    nodes = g.nodes()
    for e in g.edges():
        f = e[0]
        t = e[1]
        fneighbor = set(g.successors(f)).union(set(g.predecessors(f)))
        tneighbor = set(g.successors(t)).union(set(g.predecessors(t)))
        c=1
        undetected.append((f, t, p, c))
    graphinfo.append(s)
    graphinfo.append(d)
    graphinfo.append(nodes)
    graphinfo.append(undetected)
# write graphinfo into pklfile
    output = open('pkl/mdpgraphinfo.pkl', 'wb')
    pickle.dump(graphinfo, output)
    output.close()
    return graphinfo


def decinmal2ternary(decinmal,length):
    stateSpace = []  #stateSpace is a list but just represent one state(represented by a ternary number)
    for i in range(length):
        stateSpace.append(decinmal % 3)
        decinmal /= 3
    return ''.join(str(e) for e in stateSpace)  #list to string


def shallow_compare_2strategy(PIa,PIb):
    sta=[]
    stb=[]
    state_a = 3**edgesnum - 1
    state_b = 3**edgesnum - 1
    sta.append(state_a)
    stb.append(state_b)
    while len(sta)!=0 and len(stb) != 0:
        state_a = sta.pop()
        state_b = stb.pop()
        if PIa[state_a] != PIb[state_b]:
            return False
        if PIa[state_a] == -1:
            continue
        e=PIa[state_a]
        sta.append(state_a - int(3**e))
        sta.append(state_a - int(2*(3**e)))
        stb.append(state_b - int(3**e))
        stb.append(state_b - int(2*(3**e)))
    #double check
    if len(sta) ==0 and len(stb) == 0: # this step garentee sta and stb are absolutely same 
        print True
        return True
    else:
        print "double check false"
        return False

def strategy_equivalence(PIa,PIb):
    print "xxxxxxxx"
    mean_ = self_apply_strategy(PIb[0],PIb[1],PIb[2])
    if mut_apply_strategy(PIa[0],PIb[1],PIb[2], mean_):
        return True
    else:
        return False



def compare_while_run(PIa,PIb): #to save memory, just compare two stategy each time while running MDP
    if not shallow_compare_2strategy(PIa[0],PIb[0]) and not strategy_equivalence(PIa,PIb):
        return False
    return True



def compare_all_strategies(PIs): #PIs is the collection of all the strategies
    # strategies = [e[0] for e in PIs] 
    PI_tmp=PIs[0]
    c=0
    for PI in PIs:
        if not shallow_compare_2strategy(PI_tmp[0],PI[0]) and not strategy_equivalence(PI_tmp,PI):
            print "index:", c
            return False
        c+=1
    return True



def vis_PI(PI, undetected, q, title):
    PI_g= pydot.Dot(graph_type='digraph',label=title,fontname="Souce Code Pro", fontsize="10")
    node_id=0
    st=[]
    state = 3**len(undetected) - 1
    st.append(state)
    while len(st) != 0:
        state = st.pop()
        if(q[state] == 0):
            continue
        else:
            state_p= pydot.Node(str(state),label=decinmal2ternary(state,edgesnum),fontsize="1", shape="circle", width="0.2", fixedsize="true")
            fork_p = pydot.Node("forkp_"+str(node_id), shape="point")
            node_id+=1
            PI_g.add_node(state_p)
            PI_g.add_node(fork_p)
            e = PI[state]
        #edge with action lable
            PI_g.add_edge(pydot.Edge(state_p, fork_p,label="("+str(undetected[e][0])+","+str(undetected[e][1])+")",arrowhead="none",fontname="Source Code Pro",fontsize="7", fontcolor="#009933"))

            estate = state - int(3**e)
            mstate = state - int(2*(3**e))
            st.append(estate)
            st.append(mstate)
            # link fork point with 2 states
            estate_p = pydot.Node(str(estate),label=decinmal2ternary(estate,edgesnum),fontsize="1", shape="circle", width="0.2", fixedsize="true")
            mstate_p = pydot.Node(str(mstate),label=decinmal2ternary(mstate,edgesnum),fontsize="1", shape="circle", width="0.2", fixedsize="true")
            PI_g.add_node(estate_p)
            PI_g.add_node(mstate_p)
            PI_g.add_edge(pydot.Edge(fork_p, estate_p, color = "blue"))
            PI_g.add_edge(pydot.Edge(fork_p, mstate_p, color = "red"))
            PI_g.write_pdf("PI-vis.pdf")


def mdp(G, s, d, nodes, existingedges, undetected):

    def getStateSpace(num):   #convert decinmal number to ternary number # 2,1,0 represent undetected,exist,not exist respectivelly
        length = len(undetected)
        stateSpace = []  #stateSpace is a list but just represent one state
        cnt = 0 #cnt represent the number of detected edges 
        for i in range(length):
            stateSpace.append(num % 3)
            if num % 3 != 2:
                cnt += 1
            num /= 3
        return cnt, stateSpace

    def getPI(G, s, d):
        PI = [-1 for item in xrange(3**len(undetected))]
        q = [decimal.Decimal(str(-99999999)) for item in xrange(3**len(undetected))]
        state = [[] for item in xrange(1 + len(undetected))]
        for i in xrange(3**len(undetected)):
            cnt, stateSpace = getStateSpace(i)
            state[cnt].append(i) #state[] represent S_|E|, recording states by using  decimal number
            nodes = G.ubound.nodes()
            ug = nx.DiGraph()
            lg = nx.DiGraph()
            # print g.lbound.edges(), g.ubound.edges()
            for id, item in enumerate(stateSpace):
                if item == 1:
                    # print id, stateSpace
                    ug.add_edge(undetected[id][0], undetected[id][1])
                    lg.add_edge(undetected[id][0], undetected[id][1])
                if item == 2:
                    ug.add_edge(undetected[id][0], undetected[id][1])
            flagl = True
            if s not in lg.nodes() or d not in lg.nodes():
                flagl = False
            flagu = True
            if s not in ug.nodes() or d not in ug.nodes():
                flagu = False
            if (flagl and nx.has_path(lg, s, d)) or (not flagu or not nx.has_path(ug, s, d)):
                # print 'path', lg.edges(), ug.edges()
                q[i] = 0
                PI[i] = -1
        # print 'q[0]', q[0]
        for i in range(1 + len(undetected))[::-1]:
            for j in state[i]:
                if q[j] == 0:
                    continue
                else:
                    cnt, stateSpace= getStateSpace(j)
                    e_star = -1
                    for id, item in enumerate(stateSpace):
                        if item == 2:
                            tmp = decimal.Decimal(str(-undetected[id][3])) + decimal.Decimal(str(undetected[id][2])) * q[j - 3**id] + \
                                decimal.Decimal(str((1 - undetected[id][2]))) * q[j - 2*(3**id)]
                            if q[j] < tmp:
                                e_star = id
                                q[j] = tmp
                    if e_star != -1:
                        PI[j] = e_star
                    else:
                        # print j, q[j]
                        raise
        # for k,v in qm.iteritems():
        #     print k,v
        print "q="+str(undetected[0][2])+",", q[3**len(undetected)-1]
        # cnt = getStateSpace(1)
        return PI, q

    PI,  q = getPI(G, s, d)
    # PIs.append((PI,q,undetected))
    # vis_PI(PI, undetected, q,"p="+str(undetected[0][2]))
    return (PI, q, undetected)

def self_apply_strategy(PI, q, undetected):
    def gen_all_ug(undetected):
        allugs=[]
        for l in range(0, len(undetected)+1):
            for com in itertools.combinations(undetected,l):
                edge_list=[]
                for e in com:
                    edge_list.append((e[0],e[1]));
                g_=nx.DiGraph(edge_list)
                allugs.append(g_)
        return allugs

    def ug_prob(g, undetected):
        def get_prob(e):
            for ue in undetected:
                if e[0]== ue[0] and e[1]==ue[1]:
                    return decimal.Decimal(str(ue[2]))

        es=[] 
        for ue in undetected:
            es.append((ue[0],ue[1]))
        g_o=nx.DiGraph(es)
        p=decimal.Decimal('1.0')
        for e in g_o.edges():
            if e in g.edges():
                p*=get_prob(e)
            else:
                p*=(1-get_prob(e))
        return p

    mean = decimal.Decimal('0.0') 
    allugs = gen_all_ug(undetected)
    for g in allugs:
        cost = decimal.Decimal('0.0')
        state = 3**len(undetected) - 1
        while q[state] != 0:
            e = PI[state]
            if g.has_edge(undetected[e][0], undetected[e][1]):
                state -= int(3**e)
            else:
                state -= int(2*(3**e))
            cost += undetected[e][3]
        mean += cost*ug_prob(g, undetected)
    theory_optimal = decimal.Decimal(str(-q[3**len(undetected)-1]))
    if theory_optimal != mean:
        print "self check false"
        raise
    else:
        return mean

def mut_apply_strategy(PI, q, undetected, mean_):
    def gen_all_ug(undetected):
        allugs=[]
        for l in range(0, len(undetected)+1):
            for com in itertools.combinations(undetected,l):
                edge_list=[]
                for e in com:
                    edge_list.append((e[0],e[1]));
                g_=nx.DiGraph(edge_list)
                allugs.append(g_)
        return allugs

    def ug_prob(g, undetected):
        def get_prob(e):
            for ue in undetected:
                if e[0]== ue[0] and e[1]==ue[1]:
                    return decimal.Decimal(str(ue[2]))

        es=[] 
        for ue in undetected:
            es.append((ue[0],ue[1]))
        g_o=nx.DiGraph(es)
        p=decimal.Decimal('1.0')
        for e in g_o.edges():
            if e in g.edges():
                p*=get_prob(e)
            else:
                p*=(1-get_prob(e))
        return p

    mean = decimal.Decimal('0.0') 
    allugs = gen_all_ug(undetected)
    for g in allugs:
        cost = decimal.Decimal('0.0')
        state = 3**len(undetected) - 1
        while q[state] != 0:
            e = PI[state]
            if g.has_edge(undetected[e][0], undetected[e][1]):
                state -= int(3**e)
            else:
                state -= int(2*(3**e))
            cost += undetected[e][3]
        mean += cost*ug_prob(g, undetected)
    if mean != mean_:
        print "mutual check false"
        print mean, mean_, q[3**len(undetected) - 1]
        # print mean.hex(), mean_.hex(), q[3**len(undetected) - 1].hex()
        return False
    else:
        return True


def process_with_mdp(graphinfo, pklfile):

#read graphinfo from pklfile
    # pkl_file = open(pklfile + '.pkl', 'rb')
    # rgraphinfo = pickle.load(pkl_file)
    # pkl_file.close()
    # graphinfo = copy.deepcopy(rgraphinfo)
    s = graphinfo[0]
    d = graphinfo[1]
    nodes = graphinfo[2]
    undetected = graphinfo[3]
    existingedges = []
    G = randomgraph.Randomgraph(s, d, nodes, existingedges, undetected)
    global PI_template
    if cnt == 1:
        PI_template = mdp(G, s, d, nodes, existingedges, undetected)
    else:
        PI_ = mdp(G, s, d, nodes, existingedges, undetected)
    if cnt >=2 : #can compare
        if not compare_while_run(PI_template,PI_):
            print "a different strategy has been found"
            raise

if __name__ == '__main__':
    # edgelist=[(0,1),(1,2),(2,10),(2,5),(0,3),(3,4),(4,5),(5,10),(0,6),(6,7),(7,8),(8,9),(9,10)]
    # edgelist=[(0,1),(1,2),(2,10),(2,5),(5,10),(0,6),(6,7),(7,8),(8,9),(9,10)]
    # edgelist=[(0,1),(1,2),(2,10),(0,3),(3,4),(4,10),(4,6),(6,7),(7,8), (8,10)]
    # edgelist=[(0,1),(1,2),(2,10),(0,3),(3,4),(4,10),(4,6),(0,5), (5,6), (6,10)]
    # edgelist=[(0,4),(0,5),(4,1),(5,1),(1,2),(2,7),(2,8),(7,3),(8,3),(10,11),(0,12),(0,13),(0,14),(12,10),(13,10),(14,10),(11,16),(11,17),(16,3),(17,3)]
    # edgelist=[(0,1),(1,2),(2,10),(0,3),(3,4),(4,10),(4,6)]
    # edgelist=[(0,1),(1,2),(2,10),(0,3),(3,4),(4,10),(4,6),(0,5),(5,6), (6,10)]
    # edgelist=[(0,1),(1,2),(2,10),(0,3),(3,4),(4,10),(4,6),(6,10)] #type1.
    # edgelist=[(0,1),(1,2),(2,10),(0,3),(3,4),(4,10),(4,6),(6,10),(0,5),(5,6)] #type2.
    # edgelist = [(0,1),(1,9),(0,2),(0,3),(0,4),(2,5),(3,5),(4,5),(5,6),(6,7),(6,8),(7,9),(8,9)]
    # edgelist=[(0,1),(0,3),(3,1),(0,2),(2,3),(2,1)]
    # edgelist=[(0,1),(0,2),(0,3),(1,4),(4,7),(4,8),(7,8),(2,5),(5,8),(3,6),(6,8)] 
    # edgelist=[(0,1),(1,3),(3,5),(5,8),(3,8),(0,2),(2,4),(4,7),(7,8),(4,8),(3,9),(9,10),(10,8)]
    # edgelist=[(0,2),(2,4),(4,7),(7,8),(4,8),(4,6),(6,8),(0,1),(1,3),(3,8),(3,5),(5,8)]
    # edgelist=[(0,2),(2,4),(4,7),(7,8),(4,8),(4,6),(6,9),(9,8),(0,1),(1,3),(3,8),(3,5),(5,8)]
    # edgelist = [(0,1),(1,3),(0,2),(2,3)]
    # edgelist=[(0,1),(1,3),(3,8),(3,5),(5,6),(6,8),(0,2),(2,4),(4,8),(4,7),(7,8)]
    # edgelist=[(0,1),(0,2),(1,6),(1,4),(4,7),(7,6),(2,6),(2,5),(5,6)] 
    # edgelist = [(0,1),(1,3),(0,2),(2,3),(3,4),(4,5),(5,7),(4,6),(6,7)]  #******* symmetry graph
    # edgelist = [(0,1),(1,3),(3,4),(4,5),(5,7),(3,6),(6,7),(0,2),(2,1)]
    # edgelist = [(0,1),(1,2),(2,7),(0,3),(3,4),(4,7),(7,8),(8,9),(8,10),(9,11),(10,11)]


    # edgelist=[(0,1),(1,3),(3,5),(5,8),(3,8),(0,2),(2,4),(4,8),(3,9),(9,10),(10,8)]#_1  
    # edgelist=[(0,1),(1,3),(3,5),(5,8),(3,8),(0,2),(2,4),(4,7),(7,8),(4,8),(3,9),(9,10),(10,8)] #too large to run 
    # edgelist=[(0,1),(1,3),(3,4),(4,5),(5,7),(0,2),(2,3),(4,6),(6,7)]
    # edgelist=[(0,1),(1,2),(0,2)]
    # edgelist=[(0,1),(1,2),(0,3),(3,4),(4,2)]
    # edgelist = [(0,1),(1,3),(3,2),(0,4),(4,5),(5,6),(6,2)]
    edgelist =[(0,1),(1,2),(2,4),(4,5),(0,3),(3,4),(3,5)] #_2, s=0, d=5
    # edgelist =[(0,1),(0,2),(1,3),(3,7),(3,6),(6,7),(3,4),(4,7),(2,5),(5,7)] #_3, s=0, d=7
    # edgelist =[(0,1),(1,6),(6,7),(7,8),(1,8),(1,3),(3,8),(0,2),(2,4),(4,8),(2,8),(2,5),(5,8)] #_4, s=0, d=8
    # edgelist =[(0,1),(1,8),(0,2),(2,4),(4,5),(5,6),(6,8),(0,3),(3,4),(5,7),(7,8)] #_5, s=0, d=8
    # edgelist = [(0,1),(1,3),(3,4),(0,2),(2,4),(1,2),(2,3)] #_6, s=0, d=4

    # edgelist = [(0,1),(1,3),(3,6),(1,6),(0,2),(2,6),(2,4),(4,5),(5,6)] #_7, s=0, d=6
    # edgelist = [(0,2),(2,3),(3,6),(2,6),(0,1),(1,6),(1,4),(4,5),(5,6)] #_7_, s=0, d=6

    # edgelist =[(0,2),(2,6),(6,7),(7,8),(2,8),(2,3),(3,8),(0,1),(1,4),(4,8),(1,8),(1,5),(5,8)] #_4_, s=0, d=8
    s=0
    d=5

    edgesnum =len(edgelist) #a global variable as a substitute for len(undetected)
    # PIs=[]
    PI_template=()
    cnt=1
    for p in np.arange(0.1, 1.0, 0.1):
        graphinfo = gengraph(edgelist,s,d, p)
        process_with_mdp(graphinfo, 'pkl/mdpgraphinfo')
        # print cnt
        cnt+=1
    # res1.close()
    print "all PIs are equal"
    # if compare_strategies(PIs):
    #     print True
    vis_PI(PI_template[0], PI_template[2], PI_template[1], "decision tree")

