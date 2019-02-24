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

        # The simple solver takes nodes on the form [82, 4, 6, ...], and for whatever reason returns them on the form
        # [4, 0, 1, 2, 3, ...]. Only the "index" of each initial node is taken into consideration. So here, we
        # convert it back. Might be a better solution to change simple.py eventually.
        node_order = solution['solution']
        unordered_nodes = list(map(lambda x: (node_order[x[0]], x[1]), enumerate(partition['unordered_nodes'])))
        solution['solution'] = list(map(lambda y: y[1], sorted(unordered_nodes, key=lambda x: x[0])))

        # We don't use these two for now, but I figure they might be good to keep in the data "going forward" into
        # the algorithm, as we might want to use it for more sophisticated merging at some point.
        solution['timesteps'] = partition['timesteps']
        solution['inter_partition_edges'] = partition['inter_partition_edges']

        solutions.append(solution)
    return solutions


# Very simple merging. Simply looks at each partition in order, and adds the nodes in order to the global set of nodes.
def merge_partitions(sorted_partitions, original_timesteps):
    ordered_nodes = []
    for partition in sorted_partitions:
        ordered_nodes = ordered_nodes + partition['solution']
    return {'ordered_nodes': ordered_nodes, 'timesteps': original_timesteps}


# Main function, applying all the other functions in turn.
def sort_with_partitioning(data):
    t = time.time()
    # Extract relevant data and render the initial problem
    n_vertices = data['params']['n_vertices']
    original_timesteps = data['content']
    initial_unsorted_nodes = list(range(n_vertices))
    file_path = 'optimize/with_partitioning_svgs/partitioning_'
    render_stream_graph(initial_unsorted_nodes, original_timesteps, file_path + 'initial.svg')

    # Partition the problem binarily until the number of edges is within operational parameters
    initial_partition = apply_partitioning(initial_unsorted_nodes, original_timesteps)
    properly_sized_partitions = recursively_partitition(initial_partition[0]) + recursively_partitition(
        initial_partition[1])
    for p in properly_sized_partitions:
        render_stream_graph(p['unordered_nodes'], p['timesteps'], '' + file_path + 'unsorted_' + str(i) + '.svg')
    print('Done partitioning!\nN_edges in each partition:', list(map(lambda x: x['n_edges'], properly_sized_partitions)))

    # Sort each partition internally
    print('\n   Sorting partitions...')
    sorted_partitions = sort_partitions_internally(properly_sized_partitions)
    print('Sorting completed!\n')
    # for p in sorted_partitions:
    # render_stream_graph(p['solution'], p['timesteps'], '' + file_path + 'sorted_' + str(i) + '.svg')

    # Merge the sorted partitions back together
    print('Merging partitions...')
    merged_partitions = merge_partitions(sorted_partitions, original_timesteps)
    print('Merging complete!\n')

    # Finished! Render the result.
    render_stream_graph(merged_partitions['ordered_nodes'], merged_partitions['timesteps'], file_path + 'final.svg')
    print('Sorting of stream graph complete! View the results in the optimize/with_partitioning_svgs folder.')
    print('Total computation took', time.time() - t, 'seconds.')

    all_interpartition_edges = sum(sum(list(map(lambda x: x['inter_partition_edges'], properly_sized_partitions)), []), [])
    print('all_interpartition_edges', all_interpartition_edges)
    unique_interpartition_edges = len(list(set([tuple(e) for e in all_interpartition_edges])))
    percentage_interpartition_edges = int(unique_interpartition_edges * 100 / len(sum(original_timesteps, [])))
    print('The total number of inter-partition, unoptimized edges is', unique_interpartition_edges,
          '({}%).'.format(percentage_interpartition_edges))

    print('\nDebug: n_edges_result', len(sum(merged_partitions['timesteps'], [])), 'n_edges_orig', len(sum(original_timesteps, [])))


if __name__ == '__main__':

    datasetname = 'ErdosRenyi'
    dataset = sgdataset.AbstractDataset.load(datasetname)

    for i, data in enumerate(dataset['dataset']):
        sort_with_partitioning(data)

    logger.logger(datasetname)
