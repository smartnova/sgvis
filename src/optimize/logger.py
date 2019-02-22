#!/usr/bin/env python3

import json
import logging
import os
import sys
import time


if __name__ == '__main__' and __package__ is None:
    from os import path
    # To ensure the generator import works even with wierd Z3 python paths
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from generator import sgdataset


def logger(datasetname):

    t = time.time()
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

    resultpath = time.strftime('/tmp/sgvis/{}-{}.json').format(datasetname, datetime)
    with open(resultpath, 'w') as w: json.dump(dataset, w)
