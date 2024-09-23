import networkx as nx
from familiarity import FamiliartyModel as Fam
from pathpicker import PathPicker
import random
import sys
import matplotlib.pyplot as plt
import numpy as np

USAGE_MSG = "Usage: main <graph file name> <mode>"
MODES = ["RESTRICTED", "PATHS", "BASE"]

if (len(sys.argv) <= 2):
    print(f"Not enough arguments. {USAGE_MSG}")
    sys.exit()

inp_file = sys.argv[1]
