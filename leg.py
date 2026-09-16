
import numpy as np
from point import Point, step, roty, rotz


class Leg:
    def __init__(self, coxa_len, femur_len, tibia_len):
        self.coxa_len = coxa_len
        self.femur_len = femur_len
        self.tibia_len = tibia_len

        self.alpha = 0
        self.beta = 0
        self.gamma = 0

        self.body = Point(0, 0, 0, "body")
        self.coxa = self.femur = self.tibia = None
        self.pose(self.alpha, self.beta, self.gamma)

    def pose(self, alpha, beta, gamma):
        self.alpha, self.beta, self.gamma = alpha, beta, gamma

        R = np.eye(3)
        R = R @ rotz(alpha)
        self.coxa = step(self.body, self.coxa_len, R)

        R = R @ roty(beta)
        self.femur = step(self.coxa, self.femur_len, R)

        R = R @ roty(gamma)
        self.tibia = step(self.femur, self.tibia_len, R)

    def __str__(self):
        return {"Leg Points \n {self.coxa}"}

    def body(self) -> Point:
        return self.body
    
    def coxa(self) -> Point:
        return self.coxa

    def femur(self) -> Point:
        return self.femur

    def tibia(self) -> Point:
        return self.tibia

# leg = Leg(1, 1, 1)
# print(leg.coxa)
# print(leg.femur)
# print(leg.tibia)
# leg.pose(90, 0, 0)
# print(leg.coxa)
# print(leg.femur)
# print(leg.tibia)
