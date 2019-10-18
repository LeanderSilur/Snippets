import bpy
import bmesh
import numpy as np
from mathutils import Vector
from math import floor, ceil
import scipy.ndimage


class Brick(object):
    def __init__(self, name):
        self.bm = bmesh.new()
        self.bm.from_mesh(bpy.data.objects[name].data)
        self.bm.verts.ensure_lookup_table()
        self.bm.faces.ensure_lookup_table()
        self.kernel = None

    def instantiate(self, bm_target, at=Vector((0, 0, 0))):
        verts = [bm_target.verts.new(v.co + at) for v in self.bm.verts]
        faces = []
        for f in self.bm.faces:
            face_verts = [verts[v.index] for v in f.verts]
            faces.append(bm_target.faces.new(face_verts))
        return faces

    def place(self, bm_target, grid, color_grid):
        sx, sy, sz = 0.008, 0.008, 0.0096
        for z, y_ in enumerate(grid):
            for y, x_ in enumerate(y_):
                for x, value in enumerate(x_):
                    if value:
                        faces = self.instantiate(bm_target, Vector((sx*x, sy*y, sz*z)))
                        mat = 1 if color_grid[z, y, x] > 40 else 0
                        for f in faces:
                            f.material_index = mat


depsgraph = bpy.context.evaluated_depsgraph_get()
smoke_obj = bpy.data.objects['domain'].evaluated_get(depsgraph)
smoke_domain_mod = smoke_obj.modifiers[0]
settings = smoke_domain_mod.domain_settings
grid = settings.density_grid

dimensions = np.flip(np.array(smoke_obj.dimensions))
samples_smoke = dimensions / np.max(dimensions) * settings.resolution_max
samples_smoke = np.floor(samples_smoke)
samples_lego = dimensions / np.array([0.0032, 0.008, 0.008])
samples_lego = np.floor(samples_lego)

zoom_factor = samples_lego / samples_smoke * 3


grid = np.array(grid).reshape(samples_smoke.astype(int))
grid = scipy.ndimage.zoom(grid, zoom_factor, order=1)

density_grid = scipy.ndimage.convolve(grid, np.ones((9, 6, 6)))[::9, ::3, ::3]
max_grid = np.ones(grid.shape, dtype=np.float)[::9, ::3, ::3] * 0.065


brick_1 = Brick('brick_1')
brick_1.kernel = np.array([[[1, 1, 1]]]) / 8
brick_1.kernel = np.repeat(np.repeat(brick_1.kernel, 9, axis=0), 3, axis=1)
brick1_grid = scipy.ndimage.convolve(grid, brick_1.kernel)[::9, ::3, ::3]

brick2a = Brick('brick_2a')
brick2a.kernel = np.array([[[-6, -6, -1, 0, 1, 1]],
                           [[-6, -5, 0, 1, 1, 1]],
                           [[-5, -3, 0, 1, 1, 1]],
                           [[-4, -1, 0, 1, 1, 1]],
                           [[-3, 1, 0, 1, 1, 1]],
                           [[-2, 0, 1, 1, 1, 1]],
                           [[-1, 0, 1, 1, 1, 1]],
                           [[1, 3, 1, 1, 1, 1]],
                           [[3, 3, 1, 1, 1, 1]]
                           ]) / 84
brick2a.kernel = np.repeat(brick2a.kernel, 3, axis=1)
brick2a_grid = scipy.ndimage.convolve(grid, brick2a.kernel)[::9, ::3, ::3]

brick2b = Brick('brick_2b')
brick2b.kernel = np.flip(brick2a.kernel, axis=2)
brick2b_grid = scipy.ndimage.convolve(grid, brick2b.kernel)[::9, ::3, ::3]

brick2c = Brick('brick_2c')
brick2c.kernel = np.swapaxes(brick2a.kernel, 1, 2)
brick2c_grid = scipy.ndimage.convolve(grid, brick2c.kernel)[::9, ::3, ::3]

brick2d = Brick('brick_2d')
brick2d.kernel = np.swapaxes(brick2b.kernel, 1, 2)
brick2d_grid = scipy.ndimage.convolve(grid, brick2d.kernel)[::9, ::3, ::3]

max_grid = np.maximum(max_grid, brick1_grid)
max_grid = np.maximum(max_grid, brick2a_grid)
max_grid = np.maximum(max_grid, brick2b_grid)
max_grid = np.maximum(max_grid, brick2c_grid)
max_grid = np.maximum(max_grid, brick2d_grid)

bm = bmesh.new()
brick_1.place(bm, brick1_grid == max_grid, density_grid)
brick2a.place(bm, brick2a_grid == max_grid, density_grid)
brick2b.place(bm, brick2b_grid == max_grid, density_grid)
brick2c.place(bm, brick2c_grid == max_grid, density_grid)
brick2d.place(bm, brick2d_grid == max_grid, density_grid)

bm.to_mesh(bpy.data.objects['result'].data)
bm.free()
