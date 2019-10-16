class Vector(object):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
    
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

    def angle2d(self):
        return math.atan2(self.y, self.x)
