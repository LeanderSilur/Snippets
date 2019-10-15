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
    
def closest_node(g, name):
    node, dist = g[0], sys.maxsize
    for v in g:
        ndist = (mathutils.Vector(v.position)-bpy.data.objects[name].location).length
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

def get_intersection(edge, start, target):
    p = edge.origin.position
    r = sub(edge.other.position, edge.origin.position)
    q = start.position
    s = sub(target.position, start.position)
    
    rxs = cross(r, s)
    if rxs == 0:
        raise Exception("lines are collinear.")
    
    t = cross(sub(start.position, edge.origin.position), s) / rxs;
    
    pos = add(edge.origin.position, mult(r, t))
    
    print(t)
    
    return EdgeIntersection(edge, pos)













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
        
    def __str__(self):
        return str(self.id)# + ": " + (str(self.g) if self.g != sys.maxsize else "")
    
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
        if left: return self.face_l
        return self.face_r
    
    def double_sided(self):
        return self.face_l and self.face_r
    
    def __str__(self):
        return "[" + str(self.origin.id) + "->"+str(self.other.id)+"]"
    
    def intersect_2d(a, b):
        x1, y1, _ = a
        x2, y2, _ = b
        x3, y3, _ = self.origin.position
        x4, y4, _ = self.other.position
        
        # determinant
        if abs((x1-x2)(y3-y4)-(y1-y2)(x3-x4)) < 0.0000001:
            return None
        # https://stackoverflow.com/questions/563198/how-do-you-detect-where-two-line-segments-intersect
        return None

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

    def add_edge(self, frm_id, to_id, angle, face_l, face_r, cost = -1):
        assert frm_id >= 0 and frm_id < len(self.vert_list) and to_id >= 0 and to_id < len(self.vert_list)
        
        frm = self.vert_list[frm_id]
        to = self.vert_list[to_id]
        
        if (cost < 0):
            cost = (  (frm.position[0]-to.position[0])**2
                    + (frm.position[1]-to.position[1])**2
                    + (frm.position[2]-to.position[2])**2  ) ** 0.5
        
        rev_angle = angle - math.pi if angle >= 0 else angle + math.pi

        edge_frm = frm.add_neighbor(to, cost, angle, face_l, face_r)
        edge_to  = to.add_neighbor(frm, cost, rev_angle, face_r, face_l)
        edge_frm.inv = edge_to
        edge_to.inv = edge_frm

    def freeze(self):
        for i in range(len(self.vert_list)):
            self.vert_list[i].sort_edges()

def reconstruct_path(v):
    path = [v]
    while v.previous != v:
        path.append(v.previous)
        v = v.previous
    return path[::-1]
        
        
def theta_star(start, target):
    openList = [start]
    closedList = []
    
    start.g = 0
    start.calc_h(target)
    start.f = start.g + start.h
    start.previous = start
    
    while len(openList):
        openList.sort(key=lambda v: v.f)
        currentNode = openList.pop(0)
        
        if currentNode == target:
            return reconstruct_path(target)
            
        closedList.append(currentNode)
        for edge in currentNode.edges:
            v = edge.other
            if v not in closedList:
                if v not in openList:
                    v.g = sys.maxsize
                    v.previous = None
                
                print(currentNode, " and", v, ' => ', end='')
                update_vertex(currentNode, edge, v, openList, target)
                print(v, v.previous, "{:.2f}".format(v.g), "{:.2f}".format(v.f))
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
        angle = math.atan2(v2.co[1] - v1.co[1], v2.co[0] - v1.co[0])
        face_l, face_r = False, False
        for face in e.link_faces:
            v3 = [v for v in face.verts if v.index not in [v1.index, v2.index]][0]
            y_rotated = (v3.co[0] - v1.co[0]) * math.sin(-angle) + (v3.co[1] - v1.co[1]) * math.cos(-angle)
            if y_rotated == 0:
                raise Exception("Collinearity.", v3.index, v1.index, v2.index)
            if (y_rotated > 0): face_l = True
            elif (y_rotated < 0): face_r = True
        
        g.add_edge(v1.index, v2.index, angle, face_l, face_r)
    
    g.freeze()
    return g
    

# Create graph once.
    
def update(context):
    g = create_graph()
    print("________")
    
    # get start and target
    start = closest_node(g, 'start')
    target = closest_node(g, 'target')

    # calculate path
    path = theta_star(start, target)
    
    vis_path(path)


for h in bpy.app.handlers.depsgraph_update_post:
    bpy.app.handlers.depsgraph_update_post.remove(h)
bpy.app.handlers.depsgraph_update_post.append(update)

update(bpy.context)