import bpy
import subprocess

REBUILD = 0
if REBUILD:
    subprocess.call([
        "g++",
        bpy.path.abspath('//../main.cpp'),
        bpy.path.abspath('//../PtTree.cpp'),
        "-o",
        bpy.path.abspath('//PtTree')
        ])


# Collect the input data.
verts = bpy.data.meshes['PointCloud'].vertices
query_amount = 5
query_obj = bpy.data.objects['Search']
query_pos = query_obj.location
query_radius = query_obj.dimensions[0] / 2

points = [str(v.co.x) + ',' + str(v.co.y) for v in verts]

args = [
    bpy.path.abspath('//PtTree.exe'),
    str(query_amount),
    str(query_radius),
    str(query_pos.x) + ',' + str(query_pos.y),
    *points
    ]


# Make the call.
proc = subprocess.run(args, encoding='utf-8', stdout=subprocess.PIPE)
stdout = proc.stdout.split('\n')

[print(line) for line in stdout]
ids = [int(line.split(" ")[0]) for line in stdout]

    
# Visualize the output.
bpy.ops.object.mode_set(mode="OBJECT")

for i in range(len(verts)):
    verts[i].select = False
    if i in ids:
        verts[i].select = True
    
bpy.ops.object.mode_set(mode="EDIT")