import json

from flask import Flask, request
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
    dataset = request.args.get('dataset') or 'ErdosRenyi'
    output = run_with_generated_dataset(dataset)
    print('output', output)
    return json.dumps(output, indent=2), {'Content-Type': 'application/json'}


@app.route("/latest")
def latest():
    path = './latest_output.json'
    with open(path, 'r') as file:
        latest = json.load(file)
        return json.dumps(latest, indent=2), {'Content-Type': 'application/json'}

