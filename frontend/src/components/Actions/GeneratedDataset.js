import React, { Component } from 'react';
import './Actions.css';
import callHttp from '../../http';

class GeneratedDataset extends Component {
  constructor(props) {
    super(props);

    this.state = {
      dataset: 'ErdosRenyi',
      n_vertices: 100,
      n_timesteps: 3
    };
  }

  generate = () => {
    this.props.generate(this.state);
  };

  render() {
    const { calling, doneCalling, optimize, fetch_latest } = this.props;
    const { dataset } = this.state;

    const parseInput = (e, type) => {
      let value = e.target.value;
      if (type !== 'dataset') {
        value = parseInt(value, 10);
      }
      this.setState({ [type]: value });
    };

    return (
      <div className="generated">
        <label name="dataset">Generator</label>
        <select
          name="dataset"
          value={this.state.dataset}
          onChange={e => parseInput(e, 'dataset')}
        >
          <option
            name="ErdosRenyi"
            onClick={() => this.setState({ dataset: 'ErdosRenyi' })}
          >
            ErdosRenyi
          </option>
        </select>
        {dataset === 'ErdosRenyi' && (
          <div>
            <label name="n_vertices">N_vertices</label>
            <input
              label="n_vertices"
              type="number"
              value={this.state.n_vertices}
              onChange={e => parseInput(e, 'n_vertices')}
            />

            <label name="n_timesteps">N_timesteps</label>
            <input
              name="n_timesteps"
              type="number"
              value={this.state.n_timesteps}
              onChange={e => parseInput(e, 'n_timesteps')}
            />
          </div>
        )}

        {calling.generating ? (
          ' Generating...'
        ) : (
          <button onClick={() => this.generate()}>Generate new dataset!</button>
        )}
        {doneCalling.generating && ' Done generating!'}

        <p>
          This button runs the sgvis optimizatin algorithm on the latest
          generated dataset.
        </p>

        {calling.optimize ? (
          'Optimizing...'
        ) : (
          <button onClick={() => optimize()}>Optimize</button>
        )}
        {doneCalling.optimize && ' Done optimizing!'}
      </div>
    );
  }
}

export default GeneratedDataset;
