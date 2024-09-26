import networkx as nx
from familiarity import FamiliartyModel as Fam
import random
import sys
import matplotlib.pyplot as plt
import numpy as np
from pathpicker import PathPicker

USAGE_MSG = "Usage: main <graph file name>"

if (len(sys.argv) < 2):
    print(f"Not enough arguments. {USAGE_MSG}")
    sys.exit()

if (len(sys.argv) >= 3):
    print(f"Too many arguments. {USAGE_MSG}")
    sys.exit()

inp_file = sys.argv[1]

G = nx.read_adjlist(inp_file, delimiter="\t", create_using=nx.DiGraph)
print(G)

src_size = min(30, int(G.number_of_nodes() / 6))
trg_size = min(30, int(G.number_of_nodes() / 6))

print(f"Initial source and target size: {min(30, np.floor(G.number_of_nodes() / 6))}")

random_nodes = random.sample(tuple(G.nodes), src_size + trg_size)
src_set = set(random_nodes[:src_size])
trg_set = set(random_nodes[src_size:])

model = Fam(G, src_set, trg_set)

init_sigma = model.sigma()
print(f"Initial familiarity: {init_sigma}")

picker = PathPicker(model)

MAX_BUDGET = 12
budgets = np.array([x for x in range(1, MAX_BUDGET+1)])
res = np.array([])

for func in picker.ready_pickers:
    func_name = func.__name__

    for i in range(max(budgets)):
        best_path = func()
        if best_path != None:
            u, v = best_path
            model.graph.add_edge(u, v)
        else:
            print(f"WARNING: No edge found by {func_name} for budget {i}")
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
