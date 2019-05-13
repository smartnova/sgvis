#!/usr/bin/env python3

import json
import os
from pathlib import Path
import sys

from render.render_stream_graph import render_stream_graph

LOGDIR = Path(os.path.abspath(__file__)).parent.parent.parent.joinpath('log')
LOGNAME = 'ErdosRenyi-weighted-20190211-131724'
LOGNAME = 'ErdosRenyi-unweighted-20190211-183105'
logpath = LOGDIR.joinpath('{}.json'.format(LOGNAME))

IMAGEDIR = '/tmp/sgvis/images-{}'.format(LOGNAME)
os.makedirs(IMAGEDIR, exist_ok=True)

with open(logpath) as r:
    i = 0
    for experiment in json.load(r):
        vertices = list(map(lambda x: x[0], sorted(enumerate(experiment['result']['solution']), key=lambda x: x[1])))
        edges = experiment['content']
        render_stream_graph(vertices, edges, svg_path='{}/{:04}.svg'.format(IMAGEDIR, i))
        i = i + 1
