#from Vector import Vector, Line, Triangle

class Vertex(object):
    def __init__(self, position, id=0):
        assert isinstance(position, Vector)
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
            edge.left = self.edges[(i+1)%len(self.edges)]
            edge.right = self.edges[(i-1) % len(self.edges)]
                 
    def distance2d(self, other):
        raise Exception("why do i need this")
        return (other.position - self.position).length2d()
                 
    def distance3d(self, other):
        return (other.position - self.position).length()
        
    def __str__(self):
        return str(self.id).zfill(2)# + ": " + (str(self.g) if self.g != sys.maxsize else "")
    
    def __lt__(self, other):
        return self.position < other.position

class Edge(object):
    def __init__(self, origin, other, weight, angle, face_l, face_r):
        assert isinstance(origin, Vector) and isinstance(other, Vector)
        self.origin = origin
        self.other = other
        self.weight = weight
        self.angle = angle
        self._face_l = face_l
        self._face_r = face_r
        self.index = 0
        self.inv = None
        self.left = None
        self.right = None
    
    def has_face_l(self):
        return self.face_l

    def has_face_r(self):
        return self.face_r
    
    def __str__(self):
        return "[" + str(self.origin.id) + "->"+str(self.other.id)+"]"
    
    def intersect_2d(self, start, target):
        p = self.origin.position
        r = self.other.position - self.origin.position
        q = start.position
        s = target.position - start.position
        
        rxs = r.cross2d(s)
        if abs(rxs) < 0.000000001:
            raise Exception("lines are collinear.", start.id, target.id, self.origin.id, self.other.id)
        
        t = (start.position- self.origin.position).cross2d(s) / rxs
        pos = self.origin.position + (r * t)
        
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

    def insert_point(self, pt):
        projected_points = []
        for v in self.vert_list:
            if equals(v.position, pt):
                return v
            
            if v.position.x <= pt.x:
                for edge in v.edges:
                    if edge.other.position.x > pt.x and edge.face_l:
                        triangle = Triangle(v.position, edge.other.position, edge.left.other.position)
                        projected = triangle.closest_point(pt)
                        distance = (pt - projected).length2()
                        projected_points.append([projected, edge, distance])

        if len(projected_points) == 0:
            return None
        proj, edge, dist = min(projected_points, key=lambda a: a[1])
        v1, v2, v3 = edge.origin, edge.other, edge.inv.right.other
        
        # insert vertex
        center_vertex = self.add_vertex(proj)
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