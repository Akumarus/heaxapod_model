from body import Body
from leg import Leg


class Hexapod:
    LEGS_NUM = 6

    def __init__(self, f, m, s, coxa, femur, tibia):
        self.body = Body(f=f, m=m, s=s)
        self.legs = [Leg(self.body.points[i], coxa_len=coxa, femur_len=femur, tibia_len=tibia) for i in range(self.LEGS_NUM)]

    def update_pose(self, alpha, beta, gamma):
        for i in range(self.LEGS_NUM):
            self.legs[i].pose(alpha=alpha, beta=beta, gamma=gamma)
        
    def __str__(self):
        return "Hexapod:\n" + "\n".join(str(leg) for leg in self.legs)

