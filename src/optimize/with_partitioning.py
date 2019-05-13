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
    # To ensure the generator import works even with wierd Z3 python SVG_FILE_PATHs
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from generator import sgdataset
from optimize import simple, logger
from partition.half import apply_partitioning
from render.render_stream_graph import render_stream_graph


SVG_FILE_PATH = 'optimize/with_partitioning_svgs/partitioning_'

def Abs(x):
    return If(x >= 0, x, -x)


# Input: stream graph to be split into smaller, as-loosely-as-possible connected subgraphs
# Output: list of unmerged, unsorted subgraphs on the form defined in partition/half.py's format_partitioning_output()
def recursively_partitition(stream_graph):
    if stream_graph['n_edges'] <= 12:
        return [stream_graph]
    else:
        halves = apply_partitioning(stream_graph['unordered_nodes'], stream_graph['timesteps'])
        return recursively_partitition(halves[0]) + recursively_partitition(halves[1])


def sort_partitions_internally(partitions):
    logging.info('Starting sorting of partitions.')
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

        solutions.append(solution)
        render_stream_graph(solution['solution'], partition['timesteps'], '' + SVG_FILE_PATH + 'sorted_' + str(i) + '.svg')

    return solutions


# Very simple merging. Simply looks at each partition in order, and adds the nodes in order to the global set of nodes.
def merge_partitions_simple(sorted_partitions, original_timesteps):
    ordered_nodes = []
    for partition in sorted_partitions:
        ordered_nodes = ordered_nodes + partition['solution']
    return {'solution': ordered_nodes, 'timesteps': original_timesteps}


# Formulates the merging problem as a regular stream graph distance minimization problem
def merge_partitions_min_interpartition_distance(sorted_partitions, interpartition_edges):
    nodes_in_partitions = [(j, sorted_partitions[j]['solution']) for j in range(len(sorted_partitions))]

    # Convert all edges like [4, 25] to [0, 2], assuming node 4 is in partition 0 and node 25 is in partition 2.
    for i, timestamp in enumerate(interpartition_edges):
        for j, edge in enumerate(timestamp):
            source_partition = -1
            target_partition = -1
            for k, partition_nodes in nodes_in_partitions:
                if source_partition >= 0 and target_partition >= 0:
                    break
                if edge[0] in partition_nodes:
                    source_partition = k
                if edge[1] in partition_nodes:
                    target_partition = k

            interpartition_edges[i][j] = [source_partition, target_partition]

    partition_indexes = [x[0] for x in nodes_in_partitions]
    logging.info('Attempting simple.py stream graph sort with n_vertices = {} and n_edges = {}.'
                 .format(len(partition_indexes), len(sum(interpartition_edges, []))))
    problem = simple.constraint_system(partition_indexes, interpartition_edges)
    solution = simple.solve(problem)

    render_stream_graph(solution['solution'], interpartition_edges, 'optimize/with_partitioning_svgs/partitioning_smart_merge.svg')
    sorted_nodes = sum(map(lambda y: y[1], sorted(nodes_in_partitions, key=lambda x: solution['solution'].index(x[0]))), [])
    return sorted_nodes


def find_interpartition_directly(partitions, timestamps):
    node_partitions = [x['unordered_nodes'] for x in partitions]

    all_interpartition_edges = []
    unique_interpartition_edges = 0
    for t, timestamp in enumerate(timestamps):
        all_interpartition_edges.append([])
        for edge in timestamp:
            for partition in node_partitions:
                if (edge[0] in partition and edge[1] not in partition) or (edge[1] in partition and edge[0] not in partition):
                    all_interpartition_edges[t].append(edge)
                    unique_interpartition_edges += 1
                    break
    return all_interpartition_edges, unique_interpartition_edges


def find_unconnected_nodes(nodes, timestamps):
    node_is_connected = {node: False for node in nodes}
    edges = sum(timestamps, [])
    for u, v in edges:
        node_is_connected[u] = True
        node_is_connected[v] = True
    return list(filter(lambda x: not node_is_connected[x], nodes))


def get_total_distance(nodes, timestamps):
    total_distance = 0
    for timestamp in timestamps:
        for u, v in timestamp:
            total_distance += abs(nodes.index(u) - nodes.index(v))

    return total_distance


# Main function, applying all the other functions in turn.
def sort_with_partitioning(data):
    t = time.time()

    # Extract relevant data from input parameter into much-used variables
    n_vertices = data['params']['n_vertices']
    original_timesteps = data['content']
    n_edges = len(sum(original_timesteps, []))
    initial_unsorted_nodes = list(range(n_vertices))
    SVG_FILE_PATH = 'optimize/with_partitioning_svgs/partitioning_'

    logging.info('Starting "Sort with partitioning". n_vertices: {}, n_timestamps: {}, n_edges: {}'
                 .format(n_vertices, len(original_timesteps), n_edges))
    logger.log_data({'n_vertices': n_vertices, 'n_edges': n_edges, 'timesteps': original_timesteps}, 'input')

    # Remove nodes that have no edge connections, as they are irrelevant and increase runtime. They are added back
    # in at render time.
    unconnected_nodes = find_unconnected_nodes(initial_unsorted_nodes, original_timesteps)
    relevant_unsorted_nodes = [x for x in initial_unsorted_nodes if x not in unconnected_nodes]

    # Partition the problem binarily until the number of edges is within operational parameters (~12)
    initial_partition = apply_partitioning(relevant_unsorted_nodes, original_timesteps)
    properly_sized_partitions = recursively_partitition(initial_partition[0]) + recursively_partitition(
        initial_partition[1])
    logging.info('Final result of partitioning (n_nodes, n_edges): {}'
                 .format(list(map(lambda x: (len(x['unordered_nodes']), x['n_edges']), properly_sized_partitions))))

    # Sort each partition internally
    sorted_partitions = sort_partitions_internally(properly_sized_partitions)
    logging.info('Sorting of partitions completed.')

    # Merge the sorted partitions back together
    merged_partitions = merge_partitions_simple(sorted_partitions, original_timesteps)
    logging.info('Naive merging of partitions completed.')

    # Finished with naive approach. Render the result.
    sorted_nodes = merged_partitions['solution'] + unconnected_nodes
    render_stream_graph(sorted_nodes, original_timesteps, SVG_FILE_PATH + 'final.svg')
    total_distance = get_total_distance(sorted_nodes, original_timesteps)
    logging.info('Optimization using naive merging finished. Time elapsed: {}s. Total edge distance: {}.'
                 .format(time.time() - t, total_distance))

    # Show some information about interpartition edges, as that's what we want to minimize
    all_interpartition_edges, unique_interpartition_edges = find_interpartition_directly(properly_sized_partitions, original_timesteps)
    percentage_interpartition_edges = int(unique_interpartition_edges * 100 / n_edges)
    logging.info('The total number of inter-partition, unoptimized edges is {} ({}%)'.format(unique_interpartition_edges,
                                                                                            percentage_interpartition_edges))
    render_stream_graph(sorted_nodes, all_interpartition_edges, SVG_FILE_PATH + 'interpartition_edges.svg')

    # Attempt a smarter merging
    smart_merged_partitions = merge_partitions_min_interpartition_distance(sorted_partitions, all_interpartition_edges) + unconnected_nodes
    render_stream_graph(smart_merged_partitions, original_timesteps, SVG_FILE_PATH + 'final_smart.svg')
    render_stream_graph(smart_merged_partitions, all_interpartition_edges, SVG_FILE_PATH + 'interpartition_edges_smart.svg')
    total_distance_smart = get_total_distance(smart_merged_partitions, original_timesteps)
    logging.info('Optimization using smart merging finished. Time elapsed: {}s. Total edge distance: {}.'
                 .format(time.time() - t, total_distance_smart))

    logger.log_data({'n_vertices': n_vertices, 'n_edges': n_edges,
                     'ordered_nodes': sorted_nodes, 'ordered_nodes_smart': smart_merged_partitions,
                     'total_distance': total_distance, 'total_distance_smart': total_distance_smart,
                     'timesteps': original_timesteps},
                    'output')


if __name__ == '__main__':
    datasetname = 'ErdosRenyi'
    dataset = sgdataset.AbstractDataset.load(datasetname)
    logger.setup_logger(datasetname)

    for i, data in enumerate(dataset['dataset']):
        sort_with_partitioning(data)

