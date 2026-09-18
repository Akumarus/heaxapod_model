import numpy as np
from point import Point

def plane_normal(p1, p2, p3):
    v1 = np.array([p2.x - p1.x, p2.y - p1.y, p2.z - p1.z])
    v2 = np.array([p3.x - p1.x, p3.y - p1.y, p3.z - p1.z])
    normal = np.cross(v1, v2)
    normal = normal / np.linalg.norm(normal)
    if normal[2] < 0:
        normal = -normal
    return normal




p1 = Point(0, 4, 0)
p2 = Point(5, 4, 0)
p3 = Point(0, 4, 0)
print(plane_normal(p1, p2, p3))