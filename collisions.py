import config


def check_object_collision(obj1, obj2):
    px, py = obj1.position
    qx, qy = obj2.position

    if (abs(px - qx) > 1) and (abs(py - qy) > 1):
        return False

    segments_obj1 = list(obj1.segments) if hasattr(obj1, 'segments') else []
    segments_obj2 = list(obj2.segments) if hasattr(obj2, 'segments') else []

    px *= config.TILE_WIDTH
    py *= config.TILE_HEIGHT
    qx *= config.TILE_WIDTH
    qy *= config.TILE_HEIGHT

    segments_obj1 = [((px + a, py + b), (px + c, py + d))
                     for ((a, b), (c, d)) in segments_obj1]
    segments_obj2 = [((qx + a, qy + b), (qx + c, qy + d))
                     for ((a, b), (c, d)) in segments_obj2]

    for segment1 in segments_obj1:
        for segment2 in segments_obj2:
            if check_segments_collision(segment1, segment2):
                return True
    return False


def det(p1, p2, p3):
    (x1, y1, x2, y2) = (p3[0] - p1[0], p3[1] - p1[1],
                        p2[0] - p1[0], p2[1] - p1[1])
    return x1 * y2 - x2 * y1


def check_on_segment(p1, p2, p3):
    return (min(p1[0], p2[0]) <= p3[0] <= max(p1[0], p2[0])
            and min(p1[1], p2[1]) <= p3[1] <= max(p1[1], p2[1]))


def check_segments_collision(seg1, seg2):
    (a, b, c, d) = (seg1[0], seg1[1], seg2[0], seg2[1])

    v1 = det(c, d, a)
    v2 = det(c, d, b)
    v3 = det(a, b, c)
    v4 = det(a, b, d)

    if (v1 * v2 < 0) and (v3 * v4 < 0):
        return True
    if (abs(v1) < config.EPS) and check_on_segment(c, d, a):
        return True
    if (abs(v2) < config.EPS) and check_on_segment(c, d, b):
        return True
    if (abs(v3) < config.EPS) and check_on_segment(a, b, c):
        return True
    if (abs(v4) < config.EPS) and check_on_segment(a, b, d):
        return True
    return False
