import networkx as nx
import numpy as np
import random

class CascadingModel:
    LIVE_PROB = 0.1  # default prob that an edge is live for cascade

    def __init__(self, graph, init_nodes=None):
        self.graph = graph
        self.init_nodes = init_nodes  # should be a set of nodes

    def set_init_nodes(self, nodeset):
        self.init_nodes = nodeset

    def cascade(self):
        final_active_nodes = set()

        G_copy = self.graph.copy()
        edges_to_remove = []
        for edge in G_copy.edges():
            if random.random() > self.LIVE_PROB:
                edges_to_remove.append(edge)

        for edge in edges_to_remove:
            u, v = edge
            G_copy.remove_edge(u, v)

        for node in G_copy.nodes():
            for seed in self.init_nodes:
                if nx.has_path(G_copy, seed, node):
                    final_active_nodes.add(node)
                    break
 
        return final_active_nodes

class FamiliartyModel(CascadingModel):
    DEFAULT_SAMPLING_ITERS = 200

    def __init__(self, graph, src_set, trg_set):
        self.src_set = src_set
        self.trg_set = trg_set
        self.init_graph = graph.copy()

        # holds graph with only live edges, not important in construction
        self.live_graph = None

        # init nodes don't matter at this point, they are set later
        super().__init__(graph)

    def sigma(self, full=False):
        return self.sigma_full() if full else self.sigma_sampled()

    def sigma_full(self):
        pass

    def sigma_sampled(self, iters=None):
        if iters == None:
            iters = self.DEFAULT_SAMPLING_ITERS

        total_active_trg = 0

        for _ in range(iters):
            self.set_init_nodes({random.choice(tuple(self.src_set))})

            final_active_nodes = self.cascade()
            
            for node in final_active_nodes:
                if node in self.trg_set:
                    total_active_trg += 1

        return total_active_trg / iters
    
    def sigma_optm(self, shortcuts, iters=None):
        if iters == None:
            iters = self.DEFAULT_SAMPLING_ITERS

        sigmas = np.zeros(len(shortcuts))

        for _ in range(iters):
            self.set_init_nodes({random.choice(tuple(self.src_set))})

            self.make_live_graph()
            default_active_trgs = self.get_active_trg_count()

            for i in range(len(shortcuts)):
                if random.random() > self.LIVE_PROB:
                    u, v = shortcuts[i]
                    self.live_graph.add_edge(u, v)
                    sigmas[i] += self.get_active_trg_count()
                    self.live_graph.remove_edge(u, v)
                else:
                    sigmas[i] += default_active_trgs

        return np.divide(sigmas, iters)

    def sigma_optm_paths(self, paths, iters=None):
        if iters == None:
            iters = self.DEFAULT_SAMPLING_ITERS

        sigmas = np.zeros(len(paths))

        for _ in range(iters):
            self.set_init_nodes({random.choice(tuple(self.src_set))})

            self.make_live_graph()
            default_active_trgs = self.get_active_trg_count()

            for i in range(len(paths)):

                live_edges_added = []
                for shortcut in paths[i]:
                    u, v = shortcut
                    if not self.graph.has_edge(u, v) and random.random() > self.LIVE_PROB:
                        self.live_graph.add_edge(u, v)
                        live_edges_added.append(shortcut)

                sigmas[i] += self.get_active_trg_count()
                for shortcut in live_edges_added:
                    u, v = shortcut
                    self.live_graph.remove_edge(u, v)

        return np.divide(sigmas, iters)
    
    def get_node_to_source_fam_map(self, iters=None):
        # will be a dictionary of nodes with associated new familiarity
        rtn = {} 

        if iters == None:
            iters = self.DEFAULT_SAMPLING_ITERS

        for _ in range(iters):
            self.make_live_graph()

            for node in self.graph.nodes:
                # look at only stray nodes (ie not in either set already)
                if node in self.src_set or node in self.trg_set:
                    continue

                # source node set including new node to add/test
                new_src = self.src_set.copy()
                new_src.add(node)
                
                self.set_init_nodes({random.choice(tuple(new_src))})

                if node in rtn:
                    rtn[node] += self.get_active_trg_count()
                else:
                    rtn[node] = self.get_active_trg_count()

        # normalise by dividing by number of iters
        for item in rtn:
            rtn[item] /= iters

        return rtn
    
    def make_live_graph(self):
        self.live_graph = self.init_graph.copy()

        edges_to_remove = []
        for edge in self.live_graph.edges():
            if random.random() > self.LIVE_PROB:
                edges_to_remove.append(edge)

        for edge in edges_to_remove:
            u, v = edge
            self.live_graph.remove_edge(u, v)

    # this assumes that the live graph has been made/set
    def get_active_trg_count(self):
        total_active_trg = 0

        for trg in self.trg_set:
            for src in self.init_nodes:
                if nx.has_path(self.live_graph, src, trg):
                    total_active_trg += 1
                    break

        return total_active_trg

    def reset(self):
        self.graph = self.init_graph.copy()


if __name__=="__main__":
    CM = CascadingModel(nx.complete_graph(10), {1})
    print(CM.graph.number_of_edges())
    print(CM.cascade())
    print(CM.graph.number_of_edges())

    FM = FamiliartyModel(nx.complete_graph(10), {0, 1, 2}, {6, 7})
    print(FM.sigma_sampled())
