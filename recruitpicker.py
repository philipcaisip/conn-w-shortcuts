import networkx as nx
from familiarity import FamiliartyModel as Fam
import random
import sys
import numpy as np

class NodeRecruitPicker:
    ready_pickers = []

    def __init__(self, fm: Fam):
        self.fm = fm

        # change this as needed to change what is tested
        self.ready_pickers = [self.greedy, self.random]

    def greedy(self):
        util_map = self.fm.get_node_to_source_fam_map()
        return max(util_map, key=util_map.get)

    def random(self):
        candidates = set(self.fm.graph.nodes)
        for node in self.fm.src_set:
            candidates.remove(node)
        for node in self.fm.trg_set:
            candidates.remove(node)

        if len(candidates) == 0:
            return None

        return random.choice(list(candidates))


