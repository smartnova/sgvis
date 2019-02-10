#!/usr/bin/env python3

import logging
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

TIMEOUT = 1 * 60 * 1000  # 1 min time out set in milliseconds

def Abs(x):
    return If(x >= 0, x, -x)

def optimize(n_vertices, timesteps):
    t = time.time()
    solver = Optimize()

    # Assignment of vertices to vertical positions in the drawing
    # `assignment` is represented by I_i, where i stands for the i'th vertex
    # and the value of I_i is the position.
    assignment = [Int('I{}'.format(i)) for i in range(n_vertices)]
    for position in assignment:
        solver.add(position >= 0)
        solver.add(position < n_vertices)
    solver.add(Distinct(assignment))

    # The optimization objective is to minimize the accumulated edge distances
    edges = sum(timesteps, [])  # collecting all the edges
    Distance = Sum([Abs(assignment[u] - assignment[v]) for u, v in edges])

    edges = [tuple(edge) for edge in edges]
    logging.info('Problem (#vertices = {}, #connected pairs = {})'.format(n_vertices, len(set(edges))))
    solver.minimize(Distance)

    solver.set('timeout', TIMEOUT)
    result = solver.check()
    if result == z3.unknown:
        logging.info('Timeout after {} seconds'.format(TIMEOUT // 1000))
    else:
        logging.info('Problem solved in {:02.3f}sec'.format(time.time() - t))

    # print(solver.model())


if __name__ == '__main__':
    t = time.time()
    dataset = sgdataset.AbstractDataset.load('ErdosRenyi')
    logging.debug(dataset['kind'], dataset['doc'])
    for data in dataset['dataset']:
        params = data['params']
        result = optimize(params['n_vertices'], data['content'])
