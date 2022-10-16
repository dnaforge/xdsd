from math import atan2, pi
from numpy import dot
from numpy.linalg import norm

current_id = 0  # last used element id
color_id = -1

DOMAIN_LEN = 50  # domain length
TOEHOLD_LEN = 30
BOND_DIST = 25  # distance between paired domains

# deprecated
# ANTIPARALLEL_CONST = 0
# MAX_OUT_ANGLE_CONST = 0

START_TEMP_CONST = 20
INITIAL_ITER_NO = 150
END_TEMP_CONST = round(START_TEMP_CONST / INITIAL_ITER_NO, 2)
COOL_CONST = 0.99
INCR_CONST = 5
DISTANCE_WELL_CONST = 2

COLORS = ['#ae7294', '#f07708', '#488bb5', '#288c1f', '#F72F6E', '#524438', '#00c06e', '#96E1EC']


def calculate_cos(domain1, domain2):
    return dot(domain1.direction, domain2.direction) / (norm(domain1.direction) * norm(domain2.direction))


def get_next_color():
    global color_id
    color_id += 1
    return COLORS[color_id % len(COLORS)]


def get_color(i):
    if i == -1:
        return '#b9c0bd'
    else:
        return COLORS[int(i) % len(COLORS)]


def reset_color():
    global color_id
    color_id = -1


def get_default_optimization_parameters():
    return START_TEMP_CONST, END_TEMP_CONST, COOL_CONST, INCR_CONST


def get_id():
    """
    Returns an integer which is unique in the global scope
    :return:
    """
    global current_id
    current_id += 1
    return current_id


def get_angle_negative(vector1, vector2):
    dot = vector1[0] * vector2[0] + vector1[1] * vector2[1]  # dot product between [x1, y1] and [x2, y2]
    det = vector1[0] * vector2[1] - vector2[0] * vector1[1]  # determinant
    angle = atan2(det, dot)
    return angle


def get_angle(vector1, vector2):
    dot = vector1[0] * vector2[0] + vector1[1] * vector2[1]  # dot product between [x1, y1] and [x2, y2]
    det = vector1[0] * vector2[1] - vector2[0] * vector1[1]  # determinant
    angle = atan2(det, dot)
    if angle < 0:
        angle += 2 * pi
    return angle


def get_global_angle(vector):
    vector = [vector[0], -vector[1]]
    angle = get_angle(vector, [1, 0])
    return angle


def euclidean_dist(point1, point2):
    x = point2[0] - point1[0]
    y = point2[1] - point1[1]

    return (x ** 2 + y ** 2) ** 0.5


def get_vector_length(vector):
    return (vector[0] ** 2 + vector[1] ** 2) ** 0.5


def get_radius(n_domains, n_strands):
    if n_strands == 1:
        r = 0
    else:
        r = DOMAIN_LEN * n_domains / (2 * pi) + DOMAIN_LEN
    return r


def get_loop_radius(n, d):
    r = (DOMAIN_LEN * n + d) / (2 * pi)  # approximation of the circumference by addition of the chord
    return r
