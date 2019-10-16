class Vector(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    
    def clone(self):
        return Vector(self.x, self.y, self.z)

    def __iter__(self):
        return iter((self.x, self.y, self.z))

    def __getitem__(self, key):
        if key == 0:
            return self.x
        if key == 1:
            return self.y
        if key == 2:
            return self.z
        raise IndexError("Points only support the indices 0, 1, 2.")

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __add__(self, other):
        assert isinstance(other, Point)
        return Point(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        assert isinstance(other, Point)
        return Point(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            return Point(self.x * other, self.y * other, self.z * other)

        # dot product
        if isinstance(other, Point):
            return self.x * other.x + self.y * other.y + self.z * other

        raise TypeError("Only float/int multiplication or a vector dot product make sense to me.")
        
    def __truediv__(self, n):
        assert isinstance(n, float) or isinstance(n, int)
        return Point(self.x / n, self.y / n, self.z / n)

    def dot3d(self, other):
        return self.x * other.x + self.y * other.y + self.z * other

    def dot2d(self, other):
        return self.x * other.x + self.y * other.y

    def cross3d(self, other):
        return Point(self.y * other.z - self.z * other.y,
                     self.z * other.x - self.x * other.z,
                     self.x * other.y - self.y * other.x)
    
    def cross2d(self, other):
        return self.x * other.y - self.y * other.x

    def on_left(self, a, b):
        assert isinstance(a, Point) and isinstance(b, Point)
        return (b.x - a.x) * (self.y - a.y) - (b.y - a.y) * (self.x - a.x) > 0

    def in_angle(self, base, right, left):
        return self.is_left(base, right) and not self.is_left(base, left)

    def length(self):
        return (self.x * self.x + self.y * self.y + self.z * self.z) ** 0.5

    def length2(self):
        return (self.x * self.x + self.y * self.y + self.z * self.z)

    def length2d(self):
        return (self.x * self.x + self.y * self.y) ** 0.5

    def angle2d(self):
        return math.atan2(self.y, self.x)
    
    def normalize(self):
        length = self.length()
        self.x /= length
        self.y /= length
        self.z /= length

class Line(object):
    def __init__(self, a, b):
        assert isinstance(a, Vector) and isinstance(b, Vector)
        self.a = a
        self.b = b
    def closest_point(self, p):
        ap = p - self.a
        ab = p - self.b
        t = ap.dot(ab) / ab.length2()
        t = min(1, max(0, t))
        return self.a + ab * t

class Triangle(object):
    def __init__(self, a, b, c):
        assert isinstance(a, Vector) and isinstance(b, Vector) and isinstance(c, Vector)
        self.a = a
        self.b = b
        self.c = c

    # returns tuple: (position)
    def closest_point(self, p):
        a, b, c = self.a, self.b, self.c
        
        # for loop covers the cases, where p is not above the triangle
        for x, y in [[a, b], [b, c], [c, a]]:
            if p.on_left(x, y):    
                line = Line(x, y)
                return line.closest_point(p)

        r = b - a
        s = c - a
        # https://math.stackexchange.com/questions/305642/how-to-find-surface-normal-of-a-triangle
        n = r.cross3d(s)
        n.normalize()
        
        pz = -(n.x * (p.x - a.x) + n.y * (p.y - a.y)) / n.z + a.z
        return Vector(p.x, p.y, pz)
