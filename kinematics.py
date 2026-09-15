"""
Forward kinematics for a single 3-DOF hexapod leg.

Leg chain: body -> coxa -> femur -> tibia -> foot tip

All computations use only numpy (no external math/3d library),
same philosophy as mithi/hexapod-robot-simulator.
"""
import numpy as np


def leg_points(coxa_deg, femur_deg, tibia_deg, coxa_len, femur_len, tibia_len):
    """
    Returns the 4 joint positions of one leg as an (4, 3) numpy array:
    [body_attach, coxa_end, femur_end, tibia_end (foot tip)]

    coxa_deg  : yaw angle of the coxa joint (rotation around Z, horizontal plane)
    femur_deg : elevation angle of the femur relative to horizontal
    tibia_deg : elevation angle of the tibia relative to the femur link
    """
    coxa = np.radians(coxa_deg)
    femur = np.radians(femur_deg)
    tibia = np.radians(tibia_deg)

    p0 = np.array([0.0, 0.0, 0.0])

    # Coxa: horizontal rotation only, stays at z = 0
    p1 = p0 + coxa_len * np.array([np.cos(coxa), np.sin(coxa), 0.0])

    # Femur: elevates from horizontal, direction set by the coxa yaw
    femur_dir = np.array([
        np.cos(femur) * np.cos(coxa),
        np.cos(femur) * np.sin(coxa),
        np.sin(femur),
    ])
    p2 = p1 + femur_len * femur_dir

    # Tibia: angle is relative to the femur link (serial chain, same vertical plane)
    total = femur + tibia
    tibia_dir = np.array([
        np.cos(total) * np.cos(coxa),
        np.cos(total) * np.sin(coxa),
        np.sin(total),
    ])
    p3 = p2 + tibia_len * tibia_dir

    return np.array([p0, p1, p2, p3])