#!/usr/bin/env python

# svgwrite Documentation: https://svgwrite.readthedocs.io/en/master/

import sys
from PyQt5 import QtGui, QtSvg
from PyQt5.QtWidgets import QApplication


def render_stream_graph(nodes, edges, svg_path='stream_graph.svg'):
    import svgwrite as svg

    include_unordered_example = True

    initial_y_offset = 11
    height = initial_y_offset + 4 + len(nodes) * 4
    size = (135, height) if include_unordered_example else (65, 60)
    g = svg.Drawing(svg_path, size=size, profile='full')
    g.add(g.text('Stream graph ordering', insert=(3, 5),
                 fill='black', font_size='4', font_family='Gill Sans, sans-serif', font_weight=100))

    # ########################## Nodes ################################

    def render_nodes(nodes_to_render, x_offset):
        for i, node in enumerate(nodes_to_render):
            y_offset = (i * 4) + initial_y_offset
            add_background_lines(g, x_offset, y_offset)
            g.add(g.text(node, insert=(x_offset, y_offset + 1), fill='black', font_size='2.25',font_family='Verdana'))

    if include_unordered_example:
        render_nodes(sorted(nodes), 3)

        # Add arrow image between ordered and unordered
        arrow_resize_factor = 200
        '''
        g.add(svg.image.Image(href='render/arrow-drawing-1.png', insert=(63, height / 2),
                              size=(1200 / arrow_resize_factor, 1059 / arrow_resize_factor)))
        '''

    render_nodes(nodes, 75 if include_unordered_example else 3)

    # ########################## Edges ################################

    def render_edges(edges_to_render, x_offset, ordered=False):
        #for time, edge_set in edges_to_render.items():
        time = 0
        for edge_set in edges:
            for edge in edge_set:
                x = x_offset + time * 10
                y = get_y_offset_of_node(edge[0], ordered)
                target_y = get_y_offset_of_node(edge[1], ordered)
                middle = (y + target_y) / 2
                curve_radius_offset = abs(target_y - y) / 2

                p = g.path(d=('m', x, y), stroke='black', fill='none', stroke_width=0.25)
                p.push('Q', x + curve_radius_offset, middle, x, target_y)
                g.add(p)

                g.add(svg.shapes.Circle(center=(x, y), r=0.4, stroke_width=0.1, fill='black', stroke='black'))
                g.add(svg.shapes.Circle(center=(x, target_y), r=0.4, stroke_width=0.1, fill='black', stroke='black'))
            time = time + 1

    def get_y_offset_of_node(node, ordered):
        i = sorted(nodes).index(node) if ordered else nodes.index(node)
        return initial_y_offset + i * 4

    render_edges(edges, 12, True)
    render_edges(edges, 87)

    g.save()
    # viewer(size, svg_path)


def add_background_lines(g, x, y):

    # Configuration for the background lines
    bg_stroke_width = 0.15
    bg_stoke = 'black'
    bg_length = 1
    bg_space = 1
    bg_x_offset = x + 5

    for i in range(25):
        x_offset = bg_x_offset + (bg_length + bg_space) * i
        g.add(g.line((x_offset, y), (x_offset + bg_length, y), stroke_width=bg_stroke_width, stroke=bg_stoke))


def viewer(size, svg_path):
    app = QApplication(sys.argv)
    svg_widget = QtSvg.QSvgWidget(svg_path)
    svg_widget.setGeometry(size[0], size[1], size[0] * 10, size[1] * 10)
    # svg_widget.setGeometry(50, 50, 759, 668)
    svg_widget.show()

    sys.exit(app.exec_())


def asd():
    nodes = [0, 1, 2, 3, 4, 5, 6]
    edges = {0: [(0, 1), (0, 2), (3, 5)], 1: [(4, 6)]}
    edge_lengths = [(0, 0, 1), (0, 0, 2), (0, 3, 5), (1, 4, 6)]
    render_stream_graph(nodes, edges)


