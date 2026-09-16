
import numpy as np
from ik_solver import solve_ik
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

    def set_target(self, target : Point):
        alpha, beta, gamma = solve_ik(self, target)
        self.pose(alpha, beta, gamma)
        return alpha, beta, gamma

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

leg = Leg(25, 50, 75)
leg.pose(30, -20, 50)
target = leg.tibia
leg.pose(0, 0, 0)
alpha, beta, gamma = leg.set_target(target)
print(f"Ожидали: alpha=30, beta=-20, gamma=50")
print(f"Получили: alpha={alpha:.2f}, beta={beta:.2f}, gamma={gamma:.2f}")
