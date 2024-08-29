import networkx as nx
import igraph as ig
from familiarity import FamiliartyModel as Fam
import random
import sys
import matplotlib.pyplot as plt
import numpy as np

class PathPicker:
    def __init__(self, fm: Fam):
        self.fm = fm
        self.cutoff = self.fm.graph.number_of_nodes() / 10

    def get_candidate_paths(self):
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
    
    def select_path(self, heur):
        if heur == "RANDOM":
            return random.choice(self.get_candidate_paths())
        
        elif heur == "GREEDY":
            best_sigma = -1
            best_path = []

            for path in self.get_candidate_paths():
                new_edges = []
                for edge in path:
                    u, v = edge
                    if not self.fm.graph.has_edge(u, v):
                        new_edges.append(edge)

                # add edges not already there
                for edge in new_edges:
                    u, v = edge
                    self.fm.graph.add_edge(u, v)

                new_sigma = self.fm.sigma()
                if new_sigma > best_sigma:
                    best_sigma = new_sigma
                    best_path = path

                # remove newly added edges
                for edge in new_edges:
                    u, v = edge
                    self.fm.graph.remove_edge(u, v)

            return best_path
        
        elif heur == "SHORTEST":
            best_path = []
            shortest_len = None
            
            for path in self.get_candidate_paths():
                if shortest_len == None or len(path) < shortest_len:
                    shortest_len = len(path)
                    best_path = path
            
            return best_path
        
        elif heur == "AVG_BETWEENNESS":
            best_btw = -1
            best_path = []

            for path in self.get_candidate_paths():
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
        
        elif heur == "AVG_CLOSNESS":
            best_clsn = -1
            best_path = []

            for path in self.get_candidate_paths():
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
