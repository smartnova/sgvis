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
    5. `$ sudo make install`

    Alternatively, if you don't have sudo rights, you can manually set your python paths to be able to execute Z3 scripts from anywhere in the project.
    5. `$ export PYTHONPATH=<YOUR_FILE_PATH_TO_Z3>/build/python`
    6. `$ export LD_LIBRARY_PATH=<YOUR_FILE_PATH_TO_Z3>/build`

## Run

`$ python src/stream_graph.py`

or

`$ python src/optimize/simple.py`

or any other Z3 script in the project in the same way.


# Ken's Dropbox link

- [SVG Images](https://www.dropbox.com/sh/eaptgncxumib60l/AAAJKIoud9ptv7l1MNh5u0Qoa?dl=0)

- [Logs](https://www.dropbox.com/sh/j9antzivw7ic728/AABMy0YSpCfXipgnXLYpKVUqa?dl=0)
