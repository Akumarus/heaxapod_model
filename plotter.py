
class HexapodPlotter:
    def __init__(self):
        pass

    @staticmethod
    def draw_hexapod(fig, hexapod):
        i = 1

import numpy as np
from point import Point

def rotation_to_align(v_from: np.ndarray, v_to: np.ndarray) -> np.ndarray:
    """
    Матрица поворота, совмещающая вектор v_from с вектором v_to (формула Родригеса).
    """
    v_from = v_from / np.linalg.norm(v_from)
    v_to = v_to / np.linalg.norm(v_to)

    axis = np.cross(v_from, v_to)
    axis_len = np.linalg.norm(axis)
    cos_angle = np.dot(v_from, v_to)

    if axis_len < 1e-8:
        if cos_angle > 0:
            return np.eye(3)          # векторы уже совпадают
        return -np.eye(3)             # векторы противоположны (редкий случай)

    axis = axis / axis_len
    angle = np.arccos(np.clip(cos_angle, -1, 1))

    K = np.array([
        [0, -axis[2], axis[1]],
        [axis[2], 0, -axis[0]],
        [-axis[1], axis[0], 0],
    ])
    R = np.eye(3) + np.sin(angle) * K + (1 - cos_angle) * (K @ K)
    return R


def find_ground_contacts(hexapod, n_points=3):
    """
    Для каждой ноги находим самую низкую (по Z) точку среди coxa/femur/tibia.
    Возвращаем n_points самых низких точек среди ВСЕХ ног — они и образуют опорную плоскость.
    """
    candidates = []
    for name, leg in hexapod.legs.items():
        lowest = min([leg.coxa, leg.femur, leg.tibia], key=lambda p: p.z)
        candidates.append((name, lowest))

    candidates.sort(key=lambda pair: pair[1].z)
    return candidates[:n_points]


def plane_normal(p1: Point, p2: Point, p3: Point) -> np.ndarray:
    v1 = np.array([p2.x - p1.x, p2.y - p1.y, p2.z - p1.z])
    v2 = np.array([p3.x - p1.x, p3.y - p1.y, p3.z - p1.z])
    normal = np.cross(v1, v2)
    norm_len = np.linalg.norm(normal)
    if norm_len < 1e-8:
        return np.array([0.0, 0.0, 1.0])  # точки на одной линии — защита от деления на 0
    normal = normal / norm_len
    if normal[2] < 0:
        normal = -normal
    return normal


def apply_rigid_transform(hexapod, R: np.ndarray, dz: float, pivot: np.ndarray):
    """
    Поворачивает ВСЕ точки гексапода (тело + ноги) вокруг pivot через R,
    затем сдвигает по Z на dz.
    """
    def transform_point(p: Point):
        local = np.array([p.x, p.y, p.z]) - pivot
        rotated = R @ local
        world = rotated + pivot
        p.x, p.y, p.z = world[0], world[1], world[2] + dz

    for leg in hexapod.legs.values():
        transform_point(leg.body)
        transform_point(leg.coxa)
        transform_point(leg.femur)
        transform_point(leg.tibia)

    transform_point(hexapod.body.cog)
    transform_point(hexapod.body.head)
    for p in hexapod.body.points:
        transform_point(p)


def lay_hexapod_on_ground(hexapod, ground_z=0.0, n_contact_points=3):
    """
    Главная функция: после того как FK-позы всех ног уже посчитаны (hexapod.update_pose(...)),
    находит опорную плоскость и разворачивает весь гексапод так,
    чтобы эта плоскость легла на ground_z.
    """
    contacts = find_ground_contacts(hexapod, n_points=n_contact_points)
    p1, p2, p3 = contacts[0][1], contacts[1][1], contacts[2][1]

    normal = plane_normal(p1, p2, p3)
    R = rotation_to_align(normal, np.array([0.0, 0.0, 1.0]))

    pivot = np.array([hexapod.body.cog.x, hexapod.body.cog.y, hexapod.body.cog.z])

    # пробный поворот, чтобы узнать, на сколько сдвинуть по Z
    apply_rigid_transform(hexapod, R, dz=0.0, pivot=pivot)

    lowest_z = min(
        min(leg.coxa.z, leg.femur.z, leg.tibia.z)
        for leg in hexapod.legs.values()
    )
    dz = ground_z - lowest_z

    # сдвигаем всё по Z на нужную величину (поворот уже применён, R теперь единичный)
    apply_rigid_transform(hexapod, np.eye(3), dz=dz, pivot=pivot)

    return contacts  # пригодится для отладки / отрисовки опорных точек