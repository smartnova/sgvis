#!/usr/bin/env python3

import logging
import sys
import tempfile
import time

from z3 import *

if __name__ == '__main__' and __package__ is None:
    from os import path
    # To ensure the generator import works even with wierd Z3 python paths
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from generator import sgdataset
from generator import SG20190122
from render.render_stream_graph import render_stream_graph

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(message)s',
    handlers=[
        logging.FileHandler('half.log'),
        logging.StreamHandler()])


def Abs(x):
    return If(x >= 0, x, -x)


def split(n_vertices, timesteps):
    optimizer = Optimize()

    partition = [Int('u{}'.format(i)) for i in range(n_vertices)]

    for node in partition:
        optimizer.add(Or(node == 0, node == 1))

    partition_0_len = Int('0_len')
    partition_1_len = Int('1_len')

    optimizer.add(partition_1_len == Sum([If(partition[x] == 1, 1, 0) for x in range(n_vertices)]))
    optimizer.add(partition_0_len == n_vertices - partition_1_len)

    # Keep the size of the partitions within a certain threshold of each other
    size_difference_threshold = int(n_vertices / 5)
    optimizer.add(Abs(partition_0_len - partition_1_len) <= size_difference_threshold)

    edges = sum(timesteps, [])
    print('edges', edges)
    edges_between_partitions = [Int('e{}_{}'.format(i, j)) for i in range(n_vertices) for j in range(n_vertices)]

    def get_edge(u, v):
        for single_edge in edges_between_partitions:
            if str(single_edge) == 'e{}_{}'.format(u, v):
                return single_edge
        raise RuntimeError('Tried finding edge between node ' + str(u) + ' and node ' + str(v)
                           + ', but it did not exist.')

    for edge_pair in edges_between_partitions:
        optimizer.add(Or(edge_pair == 0, edge_pair == 1))

    optimizer.add([Implies(And(partition[x] != partition[y], Or([x, y] in edges, [y, x] in edges)), get_edge(x, y) ==  1)
                  for x in range(n_vertices) for y in range(n_vertices)])
    optimizer.minimize(Sum(edges_between_partitions))

    return optimizer, partition


if __name__ == '__main__':
    t = time.time()
    print('Starting partitioning...')
    dataset = sgdataset.AbstractDataset.load('sample')
    for data in dataset['dataset']:
        params = data['params']
        optimizer, partition = split(params['n_vertices'], data['content'])
        result = optimizer.check()
        if result == sat:
            print('Finished!')
            m = optimizer.model()
            r = [m.evaluate(partition[i]) for i in range(len(partition))]
            d = [(i, x.as_long()) for i, x in enumerate(r)]

            sorted_nodes = list(map(lambda y: y[0], sorted(d, key=lambda x: x[1])))
            print('Result:', m)

            edges = sum(data['content'], [])
            edges = [tuple(e) for e in edges]
            print('Rendering', sorted_nodes, data['content'])
            render_stream_graph(sorted_nodes, data['content'])
        else:
            print('Could not solve')
