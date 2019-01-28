# Stream graph layout project

## Setup

1. `$ git clone ...`
2. `$ python3 -m venv venv`
2. `$ source venv/bin/activate`
3. `$ pip install -r requirements.txt`
4. If you don't already have it, install Z3:
    1. `$ git clone https://github.com/Z3Prover/z3.git`
    2. `$ cd z3`
    3. `$ python scripts/mk_make.py`
    4. `$ cd build && make`
    5. `$ export PYTHONPATH=<YOUR_FILE_PATH_TO_Z3>/build/python`
    6. `$ export LD_LIBRARY_PATH=<YOUR_FILE_PATH_TO_Z3>/build`

## Run

`$ python stream_graph.py`