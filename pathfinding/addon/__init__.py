

bl_info = {
    "name" : "Pathfinding",
    "author" : "Leander",
    "description" : "",
    "blender" : (2, 80, 0),
    "version" : (0, 0, 1),
    "location" : "",
    "warning" : "",
    "category" : "Generic"
}

from . Vector import *
from . Graph import *

#from . iota_star import *

def register():
    return
    iota_star.register()

def unregister():
    return
    iota_star.unregister()
