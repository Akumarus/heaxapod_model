from point import Point

class Body:
    VERTEX_NAMES = (
        "right-front",
        "right-middle",
        "rigth-back",
        "left-back",
        "left-middle",
        "left-front",
    )
    AXIS = (45, 0, -45, 180 + 45, 180, 180 - 45)

    def __init__(self, f, m, s):
        self.f = f
        self.m = m
        self.s = s
        self.cog = Point(0, 0, 0, "center-of-gravity")
        self.head = Point(0, s, 0, "head")
        self.points = [
            Point( f,  s, 0, self.VERTEX_NAMES[0]),
            Point( m,  0, 0, self.VERTEX_NAMES[1]),
            Point( f, -s, 0, self.VERTEX_NAMES[2]),
            Point(-f, -s, 0, self.VERTEX_NAMES[5]),
            Point(-m,  0, 0, self.VERTEX_NAMES[4]),
            Point(-f,  s, 0, self.VERTEX_NAMES[3]),
        ]

# def add_body(body):
#     xs = [p.x for p in body.points]
#     ys = [p.y for p in body.points]
#     zs = [p.z for p in body.points]

#     print(xs)
#     print(ys)
#     print(zs)

# body = Body(10, 10, 10)
# add_body(body)