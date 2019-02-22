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


def Abs(x):
    return If(x >= 0, x, -x)


def constraint_system(unordered_nodes, timesteps):
    solver = Solver()
    n_vertices = len(unordered_nodes)

    # Assignment of vertices to vertical positions in the drawing
    # `Assignment` is represented by I_i, where i stands for the i'th vertex
    # and the value of I_i is the position.
    Assignment = [Int('I{}'.format(i)) for i in unordered_nodes]
    for Position in Assignment:
        solver.add(Position >= 0)
        solver.add(Position < n_vertices)
    solver.add(Distinct(Assignment))

    # The optimization objective is to minimize the accumulated edge distances
    edges = sum(timesteps, [])  # collecting all the edges
    #edges = set([tuple(e) for e in edges])
    Distance = Sum([Abs(Assignment[unordered_nodes.index(u)] - Assignment[unordered_nodes.index(v)]) for u, v in edges])

    edges = [tuple(edge) for edge in edges]
    info = {'n_vertices': n_vertices, 'n_edges': len(set(edges))}

    return {'Assignment': Assignment, 'solver': solver, 'Distance': Distance, 'info': info}


TIMEOUT = 1 * 60 * 1000  # 1 min time out set in milliseconds


def solve(problem):
    info = problem['info']
    t = time.time()
    solver, Assignment, Distance = problem['solver'], problem['Assignment'], problem['Distance']

    history = []
    max_distance = 1 << 31

    while True:
        solver.add(Distance < max_distance)
        timeout = int((t + 60 - time.time()) * 1000)
        if timeout < 0: break
        solver.set('timeout', timeout)
        result = solver.check()
        if result != sat: break
        current_best = solver.model()
        max_distance = current_best.evaluate(Distance)
        history.append(max_distance.as_long())

    info['solution'] = [current_best[v].as_long() for v in Assignment]
    info['distance'] = max_distance.as_long()
    info['optimum'] = result == unsat
    info['history'] = history
    logging.info('{} Distance reduction sequence: {}'.format('+' if result == unsat else '-', history))
    return info


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

    for data in dataset:
        params = data['params']
        initial_nodes = list(range(params['n_vertices']))
        problem = constraint_system(initial_nodes, data['content'])
        data['result'] = solve(problem)

    resultpath = time.strftime('/tmp/sgvis/{}-{}.json').format(datasetname, datetime)
    with open(resultpath, 'w') as w: json.dump(dataset, w)
