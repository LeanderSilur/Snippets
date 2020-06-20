import numpy as np

# Bezier Class representing a CUBIC bezier defined by four
# control points.
# 
# at(t):            gets a point on the curve at t
# distance2(pt)      returns the closest distance^2 of
#                   pt and the curve
# closest(pt)       returns the point on the curve
#                   which is closest to pt
# maxes(pt)         plots the curve using matplotlib
class Bezier(object):
    # minimum and maximum for t
    boundaries = np.array([0, 1], dtype=np.float32)

    # Initialize the curve by assigning the control points.
    # Then create the coefficients.
    def __init__(self, points):
        assert isinstance(points, np.ndarray)
        assert points.dtype in [np.float32, np.float64]
        assert len(points.shape) == 2 and points.shape[0] == 4

        self.points = points.copy()
        self.dimension = points.shape[1]
        self.create_factors()
        self.create_coefficients()
    
    def create_factors(self):
        self.exp = dict()
        for i in [3, 4]:
            f = np.arange(i, -1, -1, dtype=np.float32)
            self.exp[i] = f.reshape(*f.shape, 1).repeat(self.dimension, axis=1)
            # something like => [[3, 3], [2, 2], [1, 1], [0, 0]]

    # Create the coefficients of the bezier equation, bringing
    # the bezier in the form:
    # f(t) = a * t^3 + b * t^2 + c * t^1 + d
    #
    # The coefficients have the same dimensions as the control
    # points.
    def create_coefficients(self):
        co_coeffs = np.array([[-1, 3, -3, 1], [3, -6, 3, 0], [-3, 3, 0, 0], [1, 0, 0, 0]], dtype=np.float32)
        coeffs = np.multiply(co_coeffs.reshape((4, 4, 1)), self.points.reshape((1, 4, self.dimension)))
        self.coeffs = np.sum(coeffs, axis=1).reshape(-1, 4, self.dimension)

    # Return a point on the curve at the parameter t.
    def at(self, t):
        if type(t) != np.ndarray:
            t = np.array(t)
        pts = self.coeffs * np.power(t, self.exp[3])
        return np.sum(pts, axis = 1)

    # Return the closest DISTANCE (squared) between the point pt
    # and the curve.
    def distance2(self, pt):
        points, distances = self.measure_distance(pt)
        return np.min(distances)

    # Return the closest POINT between the point pt
    # and the curve.
    def closest(self, pt):
        points, distances = self.measure_distance(pt)
        index = np.argmin(distances)
        return points[index]

    # Measure the distance^2 and closest point on the curve of 
    # the point pt and the curve. This is done in three steps:

    # (1) Define the distance^2 depending on the pt. Use the squared
    # distance to prevent an additional root.
    #       D(t) = (f(t) - pt)^2

    # (2) The roots of D'(t) are the extremes of D(t) and contain the
    # closest points on the unclipped curve. Only keep the minima
    # by checking if D''(roots) > 0 and discard imaginary roots.

    # Compare the distances of "pt" to the minima as well as the
    # start and end of the curve and return the index of the
    # shortest distance.
    #
    # This desmos graph is a helpful visualization.
    # https://www.desmos.com/calculator/ktglugn1ya
    def measure_distance(self, pt):
        assert isinstance(pt, np.ndarray)
        assert pt.dtype == self.points.dtype
        assert pt.shape == (self.dimension,)

        coeffs = self.coeffs

        # These are the coefficients of the derivatives d/dx and d/(d/dx).
        da = 6*np.sum(coeffs[0][0]*coeffs[0][0])
        db = 10*np.sum(coeffs[0][0]*coeffs[0][1])
        dc = 4*(np.sum(coeffs[0][1]*coeffs[0][1]) + 2*np.sum(coeffs[0][0]*coeffs[0][2]))
        dd = 6*(np.sum(coeffs[0][0]*(coeffs[0][3]-pt)) + np.sum(coeffs[0][1]*coeffs[0][2]))
        de = 2*(np.sum(coeffs[0][2]*coeffs[0][2])) + 4*np.sum(coeffs[0][1]*(coeffs[0][3]-pt))
        df = 2*np.sum(coeffs[0][2]*(coeffs[0][3]-pt))

        dda = 5*da
        ddb = 4*db
        ddc = 3*dc
        ddd = 2*dd
        dde = de
        dcoeffs = np.stack([da, db, dc, dd, de, df])
        ddcoeffs = np.stack([dda, ddb, ddc, ddd, dde]).reshape(-1, 1)
        
        # Calculate the real extremes, by getting the roots of the first
        # derivativ of the distance function.
        extrema = Bezier.np_real_roots(dcoeffs)
        # Remove the roots which are out of bounds of the clipped range [0, 1].
        dd_clip = (np.sum(ddcoeffs * np.power(extrema, self.exp[4])) >= 0) & (extrema > 0) & (extrema < 1)
        minima = extrema[dd_clip]

        # Add the start and end position as possible positions.
        potentials = np.concatenate((minima, self.boundaries))

        # Calculate the points at the possible parameters t and 
        # get the index of the closest
        points = self.at(potentials.reshape(-1, 1, 1))
        distances = np.sum(np.square(points - pt), axis = 1)

        return points, distances


    def closest_to_line(self, a, b):
        points, distances = self.measure_distance_to_line(a, b)
        #return points[index]

    def measure_distance_to_line(self, a, b):
        for pt in [a, b]:
            assert isinstance(pt, np.ndarray)
            assert pt.dtype == self.points.dtype
            assert pt.shape == (self.dimension,)
        
        p = a.copy()
        q = b - a
        assert np.linalg.norm(q) != 0
        
        # r = (t (t (a * t + b) + c) + d - p ) / q

        # f(t, r) = (a t^3 + b t^2 + c t + d - p - rq)^2
        # Partial derivatives, find (t, r) where d/dt = 0 AND d/dr = 0
        # by substituting d/dr = 0 into d/dt

        # Wolframalpha d/dr (a t^3 + b t^2 + c t + d - p - q r)^2 = 0 for r
        a, b, c, d = self.coeffs
        # TODO assert a != 0
        
        dt_5 = 6 * np.sum(a * a)
        t = (-sqrt(b^2 - 3 a c) - b)/(3 a) and a!=0
        dt_4 = 6 * np.sum(a * a)
        dt_5 = 6 * np.sum(a * a)
        dt_5 = 6 * np.sum(a * a)
        dt_5 = 6 * np.sum(a * a)
        dt_5 = 6 * np.sum(a * a)

# + 10 a b t^4
# + 8 a c t^3
# + 4 b^2 t^3

# + 6 a d t^2
# + 6 b c t^2
# - 6 a p t^2
# - 6 a q r t^2

#  + 4 b d t
#  - 4 b p t
#  - 4 b q r t
#  + 2 c^2 t
#  + 2 c d
#  - 2 c p
#  - 2 c q r

#         return [1, 2]
#         points, distances = self.measure_distance(pt)
#         index = np.argmin(distances)
#         return points[index]




#     # Wrapper around np.roots, but only returning real
#     # roots and ignoring imaginary results.
#     @staticmethod
#     def np_real_roots(coefficients, EPSILON=1e-6):
#         r = np.roots(coefficients)
#         return r.real[abs(r.imag) < EPSILON]




# import bpy
# import mathutils
# def closest_point_to_line(pt, a, b):
#     ab = b-a
#     ab2 = np.linalg.norm(ab)
#     ap_dot_ab = np.dot(p-a, ab)
#     t = ap_dot_ab / ab2
#     return a + ab * t 

# # generate Bezier object from Blender curve named 'Curve'
# bezier_points = bpy.data.objects['Curve'].data.splines[0].bezier_points
# points = [
#     bezier_points[0].co,
#     bezier_points[0].handle_right,
#     bezier_points[1].handle_left,
#     bezier_points[1].co
# ]
# points = np.array(points)
# bez = Bezier(points)


# # calculate closest t-to-point from mesh-object named 'Point'
# point_ob = bpy.data.objects['Point']
# verts = point_ob.data.vertices
# pt = np.array(point_ob.matrix_world @ verts[0].co)
# closest = bez.closest(pt)
# verts[1].co = point_ob.matrix_world.inverted() @ mathutils.Vector(closest)

# # calculate closest t-to-line from mesh-object named 'Line'
# line_ob = bpy.data.objects['Line']
# verts = line_ob.data.vertices
# a = np.array(line_ob.matrix_world @ verts[0].co)
# b = np.array(line_ob.matrix_world @ verts[1].co)

# closest = bez.closest_to_line(a, b)

# # # display it
# # line_ob = bpy.data.objects['Line_Vis']
# # verts = line_ob.data.vertices
# # a = np.array(line_ob.matrix_world @ verts[0].co)
# # b = np.array(line_ob.matrix_world @ verts[1].co)
# # verts[1].co = point_ob.matrix_world.inverted() @ mathutils.Vector(closest)

