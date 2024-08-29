import sys
import matplotlib.pyplot as plt
import numpy as np

if (len(sys.argv) > 1):
    inp_file = sys.argv[1]

with open(inp_file, "r") as inp:
    line = inp.readline()

    budgets = np.array(line.split(",")[2:])
    budgets = np.append(0, budgets)
    MAX_BUDGET = budgets[-1]

    line = inp.readline()
    while line and not str.isspace(line):
        cols = line.split(",")
        plt.plot(budgets, np.array([float(x.strip()) for x in cols[1:]]), '-', label=cols[0], linewidth=2)
        line = inp.readline()

plt.xticks(np.arange(0, int(MAX_BUDGET)+1, 2))
plt.xlabel("Budget")
plt.ylabel("Network Familiarity")

plt.legend()
plt.show()
