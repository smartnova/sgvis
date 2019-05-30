import React, { Component } from 'react';
import './Main.css';
import Results from './Results';
import Actions from './Actions/Actions';
import callHttp from '../http';

class Main extends Component {
  constructor(props) {
    super(props);

    this.state = {
      actionsCollapsed: false,
      showFormat: false,
      calling: {
        optimize: false,
        generating: false
      },
      doneCalling: {
        optimize: false,
        generating: false
      }
    };
  }

  collapseActions = () => {
    this.setState({ actionsCollapsed: !this.state.actionsCollapsed });
  };

  submitCustomDataset = input => {
    console.log('in submitCustomDataset. input: ', input);
    const dataset = JSON.parse(input);
    const postObject = {
      kind: 'custom',
      doc: 'A custom dataset.',
      dataset: [dataset]
    };

    this.setState({ calling: { ...this.state.calling, optimize: true } });

    callHttp('custom', undefined, 'POST', postObject).then(result => {
      this.props.updateData(result[0]);
      this.setState({
        doneCalling: { ...this.state.doneCalling, optimize: true },
        calling: { ...this.state.calling, optimize: false }
      });
    });
  };

  generate = input => {
    this.setState({ calling: { ...this.state.calling, generating: true } });
    callHttp('generate', input).then(result =>
      this.setState({
        doneCalling: { ...this.state.doneCalling, generating: true },
        calling: { ...this.state.calling, generating: false }
      })
    );
  };

  optimize = () => {
    console.log('in optimize', this.state);
    this.setState({
      calling: { ...this.state.calling, optimize: true },
      doneCalling: { ...this.state.doneCalling, optimize: false }
    });
    console.log('state updated.', this.state);
    callHttp('optimize').then(result => {
      console.log('call finished');
      this.props.updateData(result[0]);
      console.log('top level data updated');
      this.setState({
        doneCalling: { ...this.state.doneCalling, optimize: true },
        calling: { ...this.state.calling, optimize: false }
      });
    });
  };

  render() {
    console.log('main state:', this.state);
    const { fetch_latest, data, updateData } = this.props;
    const { actionsCollapsed, calling, doneCalling } = this.state;
    const loading = calling.optimize && !doneCalling.optimize;

    return (
      <div className="main">
        <div className="header">
          <div className="headerContent">
            <div className="headerLeft">
              <div className="logo">
                <span className="logoLine">
                  <span className="logoCap">S</span>tream
                </span>
                <span className="logoLine">
                  <span className="logoCap">G</span>raph
                </span>
                <span className="logoLine">
                  <span className="logoCap">Vis</span>ualization
                </span>
              </div>

              <div className="menu">
                <ul>
                  <li>
                    <a href="/">Home</a>
                  </li>
                </ul>
              </div>
            </div>
            <div className="headerRight">
              <ul style={{ margin: '7px 0 0 0' }}>
                <li>
                  <a href="https://github.com/smartnova/sgvis">
                    <img
                      style={{
                        width: '40px'
                      }}
                      target="blank"
                      alt="GitHub"
                      src="http://chittagongit.com/download/419235"
                    />
                  </a>
                </li>
              </ul>
            </div>
          </div>
        </div>
        <div className="content">
          <div className="block about">
            <p>
              This is a website used for showing the results of the work to
              improve readability of stream graphs.
            </p>
          </div>

          <div className="middle">
            <div className="block result">
              <Results
                data={data}
                actionsCollapsed={actionsCollapsed}
                loading={loading}
              />
            </div>
            <div className="block buttons" style={{ padding: 0 }}>
              <Actions
                fetch_latest={fetch_latest}
                collapsed={actionsCollapsed}
                collapse={this.collapseActions}
                updateData={updateData}
                calling={calling}
                doneCalling={doneCalling}
                optimize={this.optimize}
                submitCustomDataset={this.submitCustomDataset}
                generate={this.generate}
              />
            </div>
          </div>
        </div>
      </div>
    );
  }
}

export default Main;
