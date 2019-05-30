import json

from flask import Flask, request, Response
from flask_cors import CORS

from src.generator.ErdosRenyi import ErdosRenyi
from src.generator.sgdataset import AbstractDataset
from src.optimize.with_partitioning import run_with_generated_dataset

app = Flask(__name__)
CORS(app)


@app.route("/generate")
def generate():
    dataset = request.args.get('dataset') or 'ErdosRenyi'
    n_vertices = int(request.args.get('n_vertices')) or 100
    n_timesteps = int(request.args.get('n_timesteps')) or 3
    print('params:', dataset, n_vertices, n_timesteps)
    if dataset.lower() == 'erdosrenyi':
        ErdosRenyi([(n_vertices, n_timesteps)]).save()
        return json.dumps({'response': 'OK'}), 200, {'Content-Type': 'application/json'}

    return json.dumps({'Error': 'Unknown dataset'}, indent=2), 406, {'Content-Type': 'application/json'}


@app.route("/optimize")
def optimize():
    print('optimizing')
    datasetname = request.args.get('dataset') or 'ErdosRenyi'
    dataset = AbstractDataset.load(datasetname)
    print('in optimize. dataset', dataset)
    output = run_with_generated_dataset(dataset)
    print('output', output)
    return json.dumps(output, indent=2), {'Content-Type': 'application/json'}


@app.route("/latest")
def latest():
    path = './latest_output.json'
    with open(path, 'r') as file:
        latest = json.load(file)
        return json.dumps(latest, indent=2), {'Content-Type': 'application/json'}


@app.route("/custom", methods=['POST'])
def custom():
    input = request.get_json()
    print('custom input', input)
    try:
        assert input['kind']
        assert input['doc']
        assert input['dataset']
        assert input['dataset'][0]
        assert input['dataset'][0]['content']
        assert input['dataset'][0]['params']
        assert input['dataset'][0]['params']['n_vertices']
        assert input['dataset'][0]['params']['n_timesteps']
    except AssertionError:
        print('Input had incorrect format:')
        return Response('Input had incorrect format:', 400)

    output = run_with_generated_dataset(input)
    print('custom output')
    return json.dumps(output, indent=2), {'Content-Type': 'application/json'}