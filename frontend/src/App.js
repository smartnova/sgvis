import React, { Component } from 'react';
import Main from './components/Main.js';
import callHttp from './http';

class App extends Component {
  constructor(props) {
    super(props);

    this.state = {
      data: {
        n_timestamps: null,
        n_vertices: null,
        ordered_nodes: null,
        ordered_nodes_smart: null,
        total_distance: null,
        total_distance_smart: null
      }
    };
  }

  fetch_latest = () => {
    callHttp('latest').then(data => this.setState({ data }));
  };

  componentDidMount() {
    this.fetch_latest();
  }

  render() {
    return <Main data={this.state.data} fetch_latest={this.fetch_latest} />;
  }
}

export default App;
