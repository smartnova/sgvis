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

from src.generator import sgdataset

global_datasetname = ''
global_datetime = ''

def setup_logger(datasetname):
    global global_datasetname, global_datetime

    global_datasetname = datasetname
    dataset = sgdataset.AbstractDataset.load(datasetname)

    os.makedirs('/tmp/sgvis', exist_ok=True)
    datetime = time.strftime('%Y%m%d-%H%M%S').format(datasetname)
    global_datetime = datetime
    logpath = time.strftime('/tmp/sgvis/{}-{}.log').format(datasetname, datetime)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(message)s',
        handlers = [
            logging.FileHandler(logpath),
            logging.StreamHandler() ])

    logging.debug(dataset['kind'], dataset['doc'])


def log_data(dataset, filename_extention):
    global global_datasetname, global_datetime

    if global_datasetname is '' or global_datetime is '':
        raise RuntimeError('log_data was called before logging was set up.')

    resultpath = time.strftime('/tmp/sgvis/{}-{}-{}.json').format(global_datasetname, global_datetime, filename_extention)
    with open(resultpath, 'w') as w: json.dump(dataset, w)
