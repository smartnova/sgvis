#!/usr/bin/env python3

import json
import logging
import os
import sys
import tempfile
import time

from z3 import *

if __name__ == '__main__' and __package__ is None:
    from os import path
    # To ensure the generator import works even with wierd Z3 python file_paths
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from generator import sgdataset
from optimize import simple, logger
from partition.half import apply_partitioning
from render.render_stream_graph import render_stream_graph


def Abs(x):
    return If(x >= 0, x, -x)


# Input: stream graph to be split into smaller, as-loosely-as-possible connected subgraphs
# Output: list of unmerged, unsorted subgraphs on the form defined in partition/half.py's format_partitioning_output()
def recursively_partitition(stream_graph):
    print()
    if stream_graph['n_edges'] <= 11:
        return [stream_graph]
    else:
        halves = apply_partitioning(stream_graph['unordered_nodes'], stream_graph['timesteps'])
        return recursively_partitition(halves[0]) + recursively_partitition(halves[1])


def sort_partitions_internally(partitions):
    solutions = []
    for partition in partitions:
        problem = simple.constraint_system(partition['unordered_nodes'], partition['timesteps'])
        solution = simple.solve(problem)
        solution['timesteps'] = partition['timesteps']
        solution['inter_partition_edges'] = partition['inter_partition_edges']
        solutions.append(solution)
    return solutions


def merge_solutions(sorted_partitions, original_timesteps):
    ordered_nodes = []
    for partition in enumerate(sorted_partitions):
        ordered_nodes = ordered_nodes + partition['solution']
    return {'ordered_nodes': ordered_nodes, 'timesteps': original_timesteps}


if __name__ == '__main__':

    datasetname = 'ErdosRenyi'
    dataset = sgdataset.AbstractDataset.load(datasetname)

    for i, data in enumerate(dataset['dataset']):
        # Extract relevant data and render the initial problem
        n_vertices = data['params']['n_vertices']
        original_timesteps = data['content']
        initial_unsorted_nodes = list(range(n_vertices))
        file_path = 'optimize/with_partitioning_svgs/partitioning_'
        render_stream_graph(initial_unsorted_nodes, original_timesteps, file_path + 'initial.svg')

        # Partition the problem binarily until the number of edges is within operational parameters
        initial_partition = apply_partitioning(initial_unsorted_nodes, original_timesteps)
        properly_sized_partitions = recursively_partitition(initial_partition[0]) + recursively_partitition(initial_partition[1])
        for i, p in enumerate(properly_sized_partitions):
            render_stream_graph(p['unordered_nodes'], p['timesteps'], '' + file_path + 'unsorted_' + str(i) + '.svg')
        print('\nDone partitioning!', list(map(lambda x: x['n_edges'], properly_sized_partitions)))
        print(properly_sized_partitions[0])

        # Sort each partition internally
        print('Sorting partitions...')
        sorted_partitions = sort_partitions_internally(properly_sized_partitions)
        print('Sorted!')
        for p in sorted_partitions:
            render_stream_graph(p['solution'], p['timesteps'], '' + file_path + 'sorted_' + str(i) + '.svg')

        # Merge the sorted partitions back together
        merged_partitions = merged_partitions(sorted_partitions, original_timesteps)  # TODO
        print('merged_partitions', merged_partitions)
        render_stream_graph(merged_partitions['ordered_nodes'], merged_partitions['timestamps'], path + 'final.svg')

    logger.logger(datasetname)
