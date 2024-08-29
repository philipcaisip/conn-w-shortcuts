import networkx as nx
import igraph as ig
from familiarity import FamiliartyModel as Fam
from pathpicker import PathPicker
import random
import sys
import matplotlib.pyplot as plt
import numpy as np

USAGE_MSG = "Usage: main <graph file name> <selection alg>"
# MODE = "RESTRICTED"
MODE = "PATHS"
# MODE = "BASE"

print("REMEMBER TO CHANGE SRC AND TRG SIZE")

if (len(sys.argv) <= 1):
    # inp_file = "./formattedData/soc-firm-hi-tech.adjlist"
    print(f"No graph file provided. {USAGE_MSG}")
    sys.exit()

inp_file = sys.argv[1]
heur = sys.argv[2] if len(sys.argv) > 2 else None

def non_edges_dir(graph):
    rtn = set()

    for s in graph.nodes(): 
        for t in graph.nodes():
            if not graph.has_edge(s, t):
                rtn.add((s, t))

    return rtn

def non_edges_between_st(fm: Fam):
    rtn = set()

    for s in fm.src_set:
        for t in fm.trg_set:
            if not fm.graph.has_edge(s, t):
                rtn.add((s, t))

    return rtn

def greedy(fm: Fam):
    best_shortcut = None
    best_sigma = -1
    # current_sigma = fm.sigma()

    if MODE == "RESTRICTED":
        print("RESTRICTION APPLIES")
        candidates = non_edges_between_st(fm)
    else:
        candidates = non_edges_dir(fm.graph)

    for shortcut in candidates:
        u, v = shortcut
        fm.graph.add_edge(u, v)
        new_sigma = fm.sigma()
        if new_sigma > best_sigma:
            best_sigma = new_sigma
            best_shortcut = shortcut
        fm.graph.remove_edge(u, v)

    return best_shortcut

def betweeness(fm: Fam):
    best_shortcut = None
    best_betweeness = -1
    
    if MODE == "RESTRICTED":
        print("RESTRICTION APPLIES")
        candidates = non_edges_between_st(fm)
    else:
        candidates = non_edges_dir(fm.graph)

    for shortcut in candidates:
        # temp_graph = ig.Graph(edges=fm.graph.edges(), directed=True)
        # TODO optimise by just calcing the one edge

        u, v = shortcut
        temp_graph = fm.graph.copy()
        temp_graph.add_edge(u, v)
        all_betweeness = nx.edge_betweenness_centrality(temp_graph)
        if all_betweeness[shortcut] > best_betweeness:
            best_shortcut = shortcut
            best_betweeness = all_betweeness[shortcut]

    return best_shortcut
        

def closeness(fm: Fam):
    best_shortcut = None
    best_closeness = -1

    if MODE == "RESTRICTED":
        print("RESTRICTION APPLIES")
        candidates = non_edges_between_st(fm)
    else:
        candidates = non_edges_dir(fm.graph)

    for shortcut in candidates:
        u, v = shortcut

        temp_graph = fm.graph.copy()
        temp_graph.add_edge(u, v)
        all_closeness = nx.closeness_centrality(temp_graph)

        new_closeness = all_closeness[u] + all_closeness[v]
        if new_closeness > best_closeness:
            best_closeness = new_closeness
            best_shortcut = shortcut

    return best_shortcut

def degree(fm: Fam):
    best_shortcut = None
    best_deg_sum = -1

    # form in-degree map
    subset_indeg = {}
    for node in fm.graph.nodes:
        for s in fm.src_set:
            if (s, node) in fm.graph.edges:
                subset_indeg[node] = subset_indeg.get(node, 0) + 1

    # form out-degree 
    subset_outdeg = {}
    for node in fm.graph.nodes:
        for t in fm.trg_set:
            if (node, t) in fm.graph.edges:
                subset_outdeg[node] = subset_outdeg.get(node, 0) + 1

    if MODE == "RESTRICTED":
        print("RESTRICTION APPLIES")
        candidates = non_edges_between_st(fm)
    else:
        candidates = non_edges_dir(fm.graph)

    for shortcut in candidates:
        u, v = shortcut
        new_deg_sum = subset_indeg.get(u, -1) + subset_outdeg.get(v, -1)
        if new_deg_sum > best_deg_sum:
            best_shortcut = shortcut
            best_deg_sum = new_deg_sum

    return best_shortcut

def current_flow(fm: Fam):
    best_shortcut = None
    best_cf = -1

    if MODE == "RESTRICTED":
        print("RESTRICTION APPLIES")
        candidates = non_edges_between_st(fm)
    else:
        candidates = non_edges_dir(fm.graph)

    for shortcut in candidates:
        u, v = shortcut
        temp_graph = fm.graph.copy()
        temp_graph.add_edge(u, v)

        # currently won't work for directed graphs
        all_cf = nx.edge_current_flow_betweenness_centrality(temp_graph)
        if all_cf[shortcut] > best_cf:
            best_shortcut = shortcut
            best_cf = all_cf[shortcut]

    return best_shortcut

def rand(fm: Fam):
    if MODE == "RESTRICTED":
        print("RESTRICTION APPLIES")
        candidates = non_edges_between_st(fm)
    else:
        candidates = non_edges_dir(fm.graph)
            
    return random.choice(tuple(candidates))

G = nx.read_adjlist(inp_file, delimiter="\t", create_using=nx.DiGraph)
# G = nx.read_edgelist(inp_file, create_using=nx.DiGraph)
# if not nx.is_connected(G.to_undirected()):
#     G = G.subgraph(max(nx.strongly_connected_components(G), key=len)).copy()
print(G)

src_size = 5
trg_size = 5

random_nodes = random.sample(tuple(G.nodes), src_size + trg_size)
src_set = set(random_nodes[:src_size])
trg_set = set(random_nodes[src_size:])

model = Fam(G, src_set, trg_set)

init_sigma = model.sigma()
print(f"Initial familiarity: {init_sigma}")

ready_funcs = [rand, greedy, betweeness, closeness, degree]

# budgets = np.array([1, 2, 3, 5, 8, 11])
MAX_BUDGET = 12
budgets = np.array([x for x in range(1, MAX_BUDGET+1)])
# budgets = np.array([1])
res = np.array([])

# analysis based on entire paths
if MODE == "PATHS":
    picker = PathPicker(model)

    ready_heurs = ["RANDOM", "SHORTEST", "AVG_BETWEENNESS", "AVG_CLOSNESS"]

    for heur in ready_heurs:
        for i in range(max(budgets)):
            best_path = picker.select_path(heur)

            for edge in best_path:
                u, v = edge
                model.graph.add_edge(u, v)
            print(model.graph)

            if i+1 in budgets:
                res = np.append(res, model.sigma()) 
        
        model.reset()

          # save raw results (with init sigma) in csv
        with open("raw.csv", "a") as raw:
            raw.write(f"{heur},{init_sigma},{','.join(['%.5f' % s for s in res])}\n")

        print(res)
        plt.plot(np.append(0, budgets), np.append(init_sigma, res), 'o-', label=heur, linewidth=2)

        res = np.array([])

# analysis based on single edges
else:
    for k in range(len(ready_funcs)):
        func_name = ready_funcs[k].__name__

    # for budget in budgets:
        for i in range(max(budgets)):
            best = ready_funcs[k](model)
            if best != None:
                u, v = best
                model.graph.add_edge(u, v)
            else:
                print("No edge found")
            print(model.graph)

            if i+1 in budgets:
                res = np.append(res, model.sigma()) 

        model.reset()

        # save raw results (with init sigma) in csv
        with open("raw.csv", "a") as raw:
            raw.write(f"{func_name},{init_sigma},{','.join(['%.5f' % s for s in res])}\n")

        print(res)
        plt.plot(np.append(0, budgets), np.append(init_sigma, res), 'o-', label=func_name, linewidth=2)
        # plt.show()      # note: showing the plot pauses the program by default

        res = np.array([])
    
plt.xticks(np.arange(0, MAX_BUDGET+1, 2))
plt.xlabel("Budget")
plt.ylabel("Network Familiarity")

plt.legend()
plt.show()
