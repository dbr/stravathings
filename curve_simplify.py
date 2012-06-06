def ramerdouglas(line, dist):
    """Does Ramer-Douglas-Peucker simplification of a line with `dist`
    threshold.  `line` must be a list of Vec objects, all of the same
    type (either 2d or 3d)

    From http://stackoverflow.com/a/2577352/745
    """

    if len(line) < 3:
        return line

    begin, end = line[0], line[-1]
    distSq = [begin.distSq(curr) -
        ((end - begin) * (curr - begin)) ** 2 /
        begin.distSq(end) for curr in line[1:-1]]

    maxdist = max(distSq)
    if maxdist < dist ** 2:
        return [begin, end]

    pos = distSq.index(maxdist)
    return (ramerdouglas(line[:pos + 2], dist) + 
            ramerdouglas(line[pos + 1:], dist)[1:])


class Line:
    """Polyline. Contains a list of points and outputs
    a simplified version of itself."""
    def __init__(self, points):
        pointclass = points[0].__class__
        for i in points[1:]:
            if i.__class__ != pointclass:
                raise TypeError("""All points in a Line
                                must have the same type""")
        self.points = points

    def simplify(self, dist):
        if self.points[0] != self.points[-1]:
            # Non-looping
            points = ramerdouglas(self.points, dist)
        else:
            points = ramerdouglas(
                self.points[:-1], dist) + self.points[-1:]
        return self.__class__(points)

    def __repr__(self):
        return '{0}{1}'.format(self.__class__.__name__,
            tuple(self.points))

class Vec:
    """Generic vector class for n-dimensional vectors
    for any natural n."""
    def __eq__(self, obj):
        """Equality check."""
        if self.__class__ == obj.__class__:
            return self.coords == obj.coords
        return False

    def __repr__(self):
        """String representation. The string is executable as Python
        code and makes the same vector."""
        return '{0}{1}'.format(self.__class__.__name__, self.coords)

    def __add__(self, obj):
        """Add a vector."""
        if not isinstance(obj, self.__class__):
            raise TypeError

        return self.__class__(*map(sum, zip(self.coords, obj.coords)))

    def __neg__(self):
        """Reverse the vector."""
        return self.__class__(*[-i for i in self.coords])

    def __sub__(self, obj):
        """Substract object from self."""
        if not isinstance(obj, self.__class__):
            raise TypeError

        return self + (- obj)

    def __mul__(self, obj):
        """If obj is scalar, scales the vector.
        If obj is vector returns the scalar product."""
        if isinstance(obj, self.__class__):
            return sum([a * b for (a, b) in zip(self.coords, obj.coords)])

        return self.__class__(*[i * obj for i in self.coords])

    def dist(self, obj = None):
        """Distance to another object. Leave obj empty to get
        the length of vector from point 0."""
        return self.distSq(obj) ** 0.5

    def distSq(self, obj = None):
        """ Square of distance. Use this method to save
        calculations if you don't need to calculte an extra square root."""
        if obj is None:
            obj = self.__class__(*[0]*len(self.coords))
        elif not isinstance(obj, self.__class__):
            raise TypeError('Parameter must be of the same class')

        # simple memoization to save extra calculations
        if obj.coords not in self.distSqMem:
            self.distSqMem[obj.coords] = sum([(s - o) ** 2 for (s, o) in
                zip(self.coords, obj.coords)])
        return self.distSqMem[obj.coords]

class Vec3D(Vec):
    """3D vector"""
    def __init__(self, x, y, z):
        self.coords = x, y, z
        self.distSqMem = {}

    @property
    def x(self):
        return self.coords[0]

    @property
    def y(self):
        return self.coords[1]

    @property
    def z(self):
        return self.coords[2]

class Vec2D(Vec):
    """2D vector"""
    def __init__(self, x, y):
        self.coords = x, y
        self.distSqMem = {}

    @property
    def x(self):
        return self.coords[0]

    @property
    def y(self):
        return self.coords[1]


def reduce_curve(curve, dist):
    """Takes a list of tuples, and a distance.

    >>> curve = [(0, 0), (1, 0), (2, 1), ...]
    >>> reduce_curve(curve, 0.5)
    """

    # TODO: This function simplifies the interface, preventing stuff
    # needing to be wrapped up in Vec2D/Line classes. Could skip this
    # step and simplify the ramerdouglas() function

    comp = Line([Vec2D(p[0], p[1]) for p in curve])
    simp = comp.simplify(dist)

    print "%s reduced to %s" % (
        len(comp.points),
        len(simp.points))

    return [(p.x, p.y) for p in simp.points]


'''
import math

def PerpendicularDistance(line_point_1, line_point_2, point_pos):
    x1, y1 = line_point_1
    x2, y2 = line_point_2
    x3, y3 = point_pos

    px = x2-x1
    py = y2-y1

    something = px*px + py*py

    u =  ((x3 - x1) * px + (y3 - y1) * py) / something

    if u > 1:
        u = 1
    elif u < 0:
        u = 0

    x = x1 + u * px
    y = y1 + u * py

    dx = x - x3
    dy = y - y3

    # Note: If the actual distance does not matter,
    # if you only want to compare what this function
    # returns to other results of this function, you
    # can just return the squared distance instead
    # (i.e. remove the sqrt) to gain a little performance

    dist = math.sqrt(dx*dx + dy*dy)

    return dist

def DouglasPeucker(PointList, epsilon, rec_level = 1):
     print ("#" * rec_level) + " Point List", PointList
     # Find the point with the maximum distance
     dmax = 0
     index = 0
     #for i = 2 to (length(PointList) - 1)
     for i in range(2, len(PointList)-1):
          d = PerpendicularDistance(point_pos = PointList[i], line_point_1 = PointList[0], line_point_2 = PointList[-1])
          if d > dmax:
              index = i
              dmax = d

     print ("#" * rec_level) + " index", index
     print ("#" * rec_level) + " dmax", dmax
     print ("#" * rec_level) + " epsilon", epsilon
     
     # If max distance is greater than epsilon, recursively simplify
     if dmax >= epsilon:
         # Recursive call
         print ("#" * rec_level), "Recursing"
         print ("#" * rec_level), "Before", PointList[1:index]
         print ("#" * rec_level), "After ", PointList[index:-1]

         before = PointList[1:index]
         after = PointList[index:-1]

         if len(before) < 2:
             recResults1 = before
         else:
             recResults1 = DouglasPeucker(before, epsilon, rec_level = rec_level + 1)

         if len(after) < 2:
             recResults2 = after
         else:
             recResults2 = DouglasPeucker(after, epsilon, rec_level = rec_level + 1)

         print ("#" * rec_level), "recResults1", recResults1
         print ("#" * rec_level), "recResults2", recResults2

         # Build the result list
         return recResults1[1:-1] + recResults2[1:]

     else:
         print ("#" * rec_level), "No more recursion"
         print ("#" * rec_level), PointList
         ResultList = [PointList[1], PointList[-1]]
         return PointList
'''

if __name__ == '__main__':
    pl = Line([
        Vec2D(0.0, 0.0),
        Vec2D(1.0, 0.0),
        Vec2D(2.0, -1.0),
        Vec2D(3.0, -2.0),
        Vec2D(4.0, -1.0),
        Vec2D(5.0, 0.0),
        Vec2D(6.0, 3.0),
        Vec2D(7.0, 2.0),
        Vec2D(8.0, 4.0),
    ])
    
    def plot(pl):
        max_x = max(pl, key = lambda k: k.x).x
        max_y = max(pl, key = lambda k: k.y).y
    
        min_x = min(pl, key = lambda k: k.x).x
        min_y = min(pl, key = lambda k: k.y).y
    
        width, height = 16, 16
    
        out_grid = [[" " for _ in range(width)] for _ in range(height)]
    
        for p in pl:
            cur_x = p.x
            cur_y = p.y
            norm_x = (cur_x - min_x) / (max_x-min_x)
            norm_y = (cur_y - min_y) / (max_y-min_y)
    
            out_grid[int(norm_x * (width-1))][int(norm_y*(height-1))] = "*"
    
        for row in out_grid:
            print " ".join(c for c in row)
    
    plot(pl.points)
    simple = pl.simplify(1.0)
    print "simplfied:", simple
    plot(simple.points)
    print len(pl.points), "and after", len(simple.points)
