import numpy as np


def angles_to_unit_vector(heading_angle_degrees, incidence_angle_degrees, left_looking=True):
    # Convert angles to radians
    heading_angle_start_at_east = 90 - heading_angle_degrees
    look_offset = 90 if left_looking else -90
    heading_los = heading_angle_start_at_east + look_offset
    heading_angle_radians = np.radians(heading_los)

    incidence_angle_sensor_to_ground = -(90 - incidence_angle_degrees)
    incidence_angle_radians = np.radians(incidence_angle_sensor_to_ground)

    # Calculate the vector components
    x_component = np.cos(heading_angle_radians) * np.cos(incidence_angle_radians)
    y_component = np.sin(heading_angle_radians) * np.cos(incidence_angle_radians)
    z_component = np.sin(incidence_angle_radians)

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


def angles_to_hex(heading_angle_degrees, incidence_angle_degrees, left_looking=True):
    unit_vector = angles_to_unit_vector(heading_angle_degrees, incidence_angle_degrees, left_looking)
    hex = unit_vector_to_hex(unit_vector)
    return hex
