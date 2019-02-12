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

    for x in partition:
        print('x', x, (x == 0), x == 1)
    print('asd', [x for x in range(n_vertices) if partition[x] == 0])
    partition_0 = [partition[x] for x in range(n_vertices) if partition[x] == 0]
    partition_1 = [partition[x] for x in range(n_vertices) if partition[x] == 1]
    size_difference_threshold = int(n_vertices / 10)
    optimizer.add(Abs(Sum(partition) - int(n_vertices / 2)) <= size_difference_threshold)

    # Keep the size of the partitions within a certain threshold of each other
    optimizer.add(Abs(len(partition_0) - len(partition_1)) <= size_difference_threshold)

    edges = sum(timesteps, [])
    edges_between_partitions = [If(And(partition[x] != partition[y], (x, y) in edges), 1, 0)
                                for x in range(n_vertices) for y in range(n_vertices) if y != x]
    optimizer.minimize(Sum(edges_between_partitions))

    return optimizer, partition, partition_0, partition_1


if __name__ == '__main__':
    t = time.time()
    dataset = sgdataset.AbstractDataset.load('ErdosRenyi')
    logging.debug(dataset['kind'], dataset['doc'])
    for data in dataset['dataset']:
        params = data['params']
        optimizer, partition, p0, p1 = split(params['n_vertices'], data['content'])
        optimizer.check()
        print('Finished', p0, p1)
        m = optimizer.model()
        r = [m.evaluate(partition[i]) for i in range(len(partition))]
        d = [(i, x.as_long()) for i, x in enumerate(r)]
        print('model', m, r)
