import bpy
import numpy as np
import mathutils

scn = bpy.context.scene
base_intensity = list(scn.world.color)
view_layer = bpy.context.view_layer
cam_mat = scn.camera.matrix_world
cam_loc, _, _ = cam_mat.decompose()
lamps = [ob for ob in scn.objects if ob.type=='LIGHT']
cam = scn.camera.data
render = scn.render
horizontal = cam.sensor_width/2
vertical = horizontal/render.resolution_x*render.resolution_y

width = render.resolution_x
height = render.resolution_y
rays = np.zeros((height, width, 3), dtype=float)

ray_width = np.linspace(-horizontal, horizontal, num=width, dtype=float).reshape(1, -1)
ray_width = np.repeat(ray_width, height, axis = 0)
ray_height = np.linspace(-vertical, vertical, num=height, dtype=float).reshape(-1, 1)
ray_height = np.repeat(ray_height, width, axis = 1)
ray_depth = np.zeros((height, width), dtype=float) - cam.lens

rays = np.stack([ray_width, ray_height, ray_depth], axis = 2)

pixels = np.zeros((height, width, 4), dtype=float)

for y in range(height):
    for x in range(width):
        ray = cam_mat @ mathutils.Vector(rays[y, x]) - cam_loc
        result, loc, nor, ind, ob, mat = scn.ray_cast(view_layer, cam_loc, ray)
        
        if (result):
            intensity = base_intensity[:]
            
            for lamp in lamps:
                dir = lamp.location - loc
                dirn = dir.normalized()
                
                start = loc + dirn * 1e-4
                hit,_,_,_,_,_ = scn.ray_cast(view_layer, start, dirn)
                if not hit:
                    multiplier = max(0, min(1, 1 - dir.length / lamp.data.distance)) * lamp.data.energy * max(0, dirn.dot(nor))
                    intensity[0] += multiplier * lamp.data.color[0]
                    intensity[1] += multiplier * lamp.data.color[1]
                    intensity[2] += multiplier * lamp.data.color[2]
            
            pixels[y, x] = intensity[0], intensity[1], intensity[2], 255
            
img = bpy.data.images.get("name")
if (    (not img) or
        (img.size[0] != width or img.size[1] != height)):
    img = bpy.data.images.new("name", width, height)
img.pixels = pixels.reshape(-1)
