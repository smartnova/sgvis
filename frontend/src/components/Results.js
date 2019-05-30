import React, { Component } from 'react';
import './Results.css';
import RenderGraph from './RenderGraph.js';
import * as d3 from 'd3';

class Results extends Component {
  constructor(props) {
    super(props);

    this.state = {
      shouldRenderOrdered: true,
      shouldRenderUnordered: true,
      shouldRenderSmart: true
    };
  }

  componentDidMount() {
    const { data } = this.props;
    const shouldRenderSmart = data.total_distance_smart < data.total_distance;
    this.setState({
      shouldRenderSmart,
      shouldRenderOrdered: !shouldRenderSmart
    });
  }

  render() {
    console.log('data', this.props.data);
    const { data, actionsCollapsed, loading } = this.props;

    const {
      shouldRenderOrdered,
      shouldRenderUnordered,
      shouldRenderSmart
    } = this.state;

    if (!data.ordered_nodes) return <div />;

    console.log('loading:', loading);

    return (
      <div>
        <h1>Results</h1>
        Latest Result Info:
        <ul>
          <li>n_vertices: {data.n_vertices}</li>
          <li>n_edges: {data.n_edges}</li>
          <li>Total distance after optimization: {data.total_distance}</li>
          <li>
            Total distance after optimization (smart):{' '}
            {data.total_distance_smart}
          </li>
        </ul>
        <div className="whatToRender">
          <input
            type="checkbox"
            name="renderUnordered"
            value="renderUnordered"
            checked={shouldRenderUnordered}
            onChange={e =>
              this.setState({
                shouldRenderUnordered: !shouldRenderUnordered
              })
            }
          />
          <label name="renderUnordered">Render unordered</label>
          <br />

          <input
            type="checkbox"
            name="renderOrdered"
            value="renderOrdered"
            checked={shouldRenderOrdered}
            onChange={e =>
              this.setState({
                shouldRenderOrdered: !shouldRenderOrdered
              })
            }
          />
          <label name="renderOrdered">Render ordered</label>
          <br />

          <input
            type="checkbox"
            name="renderSmart"
            value="renderSmart"
            checked={shouldRenderSmart}
            onChange={e =>
              this.setState({
                shouldRenderSmart: !shouldRenderSmart
              })
            }
          />
          <label name="renderOrdered">Render ordered(smart)</label>
        </div>
        {loading ? (
          <div style={{ minWidth: '620px', display: 'flex' }}>
            <div className="lds-ring" style={{ margin: '40px auto 0' }}>
              <div />
              <div />
              <div />
              <div />
            </div>
          </div>
        ) : (
          <div
            className="graphContainer"
            style={{ width: actionsCollapsed ? '968px' : '600px' }} // I hate css
          >
            {shouldRenderUnordered && (
              <div>
                <h3>Unordered - {}</h3>
                <RenderGraph
                  data={{
                    ...data,
                    ordered_nodes: [...data.ordered_nodes].sort(
                      (a, b) => parseInt(a, 10) - parseInt(b, 10)
                    )
                  }}
                  selector={'unordered'}
                >
                  <div id="unordered" />
                </RenderGraph>
              </div>
            )}

            {shouldRenderOrdered && (
              <div
                style={{ marginLeft: shouldRenderUnordered ? '-300px' : '0' }}
              >
                <h3>Ordered – {data.total_distance}</h3>
                <RenderGraph data={data} selector={'ordered'}>
                  <div id="ordered" />
                </RenderGraph>
              </div>
            )}

            {shouldRenderSmart && (
              <div
                style={{ marginLeft: shouldRenderUnordered ? '-300px' : '0' }}
              >
                <h3>Ordered (smart) – {data.total_distance_smart}</h3>
                <RenderGraph
                  data={{
                    ...data,
                    ordered_nodes: data.ordered_nodes_smart
                  }}
                  selector={'smart'}
                >
                  <div id="smart" />
                </RenderGraph>
              </div>
            )}
          </div>
        )}
      </div>
    );
  }
}

export default Results;
