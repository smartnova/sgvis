#!/usr/bin/env python3

from generator.sgdataset import *

class SG20190122(AbstractDataset):
    '''
    Finn's first stream-graph dataset

    In fact this data was created from his random generator and nothing so special.  It first appeared
    on our Slack, on Jan 22, 2019, as the first successful result of Finn's z3 solver, it was given a
    historical value.
    '''
    def __init__(self):
        super().__init__()
        self.d['dataset'].append(
            {'params': {
                'n_vertices': 10,
                'n_timesteps': 2 },
             'content': [[(0, 1), (0, 2), (0, 3), (2, 3), (3, 4), (4, 9), (5, 8), (8, 9)],
                         [(0, 2), (0, 7), (1, 2), (1, 3), (3, 4), (4, 9), (5, 6), (8, 9)]]})

if __name__ == '__main__':
    SG20190122().save()

    d = AbstractDataset.load('SG20190122')
    AbstractDataset.output(d)
