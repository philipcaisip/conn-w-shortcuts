import networkx as nx
from familiarity import FamiliartyModel as Fam
import random
import numpy as np

class ShortcutPicker:
    ready_pickers = []

    def __init__(self, fm: Fam, restricted=False):
        self.fm = fm
        self.restricted = restricted

        if self.restricted:
            print("WARNING: picker running in restrcted mode")

        # change this as needed to change what is tested
        self.ready_pickers = [self.greedy, 
                              self.random,
                              self.betweenness,
                              self.closeness,
                              self.degree]


    def non_edges(self):
        rtn = []

        for s in self.fm.graph.nodes(): 
            for t in self.fm.graph.nodes():
                if not self.fm.graph.has_edge(s, t):
                    rtn.append((s, t))

        return rtn
    
    def non_edges_between_st(self):
        rtn = []

        for s in self.fm.src_set:
            for t in self.fm.trg_set:
                if not self.fm.graph.has_edge(s, t):
                    rtn.append((s, t))

        return rtn

    def greedy(self):
        best_shortcut = None
        best_sigma = -1

        if self.restricted:
            candidates = self.non_edges_between_st()
        else:
            candidates = self.non_edges()

        sigmas = self.fm.sigma_optm(candidates)

        for i in range(len(sigmas)):
            if sigmas[i] > best_sigma:
                best_sigma = sigmas[i]
                best_shortcut = candidates[i]

        return best_shortcut

    def random(self):
        if self.restricted:
            candidates = self.non_edges_between_st()
        else:
            candidates = self.non_edges()
                
        return random.choice(tuple(candidates))

    def betweenness(self):
        best_shortcut = None
        best_betweeness = -1
        
        if self.restricted:
            candidates = self.non_edges_between_st()
        else:
            candidates = self.non_edges()

        for shortcut in candidates:
            # TODO optimise by just calcing the one edge

            u, v = shortcut
            temp_graph = self.fm.graph.copy()
            temp_graph.add_edge(u, v)
            all_betweeness = nx.edge_betweenness_centrality(temp_graph)
            if all_betweeness[shortcut] > best_betweeness:
                best_shortcut = shortcut
                best_betweeness = all_betweeness[shortcut]

        return best_shortcut

    def closeness(self):
        best_shortcut = None
        best_closeness = -1

        if self.restricted:
            candidates = self.non_edges_between_st()
        else:
            candidates = self.non_edges()

        for shortcut in candidates:
            u, v = shortcut

            temp_graph = self.fm.graph.copy()
            temp_graph.add_edge(u, v)
            all_closeness = nx.closeness_centrality(temp_graph)

            new_closeness = all_closeness[u] + all_closeness[v]
            if new_closeness > best_closeness:
                best_closeness = new_closeness
                best_shortcut = shortcut

        return best_shortcut

    def degree(self):
        best_shortcut = None
        best_deg_sum = -1

        # form in-degree map
        subset_indeg = {}
        for node in self.fm.graph.nodes:
            for s in self.fm.src_set:
                if (s, node) in self.fm.graph.edges:
                    subset_indeg[node] = subset_indeg.get(node, 0) + 1

        # form out-degree 
        subset_outdeg = {}
        for node in self.fm.graph.nodes:
            for t in self.fm.trg_set:
                if (node, t) in self.fm.graph.edges:
                    subset_outdeg[node] = subset_outdeg.get(node, 0) + 1

        if self.restricted:
            candidates = self.non_edges_between_st()
        else:
            candidates = self.non_edges()

        for shortcut in candidates:
            u, v = shortcut
            new_deg_sum = subset_indeg.get(u, -1) + subset_outdeg.get(v, -1)
            if new_deg_sum > best_deg_sum:
                best_shortcut = shortcut
                best_deg_sum = new_deg_sum

        return best_shortcut
