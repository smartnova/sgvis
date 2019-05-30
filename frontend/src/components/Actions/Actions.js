import React, { Component } from 'react';
import './Actions.css';
import callHttp from '../../http';
import GeneratedDataset from './GeneratedDataset';
import CustomDataset from './CustomDataset';

class Actions extends Component {
  constructor(props) {
    super(props);

    this.state = {
      datasetType: 'Custom'
    };
  }

  render() {
    const {
      collapse,
      collapsed,
      updateData,
      calling,
      doneCalling,
      fetch_latest,
      optimize,
      generate,
      submitCustomDataset
    } = this.props;
    const { datasetType } = this.state;

    const parseInput = (e, type) => {
      let value = e.target.value;
      if (type !== 'datasetType') {
        value = parseInt(value, 10);
      }
      this.setState({ [type]: value });
    };

    return !collapsed ? (
      <div className="actionContainer">
        <div className="collapser" onClick={() => collapse()}>
          <div>»</div>
        </div>
        <div className="actions">
          <h1>Actions</h1>

          <label name="dataset">Dataset type</label>
          <select
            name="datasetType"
            value={this.state.datasetType}
            onChange={e => parseInput(e, 'datasetType')}
          >
            <option name="generated">Generated</option>
            <option name="custom">Custom</option>
          </select>

          <div style={{ margin: '0 0 25px 15px' }}>
            {datasetType === 'Generated' ? (
              <GeneratedDataset
                updateData={updateData}
                calling={calling}
                doneCalling={doneCalling}
                fetch_latest={fetch_latest}
                optimize={optimize}
                generate={generate}
              />
            ) : (
              <CustomDataset
                updateData={updateData}
                calling={calling}
                doneCalling={doneCalling}
                submitCustomDataset={submitCustomDataset}
              />
            )}
          </div>

          <p style={{ marginBottom: '5px' }}>
            This button re-fetches the latest optimization.
          </p>
          <button onClick={() => fetch_latest()}>Fetch latest</button>
        </div>
      </div>
    ) : (
      <div onClick={() => collapse()} className="uncollapser">
        «
      </div>
    );
  }
}

export default Actions;
