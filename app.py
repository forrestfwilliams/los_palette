import panel as pn
import numpy as np

from matplotlib.figure import Figure
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.markers import MarkerStyle

WIDTH = 800
BG_COLOR = '#646464'


# los_palette.py ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
def angles_to_unit_vector(heading_angle_degrees, grazing_angle_degrees, left_looking=True):
    # Convert angles to radians
    heading_angle_start_at_east = 90 - heading_angle_degrees
    look_offset = 90 if left_looking else -90
    heading_los = heading_angle_start_at_east + look_offset
    heading_angle_radians = np.radians(heading_los)

    grazing_angle_sensor_to_ground = -(90 - grazing_angle_degrees)
    grazing_angle_radians = np.radians(grazing_angle_sensor_to_ground)

    # Calculate the vector components
    x_component = np.cos(heading_angle_radians) * np.cos(grazing_angle_radians)
    y_component = np.sin(heading_angle_radians) * np.cos(grazing_angle_radians)
    z_component = np.sin(grazing_angle_radians)

    # Create a NumPy array for the vector
    vector = np.array([x_component, y_component, z_component])

    # Normalize the vector to obtain the unit vector
    unit_vector = (vector / np.linalg.norm(vector)).round(5)

    return unit_vector


def unit_vector_to_hex(unit_vector):
    centered_rgb = (unit_vector * 127.5) + 127.5
    # r, g, b = centered_rgb.round(0).astype(int)
    r, b, g = centered_rgb.round(0).astype(int)
    hex_color = f'#{r:02X}{g:02X}{b:02X}'
    return hex_color


def angles_to_hex(heading_angle_degrees, grazing_angle_degrees, left_looking=True):
    unit_vector = angles_to_unit_vector(heading_angle_degrees, grazing_angle_degrees, left_looking)
    hex = unit_vector_to_hex(unit_vector)
    return hex


# end los_palette.py~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#


def get_heading_line(vector):
    if vector[0] == 0 and vector[1] == 0:
        return [0, 0], [0, 0]

    projected_vector = vector.copy()
    projected_vector[2] = 0
    unit_vector = (projected_vector / np.linalg.norm(projected_vector)).round(5)
    x = [0, unit_vector[0]]
    y = [0, unit_vector[1]]
    return x, y


def get_azimuth_line(vector, left_looking=True):
    if vector[0] == 0 and vector[1] == 0:
        return [0, 0], [0, 0]

    projected_vector = vector.copy()
    projected_vector[2] = 0
    look_offset = 90 if left_looking else -90
    angle_rad = np.deg2rad(-look_offset)
    rotation_matrix = np.array(
        [[np.cos(angle_rad), -np.sin(angle_rad), 0], [np.sin(angle_rad), np.cos(angle_rad), 0], [0, 0, 1]]
    )
    rotated_vector = np.dot(rotation_matrix, projected_vector)
    unit_vector = (rotated_vector / np.linalg.norm(projected_vector)).round(5)
    half_vector = unit_vector * 0.5
    x = [0, half_vector[0]]
    y = [0, half_vector[1]]
    return x, y


def satellite_marker(axis, angle=0, center=(0, 0)):
    # TODO: update to below when pyodide matplotlib version>=3.7.2
    # t = Affine2D().rotate_deg(angle)
    # marker = MarkerStyle('_', transform=t)
    marker = MarkerStyle('_')
    marker._transform.rotate_deg(angle)

    axis.scatter(center[0], center[1], marker=marker, s=3000, lw=4, color='black', zorder=1000)
    axis.scatter(center[0], center[1], marker=MarkerStyle('o'), s=200, color='black', zorder=1001)


def get_params(heading_angle, grazing_angle, look_direction):
    left_looking = look_direction == 'Left Looking'
    away_vector = angles_to_unit_vector(heading_angle, grazing_angle, left_looking)
    away_color = unit_vector_to_hex(away_vector)
    towards_vector = angles_to_unit_vector(heading_angle, 180 + grazing_angle, left_looking)
    towards_color = unit_vector_to_hex(towards_vector)
    return away_vector, left_looking, (away_color, towards_color)


def plot_look_direction(params):
    away_vector, left_looking, (away_color, _) = params

    x, y = get_heading_line(away_vector)
    az_x, az_y = get_azimuth_line(away_vector, left_looking)
    unit_circle = np.linspace(0, np.pi * 2, 500)

    fig = Figure(figsize=(6, 6))
    ax = fig.subplots()
    ax.plot(np.cos(unit_circle), np.sin(unit_circle), linewidth=1, color=BG_COLOR, zorder=2)
    ax.plot(az_x, az_y, color='lightgray', linestyle='--', label='Azimuth Direction', zorder=4)
    ax.plot(x, y, color=away_color, linestyle='--', label='Look Direction', zorder=3)
    angle = np.rad2deg(np.arctan2(away_vector[1], away_vector[0]))
    satellite_marker(ax, angle)

    ax.set(xlabel=None, ylabel=None, xlim=(-1.1, 1.1), ylim=(-1.1, 1.1), aspect='equal', facecolor=(0, 0, 0, 0))
    ax.spines['left'].set(position='center', color=BG_COLOR, zorder=0)
    ax.spines['bottom'].set(position='center', color=BG_COLOR, zorder=1)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.xaxis.set_ticks([-1, 1], labels=[270, 90], zorder=5)
    ax.yaxis.set_ticks([-1, 1], labels=[180, 0])
    ax.legend(loc='upper left')

    fig.patch.set_alpha(0.0)
    fig.tight_layout()
    mpl_pane = pn.pane.Matplotlib(fig, format='svg', dpi=150, width=WIDTH // 2)
    return mpl_pane


def get_grazing_line(vector, left_looking, vertical_offset=1):
    if vector[2] == 0:
        x = np.array([100, 0, -100])
        y = np.array([0, 0, 0])
    elif vector[0] == 0 and vector[1] == 0:
        x = np.array([0, 0, 0])
        y = np.array([-1, 0, 1])
    else:
        slope = vector[2] / np.sqrt(vector[0] ** 2 + vector[1] ** 2)
        y = np.array([-1, 0, 1])
        x = y / slope

    if left_looking:
        x *= -1

    y += vertical_offset
    return x, y


def plot_grazing_angle(params):
    away_vector, left_looking, (away_color, towards_color) = params
    x, y = get_grazing_line(away_vector, left_looking)

    fig = Figure(figsize=(6, 6))
    ax = fig.subplots()
    ax.plot(x[:2], y[:2], linewidth=2, linestyle='--', color=away_color, label='Away from Satellite', zorder=2)
    ax.plot(x[1:], y[1:], linewidth=2, linestyle='--', color=towards_color, label='Towards Satellite', zorder=3)
    angle = np.rad2deg(np.arccos(away_vector[2]))
    angle = angle if left_looking else angle + (2 * (180 - angle))
    satellite_marker(ax, angle, (0, 1))

    ax.set(xlabel=None, ylabel=None, xlim=(-1.25, 1.25), ylim=(0, 2.5), aspect='equal', facecolor=(0, 0, 0, 0))
    ax.spines['left'].set(position='center', color=BG_COLOR, zorder=0)
    ax.spines['bottom'].set(color=BG_COLOR, zorder=1)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.xaxis.set_ticks([])
    ax.yaxis.set_ticks([])
    ax.legend(loc='upper left')

    fig.patch.set_alpha(0.0)
    fig.tight_layout()
    mpl_pane = pn.pane.Matplotlib(fig, format='svg', dpi=150, width=WIDTH // 2)
    return mpl_pane


def plot_color_gradient(params):
    _, _, (away_color, towards_color) = params
    custom_cmap = LinearSegmentedColormap.from_list('custom diverging', [towards_color, 'white', away_color], N=256)

    gradient = np.linspace(0, 1, 256)
    gradient = np.vstack((gradient, gradient))

    fontsize = 14
    fig = Figure(figsize=(12, 1.5))
    ax = fig.subplots()
    inset = ax.inset_axes([0.05, 0.05, 0.9, 0.5])
    inset.imshow(gradient, aspect='auto', cmap=custom_cmap)
    ax.annotate(
        f'Towards satellite\n{towards_color}',
        xy=[0.05, 0.6],
        fontsize=fontsize,
        horizontalalignment='left',
        verticalalignment='bottom',
    )
    ax.annotate('#FFFFFF', xy=[0.5, 0.6], fontsize=fontsize, horizontalalignment='center', verticalalignment='bottom')
    ax.annotate(
        f'Away from satellite\n{away_color}',
        fontsize=fontsize,
        xy=[0.95, 0.6],
        horizontalalignment='right',
        verticalalignment='bottom',
    )
    inset.set_axis_off()
    ax.set_axis_off()
    ax.set(facecolor=(0, 0, 0, 0))

    fig.patch.set_alpha(0.0)
    fig.tight_layout()
    mpl_pane = pn.pane.Matplotlib(fig, format='svg', dpi=150, width=WIDTH)
    return mpl_pane


def reset_widgets(menu_value):
    options = {
        's1a': (348, 34, 'Left Looking'),
        's1d': (193, 34, 'Left Looking'),
        'vert': (0, 0, 'Left Looking'),
        'we': (0, 90, 'Left Looking'),
        'sn': (90, 90, 'Left Looking'),
    }
    heading_slider.value, grazing_slider.value, look_switch.value = options[menu_value]


def on_menu_change(event):
    selected_option = event.new
    reset_widgets(selected_option)


opts = dict(align=('center', 'center'), width=int(WIDTH / 4.5))
heading_slider = pn.widgets.IntSlider(name='Satellite Heading', start=0, end=360, step=1, value=360 - 12, **opts)
grazing_slider = pn.widgets.IntSlider(name='Grazing Angle', start=0, end=90, step=1, value=34, **opts)
look_switch = pn.widgets.ToggleGroup(options=['Left Looking', 'Right Looking'], behavior='radio', **opts)
menu_items = [
    ('Sentinel-1 Ascending', 's1a'),
    ('Sentinel-1 Descending', 's1d'),
    ('Vertical', 'vert'),
    ('West-East', 'we'),
    ('South-North', 'sn'),
]
menu = pn.widgets.MenuButton(name='Presets', items=menu_items, button_type='primary', **opts)
menu.on_click(on_menu_change)

params = pn.bind(get_params, heading_slider, grazing_slider, look_switch)
interactive_look = pn.bind(plot_look_direction, params)
interactive_grazing = pn.bind(plot_grazing_angle, params)
interactive_color = pn.bind(plot_color_gradient, params)
pn.Column(
    pn.Row(menu, heading_slider, grazing_slider, look_switch, height=100),
    pn.Row(interactive_look, interactive_grazing),
    pn.Row(interactive_color),
).servable()
