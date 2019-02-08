#!/usr/bin/env python3

import logging
import time

from z3 import *

from generator import sgdataset
from generator import SG20190122


logging.basicConfig(level=logging.INFO)

def Abs(x):
    return If(x >= 0, x, -x)

def optimize(n_vertices, timesteps):
    t = time.time()
    solver = Optimize()

    assignments = [Int('I{}'.format(i)) for i in range(n_vertices)]
    for assignment in assignments:
        solver.add(assignment >= 0)
        solver.add(assignment < n_vertices)
    solver.add(Distinct(assignments))

    edges = []

    for timestep in timesteps:
        edges = edges + timestep

    logging.debug(edges)
    Distance = Sum([Abs(assignments[u] - assignments[v]) for u, v in edges])

    solver.minimize(Distance)
    logging.debug(solver)
    logging.info('Problem formulated ({}).  Model checking...'.format(time.time() - t))

    solver.check()
    logging.info('Problem solved ({})'.format(time.time() - t))

    print(solver.model())


if __name__ == '__main__':
    t = time.time()
    dataset = sgdataset.AbstractDataset.load('SG20190122')
    logging.debug(dataset['kind'], dataset['doc'])
    for data in dataset['dataset']:
        params = data['params']
        result = optimize(params['n_vertices'], data['content'])
