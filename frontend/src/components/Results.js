import React from 'react';
import './Main.css';

function Results({ data }: props) {
  if (!data) return <div />;

  return (
    <div>
      <h1>Results</h1>
      Latest Result Info:
      <ul>
        <li>n_vertices: {data.n_vertices}</li>
        <li>n_edges: {data.n_edges}</li>
        <li>Total distance after optimization: {data.total_distance}</li>
      </ul>
    </div>
  );
}

export default Results;
