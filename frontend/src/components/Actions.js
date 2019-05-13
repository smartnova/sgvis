import React, { Component } from 'react';
import './Actions.css';
import callHttp from '../http';

class Actions extends Component {
  constructor(props) {
    super(props);

    this.state = {
      dataset: 'ErdosRenyi',
      n_vertices: 100,
      n_timesteps: 3,
      calling: {
        generating: false,
        optimizing: false
      },
      doneCalling: {
        generating: false,
        optimizing: false
      }
    };
  }

  generate() {
    this.setState({ calling: { ...this.state.calling, generating: true } });
    callHttp('generate', this.state).then(result =>
      this.setState({
        doneCalling: { ...this.state.doneCalling, generating: true },
        calling: { ...this.state.calling, generating: false }
      })
    );
  }

  optimize() {
    this.setState({ calling: { ...this.state.calling, optimizing: true } });
    callHttp('optimize').then(result =>
      this.setState({
        doneCalling: { ...this.state.doneCalling, optimizing: true },
        calling: { ...this.state.calling, optimizing: false }
      })
    );
  }

  render() {
    const parseInput = (e, type) => {
      let value = e.target.value;
      if (type !== 'dataset') {
        value = parseInt(value, 10);
      }
      this.setState({ [type]: value });
    };

    return (
      <div className="actions">
        <h1>Actions</h1>

        <label name="dataset">Dataset</label>
        <select
          name="dataset"
          value={this.state.dataset}
          onChange={e => parseInput(e, 'dataset')}
        >
          <option name="ErdosRenyi">ErdosRenyi</option>
          <option name="Other">Other (Not done)</option>
        </select>

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
        <button onClick={() => this.generate()}>Generate new dataset!</button>
        {this.state.calling.generating && ' ...'}
        {this.state.doneCalling.generating && ' Done generating!'}

        <p>
          This button runs the sgvis optimizatin algorithm on the latest
          generated dataset.
        </p>
        <button onClick={() => this.optimize()}>Optimize</button>
        {this.state.calling.optimizing && ' ...'}
        {this.state.doneCalling.optimizing && ' Done optimizing!'}

        <p>This button re-fetches the latest optimization.</p>
        <button onClick={() => this.props.fetch_latest()}>Fetch latest</button>
      </div>
    );
  }
}

export default Actions;
