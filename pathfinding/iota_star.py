import bpy
import sys
import bmesh
import mathutils
import math
import time

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
    
def closest_node(g, pos):
    node, dist = g[0], sys.maxsize
    for v in g:
        ndist = (mathutils.Vector(v.position)-pos).length
        if (ndist < dist):
            dist = ndist
            node = v
    return node


def is_left(a, b, x):
    return (b[0] - a[0]) * (x[1] - a[1]) - (b[1] - a[1]) * (x[0] - a[0]) > 0

def in_angle(a, b, c, x):
    return is_left(a, b, x) and not is_left(a, c, x)

def add(a, b):
    return [a[0] + b[0], a[1] + b[1], a[2] + b[2]]
def sub(a, b):
    return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]
def mult(a, n):
    return [a[0]*n, a[1]*n, a[2]*n]
def cross(a, b):
    return a[0]*b[1] - a[1]*b[0]
def equals(a, b):
    return a[0] == b[0] and a[1] == b[1] and a[2] == b[2]












EPSILON = 1e-6

class Vertex(object):
    def __init__(self, position, id = 0):
        self.position = position
        self.id = id
        self.edges = []
        
        self.f = 0
        # walked distance
        self.g = sys.maxsize
        # heuristic estimate
        self.h = 0
        
        self.edge = None
        self.previous = None

    def add_neighbor(self, other, weight, angle, face_l, face_r):
        edge = Edge(self, other, weight, angle, face_l, face_r)
        self.edges.append(edge)
        return edge

    def get_weight(self, other):
        for e in self.edges:
            if e.other == other:
                return e.weight
        raise Exception("not good")
        
    def sort_edges(self):
        self.edges.sort(key=lambda edge: edge.angle)
        for i, edge in enumerate(self.edges):
            edge.index = i
            if edge.face_l:
                edge.left = self.edges[(i+1)%len(self.edges)]
            if edge.face_r:
                edge.right = self.edges[(i-1)%len(self.edges)]
    
    def calc_h(self, target):
        self.h = ( (target.position[0] - self.position[0])**2
                 + (target.position[1] - self.position[1])**2
                 + (target.position[2] - self.position[2])**2 ) **0.5
                 
    def distance2d2(self, other):
        return   ( (other.position[0] - self.position[0])**2
                 + (other.position[1] - self.position[1])**2 )
                 
    def distance2d(self, other):
        return   ( (other.position[0] - self.position[0])**2
                 + (other.position[1] - self.position[1])**2 ) ** 0.5
                 
    def distance3d(self, other):
        return   ( (other.position[0] - self.position[0])**2
                 + (other.position[1] - self.position[1])**2
                 + (other.position[2] - self.position[2])**2 ) ** 0.5
        
    def __str__(self):
        return str(self.id).zfill(2)# + ": " + (str(self.g) if self.g != sys.maxsize else "")
    
    def __lt__(self, other):
        return self.position < other.position

class Edge(object):
    def __init__(self, origin, other, weight, angle, face_l, face_r):
        self.origin = origin
        self.other = other
        self.weight = weight
        self.angle = angle
        self.face_l = face_l
        self.face_r = face_r
        self.index = 0
        self.inv = None
        self.left = None
        self.right = None
    
    def has_face(self, left):
        if left: return self.face_l == True
        return self.face_r == True
    
    def double_sided(self):
        return self.face_l and self.face_r
    
    def __str__(self):
        return "[" + str(self.origin.id) + "->"+str(self.other.id)+"]"
    
    def intersect_2d(self, start, target):
        p = self.origin.position
        r = sub(self.other.position, self.origin.position)
        q = start.position
        s = sub(target.position, start.position)
        
        rxs = cross(r, s)
        if abs(rxs) < 0.000000001:
            raise Exception("lines are collinear.", start.id, target.id, self.origin.id, self.other.id)
        
        t = cross(sub(start.position, self.origin.position), s) / rxs;
        
        pos = add(self.origin.position, mult(r, t))
        
        return EdgeIntersection(self, pos)

class EdgeIntersection(object):
    def __init__(self, edge, position):
        self.edge = edge
        self.position = position
    
class Graph:
    def __init__(self):
        self.vert_list = []

    def __iter__(self):
        return iter(self.vert_list)
    def __len__(self):
        return len(self.vert_list)
    def __getitem__(self, key):
        return self.vert_list[key]
    def get_vertex(self, i):
        return self.vert_list[i]

    def add_vertex(self, position):
        new_vertex = Vertex(position, len(self.vert_list))
        self.vert_list.append(new_vertex)
        return new_vertex

    def add_edge(self, frm_id, to_id, face_l, face_r, cost = -1):
        assert frm_id >= 0 and frm_id < len(self.vert_list) and to_id >= 0 and to_id < len(self.vert_list)
        
        frm = self.vert_list[frm_id]
        to = self.vert_list[to_id]
        
        if (cost < 0):
            cost = (  (frm.position[0]-to.position[0])**2
                    + (frm.position[1]-to.position[1])**2
                    + (frm.position[2]-to.position[2])**2  ) ** 0.5
        
        angle = math.atan2(to.position[1] - frm.position[1], to.position[0] - frm.position[0])
        rev_angle = angle - math.pi if angle >= 0 else angle + math.pi

        edge_frm = frm.add_neighbor(to, cost, angle, face_l, face_r)
        edge_to  = to.add_neighbor(frm, cost, rev_angle, face_r, face_l)
        edge_frm.inv = edge_to
        edge_to.inv = edge_frm

    def insert_point(self, location):
        triangles = []
        for v in self.vert_list:
            if equals(v.position, location):
                return v
            
            if v.position[0] < location[0]:
                for e in v.edges:
                    if e.other.position[0] > location[0]:
                        v1 = v
                        v2 = e.other
                        v3 = None
                        if e.left:
                            v3 = e.left.other
                        if (     v3 != None and
                                 is_left(v1.position, v2.position, location) and
                                 is_left(v2.position, v3.position, location) and
                                 is_left(v3.position, v1.position, location) ):
                             r = sub(v2.position, v1.position)
                             s = sub(v3.position, v1.position)
                             # cross
                             # https://math.stackexchange.com/questions/305642/how-to-find-surface-normal-of-a-triangle
                             nx = (r[1] * s[2]) - (r[2] * s[1])
                             ny = (r[2] * s[0]) - (r[0] * s[2])
                             nz = (r[0] * s[1]) - (r[1] * s[0])
                             l = (nx**2 + ny**2 + nz**2) ** 0.5
                             nx /= l
                             ny /= l
                             nz /= l
                             
                             bx, by, bz = v1.position
                             
                             p = location
                             
                             px, py, _ = p
                             pz = -(nx*(px-bx) + ny * (py-by)) / nz + bz
                             
                             distance = abs(p[2] - pz)
                             p = (px, py, pz)
                             triangles.append([distance, e, p])
                             
        if len(triangles) == 0: return None

        triangles.sort(key=lambda tri: tri[0])
        tris = triangles[0]
        pos = tris[2]
        edge1 = tris[1]
        edge2 = edge1.inv.right
        edge3 = edge2.inv.right
        v1, v2, v3 = edge1.origin, edge2.origin, edge3.origin
        
        # insert vertex
        center_vertex = self.add_vertex(pos)
        self.add_edge(v1.id, center_vertex.id, True, True)
        self.add_edge(v2.id, center_vertex.id, True, True)
        self.add_edge(v3.id, center_vertex.id, True, True)
        
        center_vertex.sort_edges()
        v1.sort_edges()
        v2.sort_edges()
        v3.sort_edges()
        print("added vert", center_vertex, center_vertex.position)
        
        return center_vertex
                

    def freeze(self):
        for i in range(len(self.vert_list)):
            self.vert_list[i].sort_edges()

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

def update_vertex(currentNode, edge, neighbour, openList, target):
    if line_of_sight(currentNode.previous, neighbour):
        # If there is line-of-sight between parent(s) and neighbour
        # then ignore s and use the path from parent(s) to neighbour
        
        # Have to redefine the distance
        parent_dist = currentNode.previous.distance2d(neighbour)
        if currentNode.previous.g + parent_dist < neighbour.g:
            neighbour.g = currentNode.previous.g + parent_dist
            neighbour.previous = currentNode.previous
            if neighbour not in openList:
                neighbour.calc_h(target)
            neighbour.f = neighbour.g + neighbour.h
            if neighbour not in openList:
                openList.append(neighbour)
    else:
        # If the length of the path from start to s and from s to 
        # neighbour is shorter than the shortest currently known distance
        # from start to neighbour, then update node with the new distance
        if currentNode.g + edge.weight < neighbour.g:
            neighbour.previous = currentNode
            neighbour.g  = currentNode.g + edge.weight
            if neighbour not in openList:
                neighbour.calc_h(target)
            neighbour.f = neighbour.g + neighbour.h
            if neighbour not in openList:
                openList.append(neighbour)

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
    g = Graph()

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