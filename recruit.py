import networkx as nx
from familiarity import FamiliartyModel as Fam
import random
import sys
import matplotlib.pyplot as plt
import numpy as np
from recruitpicker import NodeRecruitPicker as RecruitPicker

USAGE_MSG = "Usage: main <graph file name> <mode>"

if (len(sys.argv) < 2):
    print(f"Not enough arguments. {USAGE_MSG}")
    sys.exit()

inp_file = sys.argv[1]

# TODO make this more robust against different delimiters
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

picker = RecruitPicker(model)

MAX_BUDGET = 12
budgets = np.array([x for x in range(1, MAX_BUDGET+1)])
res = np.array([])

fig = plt.figure()
ax = plt.subplot(111)

for func in picker.ready_pickers:
    func_name = func.__name__

    for i in range(max(budgets)):
        best_node = func()
        if best_node != None:
            model.src_set.add(best_node)
        else:
            print(f"WARNING: No node found by {func_name} for budget {i}.")
        print(model.graph)
        print(f"Src count: {len(model.src_set)}, Trg count: {len(model.trg_set)}")

        if i+1 in budgets:
            res = np.append(res, model.sigma())

    model.reset()
    # save raw results (with init sigma) in csv
    with open("raw.csv", "a") as raw:
        raw.write(
            f"{func_name},{init_sigma},{','.join(['%.5f' % s for s in res])}\n")

    print(res)
    ax.plot(np.append(0, budgets), np.append(init_sigma, res), 'o-', 
             label=func_name, linewidth=2)
    res = np.array([])

box = ax.get_position()
ax.set_position([box.x0, box.y0 + box.height * 0.1,
                 box.width, box.height * 0.9])

plt.xticks(np.arange(0, MAX_BUDGET+1, 2))
plt.xlabel("Budget")
plt.ylabel("Network Familiarity")

ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
          fancybox=True, shadow=True, ncol=3)

plt.show()
