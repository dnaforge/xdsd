from math import atan2, pi, sqrt

from numpy import dot
from numpy.linalg import norm

current_id = 0  # last used element id
color_id = -1

DOMAIN_LEN = 50  # domain length
TOEHOLD_LEN = 25
BOND_DIST = DOMAIN_LEN / (sqrt(2))  # distance between paired domains

START_TEMP_CONST = 10
INITIAL_ITER_NO = 100
END_TEMP_CONST = 0.05
# END_TEMP_CONST = round(START_TEMP_CONST / INITIAL_ITER_NO, 2)
COOL_CONST = 0.7
INCR_CONST = 10

STRAIGHT_LINES = True

COLORS = [
    "#fe4a49",
    "#2ab7ca",
    "#fed766",
    "#1bbe7d",
    "#9284e3",
    "#694f51",
    "#341bc6",
    "#2f851c",
    "#ff9f31",
    "#81869b",
]


def get_side(vector, point):
    # on which side of the vector the point is
    # compute the cross product
    # 𝑑=(𝑥−𝑥1)(𝑦2−𝑦1)−(𝑦−𝑦1)(𝑥2−𝑥1)
    return (point[0] - vector[0][0]) * (vector[1][1] - vector[0][1]) - (
        point[1] - vector[0][1]
    ) * (vector[1][0] - vector[0][0])


def get_cos(vector1, vector2):
    return dot(vector1, vector2) / (norm(vector1) * norm(vector2))


def get_next_color():
    global color_id
    color_id += 1
    return COLORS[color_id % len(COLORS)]


def get_color(i):
    if i == -1:
        return "#b9c0bd"
    else:
        return COLORS[int(i) % len(COLORS)]


def reset_color():
    global color_id
    color_id = -1


def get_id():
    """
    Returns an integer which is unique in the global scope
    :return:
    """
    global current_id
    current_id += 1
    return current_id


def get_angle_negative(vector1, vector2):
    dot = (
        vector1[0] * vector2[0] + vector1[1] * vector2[1]
    )  # dot product between [x1, y1] and [x2, y2]
    det = vector1[0] * vector2[1] - vector2[0] * vector1[1]  # determinant
    angle = atan2(det, dot)
    return angle


def get_angle(vector1, vector2):
    dot = (
        vector1[0] * vector2[0] + vector1[1] * vector2[1]
    )  # dot product between [x1, y1] and [x2, y2]
    det = vector1[0] * vector2[1] - vector2[0] * vector1[1]  # determinant
    angle = atan2(det, dot)
    if angle < 0:
        angle += 2 * pi
    return angle


def get_global_angle(vector):
    vector = [vector[0], vector[1]]
    angle = get_angle(vector, [1, 0])
    return angle


def euclidean_dist(point1, point2):
    x = point2[0] - point1[0]
    y = point2[1] - point1[1]

    return (x**2 + y**2) ** 0.5


def get_vector_length(vector):
    return (vector[0] ** 2 + vector[1] ** 2) ** 0.5


def get_radius(n_domains, n_strands):
    if n_strands == 1:
        r = 0
    else:
        r = DOMAIN_LEN * n_domains / (2 * pi) + DOMAIN_LEN
    return r


def get_loop_radius(n, d):
    r = (DOMAIN_LEN * n + d) / (
        2 * pi
    )  # approximation of the circumference by addition of the chord
    return r


# def calculate_square_first_side(points_data, prev_point, next_point):
#     # bond point
#     bx, by = points_data[0]
#     # middle point
#     mx, my = points_data[1]
#
#     # center to bond
#     ctb = [bx-mx, by-my]
#     ctb_len = get_vector_length(ctb)
#     ctb = [ctb[0]*DOMAIN_LEN/2/ctb_len, ctb[1]*DOMAIN_LEN/2/ctb_len]
#
#     ctb_perp = [-ctb[1], ctb[0]]
#
#     ctb_add1 = [ctb[0]+ctb_perp[0], ctb[1]+ctb_perp[1]]
#     point1 = [mx+ctb_add1[0], my+ctb_add1[1]]
#     ctb_add2 = [ctb[0] - ctb_perp[0], ctb[1] - ctb_perp[1]]
#     point2 = [mx + ctb_add2[0], my + ctb_add2[1]]
#
#     np1 = np2 = pp1 = pp2 = 0
#     if next_point:
#         np1 = euclidean_dist(next_point, point1)
#         np2 = euclidean_dist(next_point, point2)
#     if prev_point:
#         pp1 = euclidean_dist(prev_point, point1)
#         pp2 = euclidean_dist(prev_point, point2)
#     if np1+pp2 < np2+pp1:
#         return [point2, point1]
#     else:
#         return [point1, point2]
#
#
# def calculate_square_second_side(square_side, points_data):
#     # bond point
#     bx, by = points_data[0]
#     # middle point
#     mx, my = points_data[1]
#     # square points
#     sq1x, sq1y = square_side[0]
#     sq2x, sq2y = square_side[1]
#
#     # center to bond
#     ctb = [bx-mx, by-my]
#     ctb_len = get_vector_length(ctb)
#     ctb = [ctb[0]*DOMAIN_LEN/ctb_len, ctb[1]*DOMAIN_LEN/ctb_len]
#
#     point2 = [ctb[0]+sq1x, ctb[1]+sq1y]
#     point1 = [ctb[0]+sq2x, ctb[1]+sq2y]
#
#     return [point1, point2]


def calculate_square_first_side(points_data):
    # bond point
    bx, by = points_data[0]
    # middle point
    mx, my = points_data[1]

    # center to bond
    ctb = [bx - mx, by - my]
    ctb_len = get_vector_length(ctb)
    ctb = [ctb[0] * DOMAIN_LEN / 2 / ctb_len, ctb[1] * DOMAIN_LEN / 2 / ctb_len]

    ctb_perp = [-ctb[1], ctb[0]]

    ctb_add1 = [ctb[0] + ctb_perp[0], ctb[1] + ctb_perp[1]]
    point1 = [mx + ctb_add1[0], my + ctb_add1[1]]
    ctb_add2 = [ctb[0] - ctb_perp[0], ctb[1] - ctb_perp[1]]
    point2 = [mx + ctb_add2[0], my + ctb_add2[1]]

    return [point1, point2]


def calculate_square_second_side(square_side, points_data, prev_point, next_point):
    # bond point
    bx, by = points_data[0]
    # middle point
    mx, my = points_data[1]
    # square points
    sq1 = square_side[0]
    sq2 = square_side[1]
    sq1x, sq1y = sq1
    sq2x, sq2y = sq2
    # square prev and next
    sq_prev_point = square_side[2]
    sq_next_point = square_side[3]

    # center to bond
    ctb = [bx - mx, by - my]
    ctb_len = get_vector_length(ctb)
    ctb = [ctb[0] * DOMAIN_LEN / ctb_len / 2, ctb[1] * DOMAIN_LEN / ctb_len / 2]

    p1 = [ctb[0] + sq1x, ctb[1] + sq1y]
    p2 = [ctb[0] + sq2x, ctb[1] + sq2y]

    np1 = np2 = pp1 = pp2 = snp1 = snp2 = spp1 = spp2 = 0
    if next_point:
        np1 = euclidean_dist(next_point, p1)
        np2 = euclidean_dist(next_point, p2)
    if prev_point:
        pp1 = euclidean_dist(prev_point, p1)
        pp2 = euclidean_dist(prev_point, p2)
    if sq_next_point:
        snp1 = euclidean_dist(sq_next_point, sq1)
        snp2 = euclidean_dist(sq_next_point, sq2)
    if sq_prev_point:
        spp1 = euclidean_dist(sq_prev_point, sq1)
        spp2 = euclidean_dist(sq_prev_point, sq2)
    if np1 + pp2 + snp2 + spp1 < np2 + pp1 + snp1 + spp2:
        return [p2, p1, sq1, sq2]
    else:
        return [p1, p2, sq2, sq1]
