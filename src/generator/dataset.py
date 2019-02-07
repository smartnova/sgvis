#!/usr/bin/env python3

# Important Notice
# DO NOT FORGET TO INCREASE "FORMAT_VERSION", when you modify this file

import datetime
import os
from pathlib import Path
import pickle

FORMAT_VERSION = 0.1
DATADIR = Path(__file__).parent.parent.parent.joinpath('data')

class AbstractDataset:
    def __init__(self, **params):
        self.format_version = FORMAT_VERSION
        self.kind = type(self).__name__
        self.doc  = type(self).__doc__
        self.date = datetime.datetime.now()
        self.creator = os.environ['USER']
        self.params = params
        self.dataset = []

    def save(self):
        with DATADIR.joinpath(self.kind + '.pkl').open(mode='wb') as wb:
            pickle.dump(self, wb)

    @staticmethod
    def load(name):
        with DATADIR.joinpath(name + '.pkl').open(mode='rb') as rb:
            return pickle.load(rb)


class Data:
    def __init__(self, kind, params, data):
        self.kind = kind
        self.params = params
        self.data = data

class AbstractGenerator(AbstractDataset):
    def __init__(self, **params):
        super().__init__(**params)
        for params in self.parameters():
            self.dataset.append(Data(self.kind, params, self.generate(**params)))


if __name__ == '__main__':
    Dataset(n=5, m=3).save('x')
    d = Dataset.load('x')
    print(d.format_version, d.kind, d.params, d.date, d.creator, d.doc)
