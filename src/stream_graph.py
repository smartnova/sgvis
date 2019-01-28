import time

from z3 import *
import functools
from render.render_stream_graph import render_stream_graph
from random import randint
import sys


def optimize_stream_graph(nodes, edges):
    s = Optimize()
    L = len(nodes)

    # Index

    index = [Int('i_%s' % i) for i in range(L)]

    index_choices = [And(index[i] >= 0, index[i] < L) for i in range(L)]
    index_unique = [Implies(index[i] == index[j], i == j) for i in range(L) for j in range(L)]

    s.add(index_choices)
    s.add(index_unique)

    def get_index(u):
        for single_index in index:
            if str(single_index) == 'i_%s' % u:
                return single_index
        raise RuntimeError('Tried finding current index of node:' + str(u) + ', but it did not exist.')

    # Distance

    edge_time_tuples = []
    for time, edge_list in edges.items():
        for edge in edge_list:
            edge_time_tuples.append((time, edge[0], edge[1]))
    edge_lengths = [Int('d_%s,%s_%s' % (t, u, v)) for t, u, v in edge_time_tuples]

    # Helper function to access the above variable by node i and j instead of index in the array.
    def get_distance(t, u, v):
        for single_distance in edge_lengths:
            if str(single_distance) == 'd_%s,%s_%s' % (t, u, v):
                return single_distance
        raise RuntimeError('Tried finding distance between node ' + str(u) + ' and node ' + str(v)
                           + ' at time ' + str(t) + ', but it did not exist.')

    def Abs(x):
        return If(x >= 0, x, -x)

    # Contrains for edge distanceing
    distance_positive = [edge_lengths[i] >= 0 for i in range(len(edge_lengths))]

    distance_actual_distances = [get_distance(t, u, v) == Abs(get_index(u) - get_index(v))
                                 for t, u, v in edge_time_tuples]

    s.add(distance_positive + distance_actual_distances)

    s.minimize(Sum(edge_lengths))
    return s, index


# n: number of nodes. m: number of timestamps
def generate_random_input_data(n, m):
    example_nodes = list(range(n))
    example_edges = {}

    for i in range(m):
        example_edges[i] = []
        number_of_edges = randint(3, int(n / 2))

        for j in range(number_of_edges):
            source = randint(0, n - 1)
            target = source
            while target == source:
                target = randint(0, n - 1)

            example_edges[i].append((source, target))

    return example_nodes, example_edges


def run(nodes, edges):
    print(nodes)
    print(example_edges)

    print("Calculating...")
    start_time = time.time()
    s, index = optimize_stream_graph(nodes, example_edges)
    s.check()
    print("Finished!")
    end_time = time.time()
    elapsed = round(end_time - start_time, 2)
    print("Computation took", elapsed, "seconds.")

    # Render the result
    m = s.model()
    r = [m.evaluate(index[i]) for i in range(len(nodes))]
    d = [(i, x.as_long()) for i, x in enumerate(r)]
    nodes_in_order = list(map(lambda x: x[0], sorted(d, key=lambda x: x[1])))

    render_stream_graph(nodes_in_order, edges)


example_nodes, example_edges = generate_random_input_data(15, 3)
run(example_nodes, example_edges)
