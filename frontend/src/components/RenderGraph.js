import React, { Component } from 'react';
import './renderGraph.css';
import * as d3 from 'd3';

class RenderGraph extends Component {
  initial_y = 40;

  componentDidMount() {
    this.renderGraph();
  }

  renderGraph() {
    const { data, selector } = this.props;
    const { ordered_nodes } = data;

    const svgContainer = this.setupContainer(ordered_nodes, selector);

    ordered_nodes &&
      ordered_nodes.map((node, i) => {
        const y_offset = this.initial_y + i * 40;
        this.drawBackground(svgContainer, 0, y_offset);
        svgContainer
          .append('text')
          .attr('x', 0)
          .attr('y', y_offset + 5)
          .text(node)
          .attr('font-family', 'sans-serif')
          .attr('font-size', '14px');
      });

    const ordered = selector !== 'unordered';
    this.drawEdges(data, svgContainer, 70, ordered);
  }

  setupContainer(ordered_nodes, selector) {
    const w = 600;
    const h = ordered_nodes ? ordered_nodes.length * 20 : 400;

    const zoomLogic = d3.zoom().on('zoom', function() {
      svgContainer.attr('transform', d3.event.transform);
    });

    const svgContainer = d3
      .select(`#${selector}`)
      .append('svg')
      .attr('width', w)
      .attr('height', h)
      // .call(zoomLogic)
      // .on('wheel.zoom', null)
      .append('g')
      .attr('transform', 'translate(10, -15) scale(0.5, 0.5)')
      .attr('width', '300px');

    return svgContainer;
  }

  drawEdges(data, svgContainer, x_offset, ordered) {
    const lineDatas = [];
    const circleData = [];

    data &&
      data.timesteps &&
      data.timesteps.map((edge_set, time) => {
        edge_set.map(edge => {
          const x = x_offset + time * 100;
          const y = this.get_y_offset_of_node(
            data,
            svgContainer,
            edge[0],
            ordered
          );
          const target_y = this.get_y_offset_of_node(
            data,
            svgContainer,
            edge[1],
            ordered
          );
          const middle = (y + target_y) / 2;
          const curve_radius_offset = this.get_curve_radius_offset(y, target_y);

          const linePoints = [
            [x, y],
            [x + curve_radius_offset, middle],
            [x, target_y]
          ];
          lineDatas.push(linePoints);

          const lineGen = d3.line().curve(d3.curveBundle.beta(0));

          const lineData = lineGen(linePoints);

          svgContainer
            .append('path')
            //.attr('d', lineData)
            .attr(
              'd',
              `M ${x}, ${y}, Q ${x +
                curve_radius_offset}, ${middle}, ${x}, ${target_y}`
            )
            .style('stroke', 'black')
            .style('stroke-width', 2.5)
            .style('fill', 'none');

          circleData.push({ x, y });
          circleData.push({ x, y: target_y });
        });

        svgContainer
          .selectAll('circle')
          .data(circleData)
          .enter()
          .append('circle')
          .attr('cx', d => d.x)
          .attr('cy', d => d.y)
          .attr('r', 4)
          .style('stroke_width', 4)
          .style('fill', 'black')
          .style('stroke', 'black');
      });
  }

  get_y_offset_of_node(data, svgContainer, node, ordered = true) {
    const nodes = [...data.ordered_nodes];

    const i = !ordered
      ? nodes.sort().indexOf(node)
      : data.ordered_nodes.indexOf(node);
    return this.initial_y + i * 40;
  }

  get_curve_radius_offset(y, target_y) {
    const a = Math.abs(target_y - y) / 20;
    const t = a > 0 ? a : 1;
    const normal_asymptotic = t ** 2 / (t ** 2 + 50);
    return normal_asymptotic * 150;
  }

  drawBackground(svgContainer, x, y) {
    const bg_stroke_width = 1.5;
    const bg_stoke = 'black';
    const bg_length = 10;
    const bg_space = 10;
    const bg_x_offset = x + 50;

    [...Array(25).keys()].map(i => {
      const x_offset = bg_x_offset + (bg_length + bg_space) * i;
      svgContainer
        .append('line')
        .attr('x1', x_offset)
        .attr('x2', x_offset + bg_length)
        .attr('y1', y)
        .attr('y2', y)
        .attr('stroke', bg_stoke)
        .attr('stroke-width', bg_stroke_width)
        .attr('fill', 'none');
    });
  }

  render() {
    return { ...this.props.children };
  }
}

export default RenderGraph;
