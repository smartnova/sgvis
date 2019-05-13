#!/usr/bin/env python3

# Important Notice
# DO NOT FORGET TO INCREASE "FORMAT_VERSION", when you modify this file

import datetime
import json
import os
from pathlib import Path

FORMAT_VERSION = 0.1
DATADIR = Path(os.path.abspath(__file__)).parent.parent.parent.joinpath('data')

class AbstractDataset:
    def __init__(self, **params):
        self.d = {
            'format_version': FORMAT_VERSION,
            'kind': self.__class__.__name__,
            'doc': type(self).__doc__,
            'date': str(datetime.datetime.now()),
            'creator': os.environ['USER'],
            'params': params,
            'dataset': [] }

    def save(self):
        with DATADIR.joinpath(self.d['kind'] + '.json').open(mode='w') as w:
            json.dump(self.d, w, indent=4)

    @staticmethod
    def load(name):
        with DATADIR.joinpath(name + '.json').open(mode='r') as r:
            return json.load(r)

    @staticmethod
    def output(d):
        print(d['format_version'], d['kind'], d['params'], d['date'], d['creator'], d['doc'])
        for data in d['dataset']:
            print(data['params'], [len(timestep) for timestep in data['content']])


class AbstractGenerator(AbstractDataset):
    def __init__(self, **params):
        super().__init__(**params)
        for params in self.parameters():
            self.d['dataset'].append({'params': params,
                                      'content': self.generate(**params)})


if __name__ == '__main__':
    import _path1
    AbstractDataset(n=5, m=3).save()
    '''
    d = Dataset.load('x')
    print(d.format_version, d.kind, d.params, d.date, d.creator, d.doc)
    '''
