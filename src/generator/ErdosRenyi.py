#!/usr/bin/env python3

import random

import networkx as nx

from dataset import *

class ErdosRenyi(AbstractGenerator):
    '''
    A stream graph generator, based on Erdos-Renyi random network model.

    The dataset contains multiple data generated from this generator.  Timesteps of each data
    is a random graph generated from Erdos-Renyi generator.

    Parameters:
        n_vertices: number of vertices
        n_levels:   number of levels
    '''

    GENERATOR_VERSION = 0.1

    def __init__(self):
        super().__init__()

    def generate(self, *, n_vertices = 15, n_levels = 3):
        n_node_pairs = n_vertices * (n_vertices - 1) // 2
        p_min, p_max = (n_vertices + 3) // 4 / n_node_pairs, n_vertices // 2 / n_node_pairs

        return [list(nx.erdos_renyi_graph(n_vertices, random.uniform(p_min, p_max)).edges)
                for _ in range(n_levels)]

    def parameters(self):
        return [
            { 'n_vertices': n, 'n_levels': n_levels }
            for n in range(10, 25+1, 3)
            for n_levels in range(2, 5+1)
            for _ in range(5) ]



if __name__ == '__main__':
    ErdosRenyi().save()

    '''
    d = AbstractDataset.load('ErdosRenyi')
    print(d.format_version, d.kind, d.params, d.date, d.creator, d.doc)
    print(d.dataset[0].params, d.dataset[0].data)
    for data in d.dataset:
        print([len(level) for level in data.data])
    '''
