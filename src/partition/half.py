#!/usr/bin/env python3

import logging
import sys
import tempfile
import time
import json

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


def constraint_set(n_vertices, timesteps, size_difference_param):
    optimizer = Optimize()

    partition = [Int('u{}'.format(i)) for i in range(n_vertices)]

    for node in partition:
        optimizer.add(Or(node == 0, node == 1))

    size_difference_threshold = int(n_vertices * size_difference_param)
    print('size_difference_threshold', size_difference_threshold)

    # Partition size difference is given by | n - (2 * length_of_either_partition) |
    optimizer.add(Abs(n_vertices - 2 * Sum([partition[x] for x in range(n_vertices)]))
                  <= size_difference_threshold)

    edges = sum(timesteps, [])
    number_of_cross_partition_edges = Sum([Abs(partition[x] - partition[y]) for [x, y] in edges])
    optimizer.minimize(number_of_cross_partition_edges)

    return optimizer, partition


"""
Output format: 
[
  {
    'unordered_nodes': [3, 4, 8, 10, ...],
    'timesteps': [[3, 4], [8, 10], ...],
    'n_edges': 30
  },
  {
    'unordered_nodes': [...], 
    ...
  }
]
"""
def format_partitioning_output(unsorted_nodes, timesteps, optimizer, partition):
    m = optimizer.model()
    r = [m.evaluate(partition[i]) for i in range(len(partition))]
    d = [(unsorted_nodes[i], x.as_long()) for i, x in enumerate(r)]
    nodes_sorted_into_partitions = list(map(lambda y: y[0], sorted(d, key=lambda x: x[1])))

    partition_0_nodes = [x[0] for x in d if x[1] == 0]
    partition_1_nodes = [x[0] for x in d if x[1] == 1]

    partition_0_timesteps = []
    partition_1_timesteps = []
    inter_partition_edges = []

    for timestamp, edge_set in enumerate(timesteps):
        for l in [partition_0_timesteps, partition_1_timesteps, inter_partition_edges]:
            l.append([])

        for edge in edge_set:
            u = edge[0]
            v = edge[1]
            if u in partition_0_nodes and v in partition_0_nodes:
                partition_0_timesteps[timestamp].append(edge)
            elif u in partition_1_nodes and v in partition_1_nodes:
                partition_1_timesteps[timestamp].append(edge)
            else:
                inter_partition_edges[timestamp].append(edge)

    formatted_partitions = {
        'partitions': [
            {
                'unordered_nodes': partition_0_nodes,
                'timesteps': partition_0_timesteps,
                'n_edges': len(sum(partition_0_timesteps, []))
            },
            {
                'unordered_nodes': partition_1_nodes,
                'timesteps': partition_1_timesteps,
                'n_edges': len(sum(partition_1_timesteps, []))
            }
        ],
        'inter_partition_edges': inter_partition_edges
    }
    return formatted_partitions, nodes_sorted_into_partitions


def apply_partitioning(unsorted_nodes, timesteps, size_difference_param=0.2):
    t = time.time()
    print('Starting partitioning...')
    print('Number of nodes:', len(unsorted_nodes))
    print('Number of edges:', len(sum(timesteps, [])))
    optimizer, partition = constraint_set(len(unsorted_nodes), timesteps, size_difference_param)
    result = optimizer.check()
    if result == sat:
        print('Finished!')
        print('Computation took', time.time() - t, 'seconds.')
        formatted_output, nodes_sorted_into_partitions = \
            format_partitioning_output(unsorted_nodes, timesteps, optimizer, partition)
        
        return formatted_output, nodes_sorted_into_partitions
    else:
        return ['Error: Could not solve partitioning problem.']


if __name__ == '__main__':
    datasetname = 'ErdosRenyi'
    dataset = sgdataset.AbstractDataset.load(datasetname)
    for data in dataset['dataset']:
        for threshold in [0.05, 0.1]:
            print('Size different parameter', threshold)
            params = data['params']
            unsorted_input_nodes = list(range(params['n_vertices']))
            formatted, preview = apply_partitioning(unsorted_input_nodes, data['content'], threshold)
            print('n_inter_partition_edges', len(sum(formatted['inter_partition_edges'], [])))
            print()
            render_stream_graph(preview, data['content'])
