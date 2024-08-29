import networkx as nx
import os

partial_name = "sham"
current_num = 0

out_name = partial_name + ".txt"
while os.path.exists(f".\srcData\{out_name}"):
    current_num += 1
    out_name = partial_name + str(current_num) + ".txt"


with open(f".\srcData\{out_name}", "w") as f:
    print("hohohehe", file=f)
