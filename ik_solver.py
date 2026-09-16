from point import Point
from math import atan2, sqrt, acos, degrees, pi

def solve_ik(leg: "Leg", target : Point):
    dx = target.x - leg.body.x
    dy = target.y - leg.body.y
    dz = target.z - leg.body.z
    alpha = atan2(dy, dx)

    L = sqrt(dx**2 + dy**2)
    r = L - leg.coxa_len
    d = sqrt(r**2 + dz**2)

    f = leg.femur_len
    t = leg.tibia_len
    ft_cos = (f**2 + t**2 - d**2) / (2 * f * t)
    gamma = pi - acos(ft_cos)

    phi1 = atan2(-dz, r)
    phi2 = acos((f**2 + d**2 - t**2) / (2 * f * d))
    beta = phi1 - phi2

    return degrees(alpha), degrees(beta), degrees(gamma)