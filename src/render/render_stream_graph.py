#!/usr/bin/env python

# svgwrite Documentation: https://svgwrite.readthedocs.io/en/master/

import sys
from PyQt5 import QtGui, QtSvg
from PyQt5.QtWidgets import QApplication
import json


def render_stream_graph(ordered_nodes, timestamps, svg_path='stream_graph.svg'):
    import svgwrite as svg

    include_unordered_example = True

    initial_y_offset = 110
    height = initial_y_offset + 80 + len(ordered_nodes) * 40
    size = (1350, height) if include_unordered_example else (650, height)
    g = svg.Drawing(svg_path, size=size, profile='full')
    g.add(g.text('Stream graph ordering', insert=(30, 50),
                 fill='black', font_size='40', font_family='Gill Sans, sans-serif', font_weight=100))

    def get_total_distance(nodes):
        total_distance = 0
        for timestamp in timestamps:
            for u, v in timestamp:
                if u in nodes and v in nodes:
                    total_distance += abs(nodes.index(u) - nodes.index(v))

        return total_distance

    total_distance_unordered = get_total_distance(sorted(ordered_nodes))
    total_distance_ordered = get_total_distance(ordered_nodes)

    g.add(g.text('Total distance: ' + str(total_distance_unordered), insert=(70, height - 40),
                 fill='black', font_size='35', font_family='Gill Sans, sans-serif', font_weight=100))
    g.add(g.text('Total distance: ' + str(total_distance_ordered), insert=(800, height - 40),
                 fill='black', font_size='35', font_family='Gill Sans, sans-serif', font_weight=100))

    # ########################## Nodes ################################

    def render_nodes(nodes_to_render, x_offset):
        for i, node in enumerate(nodes_to_render):
            y_offset = (i * 40) + initial_y_offset
            add_background_lines(g, x_offset, y_offset)
            g.add(g.text(node, insert=(x_offset, y_offset + 10), fill='black', font_size='22.5', font_family='Verdana'))

    if include_unordered_example:
        render_nodes(sorted(ordered_nodes), 30)

        # Add arrow image between ordered and unordered
        arrow_resize_factor = 200
        path = '' if __name__ == '__main__' else '../render/'
        g.add(svg.image.Image(href=path + 'arrow-drawing-1.png', insert=(630, height / 2),
                              size=(1200 / arrow_resize_factor, 1059 / arrow_resize_factor)))

    render_nodes(ordered_nodes, 750 if include_unordered_example else 30)

    # ########################## Edges ################################

    def render_edges(timestamps_to_render, x_offset, ordered=False):
        for time, edge_set in enumerate(timestamps_to_render):
            for edge in edge_set:
                x = x_offset + time * 100
                y = get_y_offset_of_node(edge[0], ordered)
                target_y = get_y_offset_of_node(edge[1], ordered)
                middle = (y + target_y) / 2
                curve_radius_offset = get_curve_radius_offset(y, target_y)

                p = g.path(d=('m', x, y), stroke='black', fill='none', stroke_width=02.5)
                p.push('Q', x + curve_radius_offset, middle, x, target_y)
                g.add(p)

                g.add(svg.shapes.Circle(center=(x, y), r=4, stroke_width=1, fill='black', stroke='black'))
                g.add(svg.shapes.Circle(center=(x, target_y), r=4, stroke_width=1, fill='black', stroke='black'))

    def get_y_offset_of_node(node, ordered):
        try:
            i = sorted(ordered_nodes).index(node) if ordered else ordered_nodes.index(node)
            return initial_y_offset + i * 40
        except ValueError:
            raise RuntimeError('An edge in the dataset points to a node outside the dataset.')

    # get_curve_radius_offset is a function that takes the y-coordinate of two nodes, and outputs information about
    # how the curve between them should look if they are connected. Specifically, it returns the radius of the curve.
    def get_curve_radius_offset(y, target_y):
        # This magical 6 is an approximation of the y-distance at which the curve should approach maximum radius.
        # 60 is about the distance of 15 nodes, and a "t" (function time variable) that maxes around 10
        # provides a suitable curve with our chosen function. Thus, we divide the difference between the y-coords,
        # our only input indicator for how the curve radius should grow, by the "max" distance divided by 10.
        t = abs(target_y - y) / 20

        # We want an asymptotic function for the curve radius, since it should never cross into the area of the next
        # timestamp. The expansion of 2 and constant of 5 were found experimentally, and are used to control how
        # quickly the radius should grow with distance.
        normal_asymptotic = (t ** 2) / ((t ** 2) + 50)

        # This 15 is derived from the 10 used as x-seperator for each time step. For some reason a radius of 10
        # covers "less distance" that the distance of 10 to the next time step. 15 provides a nice boundary,
        # preserving a small padding to the next time step even if normal_asymptotic approaches its max value, 1.
        return normal_asymptotic * 150

    render_edges(timestamps, 120, True)
    render_edges(timestamps, 870)

    g.save()
    if __name__ == '__main__':
        viewer(size, svg_path)


def add_background_lines(g, x, y):
    # Configuration for the background lines
    bg_stroke_width = 01.5
    bg_stoke = 'black'
    bg_length = 10
    bg_space = 10
    bg_x_offset = x + 50

    for i in range(25):
        x_offset = bg_x_offset + (bg_length + bg_space) * i
        g.add(g.line((x_offset, y), (x_offset + bg_length, y), stroke_width=bg_stroke_width, stroke=bg_stoke))


def viewer(size, svg_path):
    app = QApplication(sys.argv)
    svg_widget = QtSvg.QSvgWidget(svg_path)
    svg_widget.setGeometry(size[0], size[1], size[0] * 100, size[1] * 100)
    # svg_widget.setGeometry(50, 50, 759, 668)
    svg_widget.show()

    sys.exit(app.exec_())


def run_with_test_data():
    ordered_nodes = list(range(20))
    timestamps = [
        [(i, j) for i in range(5, 11) for j in range(5, 11)] + [(0, 19)],
        [(12, i) for i in range(0, 20)]
    ]
    render_stream_graph(ordered_nodes, timestamps)


def run_with_sample_output():
    raw = open('sample_output.json').read()
    data = json.loads(raw)
    ordered_nodes = data['result']['solution']
    timestamps = data['content']
    render_stream_graph(ordered_nodes, timestamps)


if __name__ == '__main__':
    # run_with_test_data()
    run_with_sample_output()
