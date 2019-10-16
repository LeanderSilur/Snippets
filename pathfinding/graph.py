from Vector import Vector


class Vertex(object):
    def __init__(self, position, id=0):
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
                edge.right = self.edges[(i-1) % len(self.edges)]
    
    def calc_h(self, target):
        self.h = ((target.position[0] - self.position[0])**2
                + (target.position[1] - self.position[1])**2
                + (target.position[2] - self.position[2])**2)**0.5
                 
    def distance2d2(self, other):
        return ((other.position[0] - self.position[0])**2
              + (other.position[1] - self.position[1])**2)
                 
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
        
        t = cross(sub(start.position, self.origin.position), s) / rxs
        
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
            cost = (frm - to).length()
        
        angle1 = (to - frm).angle2d()
        angle2 = (frm - to).angle2d()

        edge_frm = frm.add_neighbor(to, cost, angle1, face_l, face_r)
        edge_to  = to.add_neighbor(frm, cost, angle2, face_r, face_l)
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