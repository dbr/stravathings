def _vec2d_dist(p1, p2):
    return (p1[0] - p2[0])**2 + (p1[1] - p2[1])**2


def _vec2d_sub(p1, p2):
    return (p1[0]-p2[0], p1[1]-p2[1])


def _vec2d_mult(p1, p2):
    return p1[0]*p2[0] + p1[1]*p2[1]


def ramerdouglas(line, dist):
    """Does Ramer-Douglas-Peucker simplification of a line with `dist`
    threshold.

    `line` is a list-of-tuples, where each tuple is a 2D coordinate

    Usage is like so:

    >>> myline = [(0.0, 0.0), (1.0, 2.0), (2.0, 1.0)]
    >>> simplified = (myline, dist = 1.0)
    """

    if len(line) < 3:
        return line

    begin, end = line[0], line[-1]

    distSq = []
    for curr in line[1:-1]:
        tmp = (
            _vec2d_dist(begin, curr) - _vec2d_mult(_vec2d_sub(end, begin), _vec2d_sub(curr, begin)) ** 2 / _vec2d_dist(begin, end))
        distSq.append(tmp)

    maxdist = max(distSq)
    if maxdist < dist ** 2:
        return [begin, end]

    pos = distSq.index(maxdist)
    return (ramerdouglas(line[:pos + 2], dist) +
            ramerdouglas(line[pos + 1:], dist)[1:])




def getSquareDistance(p1, p2):
    """
    Square distance between two points
    """
    dx = p1[0] - p2[0]
    dy = p1[1] - p2[1]

    return dx * dx + dy * dy


def getSquareSegmentDistance(p, p1, p2):
    """
    Square distance between point and a segment
    """
    x = p1[0]
    y = p1[1]

    dx = p2[0] - x
    dy = p2[1] - y

    if dx != 0 or dy != 0:
        t = ((p[0] - x) * dx + (p[1] - y) * dy) / (dx * dx + dy * dy)

        if t > 1:
            x = p2[0]
            y = p2[1]
        elif t > 0:
            x += dx * t
            y += dy * t

    dx = p[0] - x
    dy = p[1] - y

    return dx * dx + dy * dy


def simplifyRadialDistance(points, tolerance):
    length = len(points)
    prev_point = points[0]
    new_points = [prev_point]

    for i in range(length):
        point = points[i]

        if getSquareDistance(point, prev_point) > tolerance:
            new_points.append(point)
            prev_point = point

    if prev_point != point:
        new_points.append(point)

    return new_points


def simplifyDouglasPeucker(points, tolerance):
    length = len(points)
    markers = [0] * length  # Maybe not the most efficent way?

    first = 0
    last = length - 1

    first_stack = []
    last_stack = []

    new_points = []

    markers[first] = 1
    markers[last] = 1

    while last:
        max_sqdist = 0

        for i in range(first, last):
            sqdist = getSquareSegmentDistance(points[i], points[first], points[last])

            if sqdist > max_sqdist:
                index = i
                max_sqdist = sqdist

        if max_sqdist > tolerance:
            markers[index] = 1

            first_stack.append(first)
            last_stack.append(index)

            first_stack.append(index)
            last_stack.append(last)

        # Can pop an empty array in Javascript, but not Python, so check
        # the length of the list first
        if len(first_stack) == 0:
            first = None
        else:
            first = first_stack.pop()

        if len(last_stack) == 0:
            last = None
        else:
            last = last_stack.pop()

    for i in range(length):
        if markers[i]:
            new_points.append(points[i])

    return new_points


def simplify(points, tolerance=0.1, highestQuality=True):
    sqtolerance = tolerance * tolerance

    if not highestQuality:
        points = simplifyRadialDistance(points, sqtolerance)

    points = simplifyDouglasPeucker(points, sqtolerance)

    return points


if __name__ == '__main__':
    def plot(pl):
        max_x = max(pl, key = lambda k: k[0])[0]
        max_y = max(pl, key = lambda k: k[1])[1]

        min_x = min(pl, key = lambda k: k[0])[0]
        min_y = min(pl, key = lambda k: k[1])[1]

        width, height = 16, 16

        out_grid = [[" " for _ in range(width)] for _ in range(height)]

        for p in pl:
            cur_x = p[0]
            cur_y = p[1]
            norm_x = (cur_x - min_x) / (max_x-min_x)
            norm_y = (cur_y - min_y) / (max_y-min_y)

            out_grid[int(norm_x * (width-1))][int(norm_y*(height-1))] = "*"

        for row in out_grid:
            print " ".join(c for c in row)


    pl = [
        (0.0, 0.0),
        (1.0, 0.0),
        (2.0, -1.0),
        (3.0, -2.0),
        (4.0, -1.0),
        (5.0, 0.0),
        (6.0, 3.0),
        (7.0, 2.0),
        (8.0, 4.0),
    ]*100

    import time

    start = time.time()
    simple = simplify(pl, 0.1)
    end = time.time()

    print "%.02fms" % ((end-start)*1000)
    print "%s reduced to %s" % (len(pl), len(simple))

    plot(pl)
    print "#"*40
    plot(simple)
