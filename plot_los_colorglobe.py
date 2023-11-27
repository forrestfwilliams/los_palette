from itertools import product

import numpy as np
import plotly.graph_objects as go

from los_palette import angles_to_unit_vector, unit_vector_to_hex

base_template = go.layout.Template()

horizontal_angles = np.linspace(0, 360, 72)
vertical_angles = np.linspace(0, 180, 36)
unit_vectors = [angles_to_unit_vector(h, v) for h, v in product(horizontal_angles, vertical_angles)]
colors = [unit_vector_to_hex(u) for u in unit_vectors]
x, y, z = [[row[i] for row in unit_vectors] for i in range(3)]

points = go.Scatter3d(x=x, y=y, z=z, mode='markers', text=colors, showlegend=False, marker=dict(size=21, color=colors, opacity=1))
layout = go.Layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)'
)
fig = go.Figure(data=[points], layout=layout)
scene_opts = dict(xaxis_range=[-1, 1], yaxis_range=[-1, 1], zaxis_range=[-1, 1], aspectmode='cube', xaxis_title='X Component', yaxis_title='Y Component', zaxis_title='Z Component', camera=dict(eye=dict(x=1.5, y=1.5, z=1.5)))

fig.update_layout(template=base_template, width=800, height=800, margin=dict(l=10, r=10, t=10, b=10), scene=scene_opts)
fig.write_html('./los_colorglobe.html')
