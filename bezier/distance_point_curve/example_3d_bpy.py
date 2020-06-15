import bpy
import mathutils
import numpy as np

# load bezier.py module
import importlib.util
spec = importlib.util.spec_from_file_location("bezier", bpy.path.abspath("//bezier.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
Bezier = mod.Bezier

def closest_point_to_line(pt, a, b):
    ab = b-a
    ab2 = np.linalg.norm(ab)
    ap_dot_ab = np.dot(p-a, ab)
    t = ap_dot_ab / ab2
    return a + ab * t 

# generate Bezier object from Blender curve named 'Curve'
bezier_points = bpy.data.objects['Curve'].data.splines[0].bezier_points
points = [
    bezier_points[0].co,
    bezier_points[0].handle_right,
    bezier_points[1].handle_left,
    bezier_points[1].co
]
points = np.array(points)
bez = Bezier(points)

print(bez.coeffs)

# calculate closest t-to-point from mesh-object named 'Point'
point_ob = bpy.data.objects['Point']
verts = point_ob.data.vertices
pt = np.array(point_ob.matrix_world @ verts[0].co)
closest = bez.closest(pt)
verts[1].co = point_ob.matrix_world.inverted() @ mathutils.Vector(closest)

# calculate closest t-to-line from mesh-object named 'Line'
line_ob = bpy.data.objects['Line']
verts = line_ob.data.vertices
a = np.array(line_ob.matrix_world @ verts[0].co)
b = np.array(line_ob.matrix_world @ verts[1].co)

# closest = bez.closest_to_line(a, b)

# # display it
# line_ob = bpy.data.objects['Line_Vis']
# verts = line_ob.data.vertices
# a = np.array(line_ob.matrix_world @ verts[0].co)
# b = np.array(line_ob.matrix_world @ verts[1].co)
# verts[1].co = point_ob.matrix_world.inverted() @ mathutils.Vector(closest)

