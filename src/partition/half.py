#!/usr/bin/env python3

import sys
import time
import logging
from z3 import *

if __name__ == '__main__' and __package__ is None:
    from os import path
    # To ensure the generator import works even with wierd Z3 python paths
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from generator import sgdataset
from generator import SG20190122
from optimize import logger
from render.render_stream_graph import render_stream_graph

"""
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(message)s',
    handlers=[
        logging.FileHandler('half.log'),
        logging.StreamHandler()])
"""
logger.setup_logger('ErdosRenyi')


def Abs(x):
    return If(x >= 0, x, -x)


def constraint_set(unordered_nodes, timesteps, size_difference_param):
    optimizer = Optimize()
    n_vertices = len(unordered_nodes)

    partition = [Int('u{}'.format(u)) for u in unordered_nodes]

    for node in partition:
        optimizer.add(Or(node == 0, node == 1))

    size_difference_threshold = int(n_vertices * size_difference_param)

    # Partition size difference is given by | n - (2 * length_of_either_partition) |
    optimizer.add(Abs(n_vertices - 2 * Sum([partition[i] for i in range(n_vertices)]))
                  <= size_difference_threshold)

    edges = sum(timesteps, [])
    number_of_cross_partition_edges = Sum([Abs(partition[unordered_nodes.index(x)]
                                               - partition[unordered_nodes.index(y)]) for [x, y] in edges])
    optimizer.minimize(number_of_cross_partition_edges)

    return optimizer, partition


def format_partitioning_output(unsorted_nodes, timesteps, optimizer, partition):
    m = optimizer.model()
    r = [m.evaluate(partition[i]) for i in range(len(partition))]
    d = [(unsorted_nodes[i], x.as_long()) for i, x in enumerate(r)]
    nodes_sorted_into_partitions = list(map(lambda y: y[0], sorted(d, key=lambda x: x[1])))

    partition_0_nodes = [x[0] for x in d if x[1] == 0]
    partition_1_nodes = [x[0] for x in d if x[1] == 1]

    partition_0_timesteps = []
    partition_1_timesteps = []

    for timestamp, edge_set in enumerate(timesteps):
        for l in [partition_0_timesteps, partition_1_timesteps]:
            l.append([])

        for edge in edge_set:
            u = edge[0]
            v = edge[1]
            if u in partition_0_nodes and v in partition_0_nodes:
                partition_0_timesteps[timestamp].append(edge)
            elif u in partition_1_nodes and v in partition_1_nodes:
                partition_1_timesteps[timestamp].append(edge)

    formatted_partitions = [
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
    ]
    return formatted_partitions


def select_size_difference_param(n_vertices, n_edges):
    return 0.2

    if n_vertices < 20:
        return 0.2
    else:
        return 0.5


def apply_partitioning(unsorted_nodes, timesteps, size_difference_param=0.1):
    t = time.time()
    size_difference_param = select_size_difference_param(len(unsorted_nodes), len(sum(timesteps, [])))
    logging.info('Starting individual partitioning. n_vertices_in: {}, n_edges_in: {}, size_difference_param: {}.'
                 .format(len(unsorted_nodes), len(sum(timesteps, [])), size_difference_param))

    optimizer, partition = constraint_set(unsorted_nodes, timesteps, size_difference_param)
    result = optimizer.check()
    if result == sat:
        formatted_output = format_partitioning_output(unsorted_nodes, timesteps, optimizer, partition)
        logging.info(('Individual partitioning finished. Time elapsed: {}s. n_vertices_1: {}, n_edges_1: {}. ' +
                     'n_vertices_2: {}, n_edges_2: {} ')
                     .format(time.time() - t, len(formatted_output[0]['unordered_nodes']), formatted_output[0]['n_edges'],
                             len(formatted_output[1]['unordered_nodes']), formatted_output[1]['n_edges']))
        return formatted_output
    else:
        raise RuntimeError('Could not solve partitioning problem.')


if __name__ == '__main__':
    datasetname = 'ErdosRenyi'
    dataset = sgdataset.AbstractDataset.load(datasetname)
    for data in dataset['dataset']:
        for threshold in [0.05, 0.1]:
            params = data['params']
            unsorted_input_nodes = list(range(params['n_vertices']))
            formatted = apply_partitioning(unsorted_input_nodes, data['content'], threshold)
            # render_stream_graph(preview, data['content'])

    logger.logger(datasetname)
