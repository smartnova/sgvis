import React, { Component } from 'react';
import './Actions.css';

class CustomDataset extends Component {
  constructor(props) {
    super(props);

    this.state = {
      dataset: '',
      showFormat: false
    };
  }

  submitCustomDataset = () => {
    const input = this.state.dataset;
    this.props.submitCustomDataset(input);
  };

  render() {
    const { calling, doneCalling } = this.props;
    return (
      <div className="customForm">
        <label htmlFor="customDataset">CustomDataset</label>
        <textarea
          name="customDataset"
          onChange={e => this.setState({ dataset: e.target.value })}
        />
        <div
          onClick={() => this.setState({ showFormat: !this.state.showFormat })}
          className="formatSelector"
        >
          Input format (<i>Click to expand</i>)
          <p
            className="customFormat"
            style={{ display: this.state.showFormat ? 'block' : 'none' }}
          >
            {`
{
    "params": {
        "n_vertices": 100,
        "n_timesteps": 3
    },
    "content": [
        [             // Timestep
            [0, 70],  // Edge
            [1, 29]
        ]
    ]
}`}
          </p>
        </div>
        {calling && calling.optimize ? (
          'Optimizing...'
        ) : (
          <button onClick={() => this.submitCustomDataset()}>Submit</button>
        )}
      </div>
    );
  }
}

export default CustomDataset;
