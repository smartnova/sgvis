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
    # To ensure the generator import works even with wierd Z3 python paths
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from generator import sgdataset
from optimize import simple
from partition.half import split


def Abs(x):
    return If(x >= 0, x, -x)


# Input: stream graph to be split into smaller, as-loosely-as-possible connected subgraphs
# Output: list of unmerged, internally sorted subgraphs on the form {'sorted_nodes': ..., 'timesteps': ...}
def recursively_partitition(sorted_nodes, timesteps):
    edges = sum(timesteps, [])
    if len(edges) <= 11:
        return timesteps

    halves = split(timesteps)


if __name__ == '__main__':

    t = time.time()
    datasetname = 'ErdosRenyi'
    dataset = sgdataset.AbstractDataset.load(datasetname)

    os.makedirs('/tmp/sgvis', exist_ok=True)
    datetime = time.strftime('%Y%m%d-%H%M%S').format(datasetname)
    logpath = time.strftime('/tmp/sgvis/{}-{}.log').format(datasetname, datetime)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(message)s',
        handlers = [
            logging.FileHandler(logpath),
            logging.StreamHandler() ])

    logging.debug(dataset['kind'], dataset['doc'])
    dataset = dataset['dataset']

    for i, data in enumerate(dataset):
        # Partition the problem binarily until the number of edges is within operational parameters
        params = data['params']
        n_vertices = params['n_vertices']
        timesteps = data['content']
        edges = sum(timesteps, [])
        n_edges = len(edges)


        problem = simple.constraint_system(params['n_vertices'], data['content'])
        data['result'] = simple.solve(problem)

    resultpath = time.strftime('/tmp/sgvis/{}-{}.json').format(datasetname, datetime)
    with open(resultpath, 'w') as w: json.dump(dataset, w)
