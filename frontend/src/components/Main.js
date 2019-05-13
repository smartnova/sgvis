import React from 'react';
import './Main.css';
import Results from './Results';
import Actions from './Actions';

function Main({ data, fetch_latest }: props) {
  return (
    <div className="main">
      <div className="header">
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
      <div className="content">
        <div className="block about">
          <p>
            This is a website used for showing the results of the work to
            improve readability of stream graphs.
          </p>
        </div>

        <div className="block result">
          <Results data={data} />
        </div>
        <div className="block buttons">
          <Actions fetch_latest={fetch_latest} />
        </div>
      </div>
    </div>
  );
}

export default Main;
