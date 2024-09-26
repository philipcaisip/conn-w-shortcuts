import networkx as nx
from familiarity import FamiliartyModel as Fam
import random
import numpy as np

class PathPicker:
    ready_pickers = []

    def __init__(self, fm: Fam):
        self.fm = fm
        self.cutoff = self.fm.graph.number_of_nodes() / 10

        # change this as needed to change what is tested
        self.ready_pickers = [self.greedy, 
                              self.random,
                              self.shortest,
                              self.avg_closeness,
                              self.avg_betweenness]

    def candidate_paths(self):
        rtn_list = []

        complete_graph = nx.complete_graph(self.fm.graph.nodes)

        for s in self.fm.src_set:
            for t in self.fm.trg_set:
                for path in nx.all_simple_edge_paths(complete_graph, s, t, self.cutoff):
                    for edge in path:
                        u, v = edge
                        if not self.fm.graph.has_edge(u, v):
                            rtn_list.append(path)
                            break
        
        return rtn_list
    
    def random(self):
        return random.choice(self.candidate_paths())

    def greedy(self):
        best_sigma = -1
        best_path = []

        candidate_paths = self.candidate_paths()

        sigmas = self.fm.sigma_optm_paths(candidate_paths, 50)

        next_selection_size = int(len(sigmas) / 10)            
        best_idx = np.argpartition(sigmas, -next_selection_size)[-next_selection_size:]

        next_selection = []
        for i in best_idx:
            next_selection.append(candidate_paths[i])

        sigmas = self.fm.sigma_optm_paths(candidate_paths, 150)
        # index of best path in next selection
        best_idx = np.argpartition(sigmas, -1)[-1:]

        return candidate_paths[best_idx]

    def shortest(self):
        best_path = []
        shortest_len = None
        
        for path in self.candidate_paths():
            if shortest_len == None or len(path) < shortest_len:
                shortest_len = len(path)
                best_path = path
        
        return best_path

    def avg_betweenness(self):
        best_btw = -1
        best_path = []

        for path in self.candidate_paths():
            temp_graph = self.fm.graph.copy()
            for edge in path:
                u, v = edge
                if not temp_graph.has_edge(u, v):
                    temp_graph.add_edge(u, v)

            all_betweeness = nx.edge_betweenness_centrality(temp_graph)
            current_btw = 0
            for edge in path:
                current_btw += all_betweeness[edge]
            current_btw /= len(path)

            if current_btw > best_btw:
                best_btw = current_btw
                best_path = path 

        return best_path

    def avg_closeness(self):
        best_clsn = -1
        best_path = []

        for path in self.candidate_paths():
            temp_graph = self.fm.graph.copy()
            for edge in path:
                u, v = edge
                if not temp_graph.has_edge(u, v):
                    temp_graph.add_edge(u, v)

            all_closeness = nx.closeness_centrality(temp_graph)
            
            # loop adds closness of target for each edge, so add the first
            # node's closeness manually
            current_clsn = all_closeness[path[0][0]]
            for edge in path:
                _, v = edge
                current_clsn += all_closeness[v]
            current_clsn /= len(path) + 1

            if current_clsn > best_clsn:
                best_clsn = current_clsn
                best_path = path 

        return best_path
