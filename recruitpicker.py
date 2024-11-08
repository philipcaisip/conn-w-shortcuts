import networkx as nx
from familiarity import FamiliartyModel as Fam
import random
import numpy as np

class NodeRecruitPicker:
    ready_pickers = []

    def __init__(self, fm: Fam):
        self.fm = fm

        # change this as needed to change what is tested
        self.ready_pickers = [self.greedy, 
                              self.random, 
                              self.betweenness_global,
                              self.betweenness_subset,
                              self.closeness_global,
                              self.closeness_subset,
                              self.in_degree,
                              self.out_degree,
                              self.both_degree]
        # self.ready_pickers = [self.betweenness_global]

        self.degree_pickers = [self.in_degree,
                               self.out_degree,
                               self.both_degree]
        
        self.ready_fast_degree_pickers = [self.get_in_degree_maps,
                                          self.get_out_degree_maps,
                                          self.get_both_degree_maps]

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
    
    def betweenness_global(self):
        util_map = nx.betweenness_centrality(self.fm.graph)

        for node in self.fm.src_set:
            del util_map[node]
        for node in self.fm.trg_set:
            del util_map[node]

        return max(util_map, key=util_map.get)

    def closeness_global(self):
        util_map = nx.closeness_centrality(self.fm.graph)

        for node in self.fm.src_set:
            del util_map[node]
        for node in self.fm.trg_set:
            del util_map[node]

        return max(util_map, key=util_map.get)
    
    def betweenness_subset(self):
        util_map = nx.betweenness_centrality_subset(self.fm.graph, 
                                list(self.fm.src_set), list(self.fm.trg_set))

        for node in self.fm.src_set:
            del util_map[node]
        for node in self.fm.trg_set:
            del util_map[node]

        return max(util_map, key=util_map.get)

    def closeness_subset(self):
        util_map = {}

        for node in self.fm.graph.nodes:
            path_length_sum = 0

            if node in self.fm.src_set or node in self.fm.trg_set:
                continue

            for s in self.fm.src_set:
                try:
                    path_length_sum += nx.shortest_path_length(self.fm.graph,
                                                                source=s,
                                                                target=node)
                except:
                    # just add number of nodes in full graph to discourage no paths
                    path_length_sum += self.fm.graph.number_of_nodes()
            for t in self.fm.trg_set:
                try:
                    path_length_sum += nx.shortest_path_length(self.fm.graph,
                                                                source=node,
                                                                target=t)
                except:
                    # just add number of nodes in full graph to discourage no paths
                    path_length_sum += self.fm.graph.number_of_nodes()
                
            # closeness is reciprocal of sum, but just minimise and still gets the best
            util_map[node] = path_length_sum

        return min(util_map, key=util_map.get)
    
    def in_degree(self, hops=1):
        util_map = {}

        for s in self.fm.src_set:
            path_lens = nx.single_source_shortest_path_length(self.fm.graph, s, hops)
            for node in path_lens:
                if node in self.fm.src_set or node in self.fm.trg_set:
                    continue
                util_map[node] = util_map.get(node, 0) + (1 / path_lens[node])

        return max(util_map, key=util_map.get) if len(util_map) > 0 else None
    
    def out_degree(self, hops=1):
        util_map = {}

        for t in self.fm.trg_set:
            path_lens = nx.single_target_shortest_path_length(self.fm.graph, t, hops)
            for node in path_lens:
                if node in self.fm.src_set or node in self.fm.trg_set:
                    continue
                util_map[node] = util_map.get(node, 0) + (1 / path_lens[node])

        return max(util_map, key=util_map.get) if len(util_map) > 0 else None
    
    def both_degree(self, hops=1):
        util_map = {}

        for s in self.fm.src_set:
            path_lens = nx.single_source_shortest_path_length(self.fm.graph, s, hops)
            for node in path_lens:
                if node in self.fm.src_set or node in self.fm.trg_set:
                    continue
                util_map[node] = util_map.get(node, 0) + (1 / path_lens[node])

        for t in self.fm.trg_set:
            path_lens = nx.single_target_shortest_path_length(self.fm.graph, t, hops)
            for node in path_lens:
                if node in self.fm.src_set or node in self.fm.trg_set:
                    continue
                util_map[node] = util_map.get(node, 0) + (1 / path_lens[node])

        return max(util_map, key=util_map.get) if len(util_map) > 0 else None
    
    
    ## time-efficient way of getting multihop degrees
    def get_in_degree_maps(self, hops):
        hop_maps = []  # array to hold maps for 1 hop, then 2, then 3 etc

        # populate hop map
        for _ in range(hops):
            hop_maps.append({})

        for s in self.fm.src_set:
            path_lens = nx.single_source_shortest_path_length(self.fm.graph, s, hops)

            for hop in range(hops):
                for node in path_lens:
                    if node in self.fm.src_set or node in self.fm.trg_set:
                        continue

                    if path_lens[node] <= hops+1:
                        hop_maps[hop][node] = hop_maps[hop].get(node, 0) + (1 / path_lens[node])

        return hop_maps

    def get_out_degree_maps(self, hops):
        hop_maps = []  # array to hold maps for 1 hop, then 2, then 3 etc

        # populate hop map
        for _ in range(hops):
            hop_maps.append({})

        for t in self.fm.trg_set:
            path_lens = nx.single_target_shortest_path_length(self.fm.graph, t, hops)
            path_lens = dict(path_lens)

            for hop in range(hops):
                for node in path_lens:
                    if node in self.fm.src_set or node in self.fm.trg_set:
                        continue

                    if path_lens[node] <= hops+1:
                        hop_maps[hop][node] = hop_maps[hop].get(node, 0) + (1 / path_lens[node])

        return hop_maps

    def get_both_degree_maps(self, hops):
        hop_maps = []  # array to hold maps for 1 hop, then 2, then 3 etc

        # populate hop map
        for _ in range(hops):
            hop_maps.append({})

        for s in self.fm.src_set:
            path_lens = nx.single_source_shortest_path_length(self.fm.graph, s, hops)

            for hop in range(hops):
                for node in path_lens:
                    if node in self.fm.src_set or node in self.fm.trg_set:
                        continue

                    if path_lens[node] <= hops+1:
                        hop_maps[hop][node] = hop_maps[hop].get(node, 0) + (1 / path_lens[node])

        for t in self.fm.trg_set:
            path_lens = nx.single_target_shortest_path_length(self.fm.graph, t, hops)
            path_lens = dict(path_lens)

            for hop in range(hops):
                for node in path_lens:
                    if node in self.fm.src_set or node in self.fm.trg_set:
                        continue

                    if path_lens[node] <= hops+1:
                        hop_maps[hop][node] = hop_maps[hop].get(node, 0) + (1 / path_lens[node])

        return hop_maps
    