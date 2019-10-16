import bpy
import sys
import bmesh
import mathutils
import math
import time

def vis_path(bm, path, height = 0.01):
    verts = []
    for v in path:
        vert = bm.verts.new(v.position)
        verts.append(vert)
        
    bm.verts.ensure_lookup_table()
    edges = []
    for i in range(len(verts)):
        if i > 0:
            edge = bm.edges.new((verts[i], verts[i-1]))
            edges.append(edge)
    
    verts = [o for o in bmesh.ops.extrude_edge_only(bm, edges=edges)['geom']
                if isinstance(o, bmesh.types.BMVert)]
    for v in verts:
        v.co.z += height
    
def closest_node(g, name):
    node, dist = g[0], sys.maxsize
    for v in g:
        ndist = (mathutils.Vector(v.position)-bpy.data.objects[name].location).length
        if (ndist < dist):
            dist = ndist
            node = v
    return node














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
        
    def __str__(self):
        return str(self.id) + "V"# + (str(self.g) if self.g != sys.maxsize else "")
    
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
            
    def get_path(v):
        path = []
        while v:
            path.append(v)
            v = v.previous
        return path


def a_star(start, target):
    openList = [start]
    closedList = []
    
    start.g = 0
    start.previous = None
    
    while len(openList):
        openList.sort(key=lambda v: v.f)
        currentNode = openList.pop(0)
        
        if currentNode == target:
            # Reached target. Create path.
            path = []
            v = target
            while True:
                path.append(v)
                prev = v.previous
                if prev == None:
                    # Reached first segment.
                    return path[::-1]
                prev.edge = [e for e in prev.edges if e.other == v][0]
                v = prev
            
        
        closedList.append(currentNode)
        for edge in currentNode.edges:
            v = edge.other
            if v not in closedList:
                walked_distance = currentNode.g + edge.weight
                
                if v not in openList:
                    openList.append(v)
                    v.calc_h(target)
                    v.g = sys.maxsize
                    
                if walked_distance < v.g:
                    v.g = walked_distance
                    v.f = v.g + v.h
                    v.previous = currentNode
    
    # Failed to reach target.
    return None

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
    
    
    return EdgeIntersection(edge, pos)


# returns
# 0     ... continue (crossing edge)
# 1     ... reached target
# 2     ... hit edge
def get_edge_collision(edge, start, target):
    if not edge.right:
        return 2, None
    
    if edge.right.other == target:
        return 1, None
    
    if is_left(start.position, target.position, edge.right.other.position):
        return 0, edge.right
    else: # is_right
        return 0, edge.right.inv.right

def get_vertex_collision(start, target):
    for edge in start.edges:
        if edge.left:
            if in_angle(start.position, edge.other.position, edge.left.other.position, target.position):
                return edge.inv.right
    return None

# return [bool] if direct path is possible
def get_path(edge, edge_path, start, target):
    result, edge = get_edge_collision(edge, start, target)
    while True:
        if result == 1: # reached target
            return True
        elif result == 2: # hit edge
            return False
        else:
            edge_path.append(edge)
        result, edge = get_edge_collision(edge, start, target)

def improve_path(path):
    start = path[0]

    edges = [get_vertex_collision(start, path[i]) for i in range(2, len(path))]
    
    edge_path = None
    prev_edge_path = None
    for i in range(len(edges)-1, -1, -1):
        edge = edges[i]
        if edge:
            target = path[i+2]
            next_edge_path = [edge]
            result = get_path(edge, next_edge_path, start, target)
            if (result):
                farthest = i
                # break here, if you don't want to get fancy
                edge_path = next_edge_path
                break
                if i < len(edges) - 1:
                    print("not very far")
                    # check if
                    farthest = i + 1
                    edge_path = prev_edge_path
                    if is_left(path[0].position, path[-1].position, path[farthest].position):
                        edge_path[-1] = edge_path[-1].other
                    else:
                        edge_path[-1] = edge_path[-1].origin
                    print(len(edge_path), len(next_edge_path))
                    break
                    
                edge_path = next_edge_path
                break
            else:
                prev_edge_path = next_edge_path
                print(i, "/", len(edges), "-> failed")
    
    if edge_path:
        target = path[farthest+2]
        
        for i in range(farthest+1, 0, -1):
            del path[i]
        
        for edge in edge_path[::-1]:
            intersect = get_intersection(edge, start, target)
            path.insert(1, intersect)
    

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
    path = a_star(start, target)
    
    bm = bmesh.new()
    vis_path(bm, path)
    
    improve_path(path)
    
    vis_path(bm, path, height = 0.1)
    
    ob = bpy.data.objects['path']
    bm.to_mesh(ob.data)
    bm.free()


for h in bpy.app.handlers.depsgraph_update_post:
    bpy.app.handlers.depsgraph_update_post.remove(h)
bpy.app.handlers.depsgraph_update_post.append(update)

update(bpy.context)