from math import sin, cos, radians, degrees
import numpy as np


class Point:
    def __init__(self, x, y, z, name="Name"):
        self.x = x
        self.y = y
        self.z = z
        self.name = name

    def move_xyz(self, x, y, z):
        self.x += x
        self.y += y
        self.z += z

    @property
    def vec(self):
        return self.x, self.y, self.z

    def __repr__(self):
        s = f"Point(x={self.x:>+8.2f}, y={self.y:>+8.2f}, z={self.z:>+8.2f}, name={self.name})"
        return s
    
    def __str__(self):
        return repr(self)


def rotx(theta):
    c, s = return_sin_cos(theta)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])

def roty(theta):
    c, s = return_sin_cos(theta)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])

def rotz(theta):
    c, s = return_sin_cos(theta)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])

def rotxyz(a, b, c):
    rx = rotx(a)
    ry = roty(b)
    rz = rotz(c)
    rxy = np.matmul(rx, ry)
    rxyz = np.matmul(rxy, rz)
    # res = np.matmul(rxyz, np.array([x, y, z]))
    # return Point(res[0], res[1], res[2])

def return_sin_cos(theta):
    d = radians(theta)
    c = cos(d)
    s = sin(d)
    return c, s

def step(origin: Point, length: float, R: np.ndarray):
    x, y, z = R @ np.array([length, 0.0, 0.0])
    return Point(origin.x + x, origin.y + y, origin.z + z)