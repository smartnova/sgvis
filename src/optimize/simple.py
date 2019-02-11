#!/usr/bin/env python3

import logging
import sys
import tempfile
import time

from z3 import *

from generator import sgdataset
from generator import SG20190122

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(message)s',
    handlers = [
        logging.FileHandler('simple.log'),
        logging.StreamHandler() ])

def Abs(x):
    return If(x >= 0, x, -x)

def constraint_system(n_vertices, timesteps):
    solver = Solver()

    # Assignment of vertices to vertical positions in the drawing
    # `Assignment` is represented by I_i, where i stands for the i'th vertex
    # and the value of I_i is the position.
    Assignment = [Int('I{}'.format(i)) for i in range(n_vertices)]
    for Position in Assignment:
        solver.add(Position >= 0)
        solver.add(Position < n_vertices)
    solver.add(Distinct(Assignment))

    # The optimization objective is to minimize the accumulated edge distances
    edges = sum(timesteps, [])  # collecting all the edges
    Distance = Sum([Abs(Assignment[u] - Assignment[v]) for u, v in edges])

    edges = [tuple(edge) for edge in edges]
    info = {'n_vertices': n_vertices, 'n_edges': len(set(edges))}

    return {'Assignment': Assignment, 'solver': solver, 'Distance': Distance, 'info': info}


TIMEOUT = 1 * 60 * 1000  # 1 min time out set in milliseconds

def solve(problem):
    t = time.time()
    solver, Assignment, Distance = problem['solver'], problem['Assignment'], problem['Distance']

    history = []
    max_distance = 1 << 31

    while True:
        solver.add(Distance < max_distance)
        if solver.check() == z3.unknown: break
        try: current_best = solver.model()
        except: break
        max_distance = current_best.evaluate(Distance)
        history.append(max_distance.as_long())

    logging.info('Distance = {}: {}, {}'.format(max_distance, [current_best[v] for v in Assignment], history))

if __name__ == '__main__':
    t = time.time()
    dataset = sgdataset.AbstractDataset.load('ErdosRenyi')
    logging.debug(dataset['kind'], dataset['doc'])
    for data in dataset['dataset']:
        params = data['params']
        problem = constraint_system(params['n_vertices'], data['content'])
        solve(problem)
