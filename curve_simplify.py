def _vec2d_dist(p1, p2):
    return (p1[0] - p2[0])**2 + (p1[1] - p2[1])**2


def _vec2d_sub(p1, p2):
    return (p1[0]-p2[0], p1[1]-p2[1])


def _vec2d_mult(p1, p2):
    return p1[0]*p2[0] + p1[1]*p2[1]


def _ramerdouglas(line, dist):
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

    if begin == end:
        # Line segment begins/ends at same point
        # FIXME: This potentially drops a lot of points
        return [begin]

    distSq = (
        _vec2d_dist(begin, curr) - _vec2d_mult(_vec2d_sub(end, begin), _vec2d_sub(curr, begin)) ** 2 / _vec2d_dist(begin, end)
        for curr in line[1:-1])

    pos, maxdist = max(enumerate(distSq), key = lambda k: k[1])

    return (_ramerdouglas(line[:pos + 2], dist) +
            _ramerdouglas(line[pos + 1:], dist)[1:])


def ramerdouglas(line, dist):
    if line[0] != line[-1]:
        return _ramerdouglas(line, dist)
    else:
        return _ramerdouglas(line[:-1], dist) + line[-1:]


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
    simple = ramerdouglas(pl, 0.1)
    end = time.time()

    print "%.02fms" % ((end-start)*1000)
    print len(simple)

    plot(pl)
    print "#"*40
    plot(simple)
