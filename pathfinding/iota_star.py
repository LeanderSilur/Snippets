import bpy
import sys
import bmesh
import mathutils
import math
import time
import graph as IOTA

def vis_path(path):
    bm = bmesh.new()
    for v in path:
        bm.verts.new(v.position)
        
    bm.verts.ensure_lookup_table()
    for i in range(len(bm.verts)):
        if i > 0:
            bm.edges.new((bm.verts[i], bm.verts[i-1]))
    
    verts = [o for o in bmesh.ops.extrude_edge_only(bm, edges=bm.edges)['geom']
                if isinstance(o, bmesh.types.BMVert)]
    for v in verts:
        v.co.z += 0.04
    ob = bpy.data.objects['path']
    bm.to_mesh(ob.data)
    bm.free()
    


def reconstruct_path(v):
    path = [v]
    while v.previous != v:
        intersections = line_of_sight_intersections(v, v.previous)
        path.extend(intersections)
        path.append(v.previous)
        v = v.previous
    return path[::-1]
        
def get_visible(start):
    openList = [edge.other for edge in start.edges]
    closedList = [start]
    
    while len(openList):
        currentNode = openList.pop(0)
        closedList.append(currentNode)
        
        for edge in currentNode.edges:
            v = edge.other
            if v not in closedList and v not in openList:
                if line_of_sight(start, v):
                    openList.append(v)
    closedList.remove(start)
    return closedList

def iota_star(start, target):
    openList = [start]
    closedList = []
    
    start.g = 0
    start.calc_h(target)
    start.f = start.g + start.h
    start.previous = start
    
    # first, check if there is a direct line to the start
    if line_of_sight(start, target):
        target.previous = start
        return reconstruct_path(target)
    
    while len(openList):
        openList.sort(key=lambda v: v.f)
        currentNode = openList.pop(0)
        closedList.append(currentNode)
        
        
        visible = get_visible(currentNode)
        visible = [v for v in visible if v not in closedList]
        
        if currentNode == target:
            print("Reached target", target)
            return reconstruct_path(target)
        
        
        added = []
        
        for v in visible:
            # check if the visible vertex is connected
            # to other not visible vertices
            connect = False
            
            for e in v.edges:
                if e.other not in closedList:
                    if e.other not in visible:
                        on_left_side = is_left(currentNode.position, v.position, e.other.position)
                        if not e.has_face(on_left_side):
                            connect = True
                            break
            if v == target:
                connect = True
                
            if not connect:
                closedList.append(v)
            if connect:
                if v not in openList:
                    v.calc_h(target)
                    v.g = sys.maxsize
                    v.f = sys.maxsize
                    v.previous = None
                    openList.append(v)
                    added.append(v)
                    
                dist = currentNode.distance3d(v)
                if currentNode.g + dist < v.g:
                    v.previous = currentNode
                    v.g = currentNode.g + dist
                    v.f = v.g + v.h
               
        for v in added:
            print("   ", v, v.previous,  "{:.2f}".format(v.g), "{:.2f}".format(v.f))
    return None

def line_of_sight(a, b):
    edge1 = None
    for edge in a.edges:
        if edge.left:
            if in_angle(a.position, edge.other.position, edge.left.other.position, b.position):
                edge1 = edge.inv.right
                break
    
    if edge1 == None: return False

    res, el = get_collision_from_edge(edge1, a, b)
    while res:
        res, el = get_collision_from_edge(el, a, b)
    return el != None

# same, but different
def line_of_sight_intersections(a, b):
    edge1 = None
    for edge in a.edges:
        if edge.other == b:
            return []
        if edge.left:
            if in_angle(a.position, edge.other.position, edge.left.other.position, b.position):
                edge1 = edge.inv.right
    if edge1 == None:
        raise Exception("expected possible path")
    res, el = True, edge1
    intersections = []
    
    while res:
        edge_intersect = el.intersect_2d(a, b)
        intersections.append(edge_intersect)
        
        res, el = get_collision_from_edge(el, a, b)
    return intersections
    
def get_collision_from_edge(edge, start, target):
    if not edge.right:
        return False, None
    
    if edge.right.other == target:
        return False, target
    
    if is_left(start.position, target.position, edge.right.other.position):
        return True, edge.right
    else: # is_right
        return True, edge.right.inv.right



def create_graph():
    g = IOTA.Graph()

    bm = bmesh.new()
    bm.from_mesh(bpy.data.objects['knots'].data)
    for v in bm.verts:
        g.add_vertex(tuple(v.co))

    for e in bm.edges:
        v1 = e.verts[0]
        v2 = e.verts[1]
        
        # TODO: Improve this for vertical faces.
        face_l, face_r = False, False
        angle = math.atan2(v2.co[1] - v1.co[1], v2.co[0] - v1.co[0])
        for face in e.link_faces:
            v3 = [v for v in face.verts if v.index not in [v1.index, v2.index]][0]
            y_rotated = (v3.co[0] - v1.co[0]) * math.sin(-angle) + (v3.co[1] - v1.co[1]) * math.cos(-angle)
            if y_rotated == 0:
                raise Exception("Collinearity.", v3.index, v1.index, v2.index)
            if (y_rotated > 0): face_l = True
            elif (y_rotated < 0): face_r = True
        
        g.add_edge(v1.index, v2.index, face_l, face_r)
    
    g.freeze()
    return g
    

# Create graph once.

def update(context):
    g = create_graph()
    print("________")
    
    # get start and target
    start_v = bpy.data.objects['start'].location
    target_v = bpy.data.objects['target'].location
    
    start = g.insert_point(tuple(start_v))
    target = g.insert_point(tuple(target_v))
    
    
    # calculate path
    path = iota_star(start, target)
    
    vis_path(path)


for h in bpy.app.handlers.depsgraph_update_post:
    bpy.app.handlers.depsgraph_update_post.remove(h)
bpy.app.handlers.depsgraph_update_post.append(update)

update(bpy.context)