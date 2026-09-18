import plotly.graph_objects as go
import numpy as np
from dash import Dash, html, dcc, Input, Output, State

from hexapod import Hexapod
from point import Point
from body import Body
from leg import Leg

DEFAULT_CAMERA = dict(eye=dict(x=1.25, y=1.25, z=1.25))

app = Dash(__name__)
app.layout = html.Div(
    [
        html.Div(
            [
                dcc.Store(id="camera-store", data=DEFAULT_CAMERA),
                dcc.Store(id="angle-store", data=0),
                dcc.Interval(id="tick", interval=50, n_intervals=0, disabled=True),
                html.Div(
                    [
                        html.Label("Размеры корпуса"),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Label("F", style={"fontSize": "12px"}),
                                        dcc.Input(id="body-f", type="number", value=20, min=0, step=1, style={"width": "40px"}),
                                    ],
                                    style={"marginRight": "10px"},
                                ),
                                html.Div(
                                    [
                                        html.Label("M", style={"fontSize": "12px"}),
                                        dcc.Input(id="body-m", type="number", value=40, min=0, step=1, style={"width": "40px"}),
                                    ],
                                    style={"marginRight": "10px"},
                                ),
                                html.Div(
                                    [
                                        html.Label("S", style={"fontSize": "12px"}),
                                        dcc.Input(id="body-s", type="number", value=40, min=0, step=1, style={"width": "40px"}),
                                    ],
                                    style={"marginRight": "10px"},
                                ),
                                html.Div(
                                    [
                                        html.Label("Coxa", style={"fontSize": "12px"}),
                                        dcc.Input(id="coxa-len", type="number", value=20, min=0, step=1, style={"width": "40px"}),
                                    ],
                                    style={"marginRight": "10px"},
                                ),
                                html.Div(
                                    [
                                        html.Label("Femur", style={"fontSize": "12px"}),
                                        dcc.Input(id="femur-len", type="number", value=20, min=0, step=1, style={"width": "40px"}),
                                    ],
                                    style={"marginRight": "10px"},
                                ),
                                html.Div(
                                    [
                                        html.Label("Tibia", style={"fontSize": "12px"}),
                                        dcc.Input(id="tibia-len", type="number", value=20, min=0, step=1, style={"width": "40px"}),
                                    ],
                                ),
                            ],
                            style={"display": "flex", "marginBottom": "20px"},
                        ),
                        html.Label("Угол поворота Coxa (град)"),
                        dcc.Slider(id="coxa", min=-90, max=90, step=1, value=0, marks={-90: "-90", 0: "0", 90: "90"}, updatemode="drag"),
                        dcc.Slider(id="femur", min=-90, max=90, step=1, value=-45, marks={-90: "-90", 0: "0", 90: "90"}, updatemode="drag"),
                        dcc.Slider(id="tibia", min=-90, max=90, step=1, value=90, marks={-90: "-90", 0: "0", 90: "90"}, updatemode="drag"),
                        html.Label("Частота вращения (град/сек)"),
                        dcc.Slider(id="speed", min=-360, max=360, step=10, value=90, marks={-360: "-360", 0: "0", 360: "360"}, updatemode="drag"),
                        dcc.Checklist(id="spin", options=[{"label": "Вращать", "value": "Вкл"}], value=[])
                    ],
                    style={"width": "320px", "padding": "20px"},
                ),
                dcc.Graph(id="model-graph", 
                          style={"flex": "1", "height": "80vh"}),
            ],
            style={"display": "flex"},
        ),
    ],
    style={"font-family": "sans-serif", "padding": "10px"},
)

@app.callback(
    Output("camera-store", "data"),
    Input("model-graph", "relayoutData"),
    State("camera-store", "data"),
)
def save_camera(relayout_data, current_camera):
    if relayout_data and "scene.camera" in relayout_data:
        return relayout_data["scene.camera"]
    return current_camera

@app.callback(
    Output("tick", "disabled"),
    Input("spin", "value"),
)
def toggle_interval(spin):
    return "Вкл" not in spin

@app.callback(
    Output("angle-store", "data"),
    Input("tick", "n_intervals"),
    Input("coxa", "value"),
    State("spin", "value"),
    State("speed", "value"),
    State("angle-store", "data"),
)
def advance_angle(n, coxa_value, spin, speed, angle):
    from dash import ctx
    if ctx.triggered_id == "coxa":
        return coxa_value
    if "Вкл" not in spin:
        return angle
    dt = 0.05
    return (angle + speed * dt) % 360

def add_line(fig, p0, p1, color="blue"):
    x0, y0, z0 = p0.vec
    x1, y1, z1 = p1.vec
    fig.add_trace(go.Scatter3d(
        x=[x0, x1], y=[y0, y1], z=[z0, z1],
        mode="lines+markers",
        line=dict(color=color, width=4),
        showlegend=False,
    ))

def add_body(fig, body):
    points = body.points + [body.points[0]]
    xs = [p.x for p in points]
    ys = [p.y for p in points]
    zs = [p.z for p in points]

    fig.add_trace(go.Scatter3d(
        x=xs, y=ys, z=zs,
        mode="lines+markers",
        line=dict(color="red", width=4),
        showlegend=False,
    ))

    fig.add_trace(go.Scatter3d(
        x=[body.cog.x, body.head.x], 
        y=[body.cog.y, body.head.y],
        z=[body.cog.z, body.head.z],
        mode="markers",
        line=dict(color="red", width=4),
        showlegend=False
    ))

    return fig

def add_legs(fig, legs):
    points = legs.points
    xs = [p.x for p in points]
    ys = [p.y for p in points]
    zs = [p.z for p in points]

    fig.add_trace(go.Scatter3d(
        x=xs, y=ys, z=zs,
        mode="lines+markers",
        line=dict(color="red", width=4),
        showlegend=False,
    ))

    return fig

def add_ground(fig, size=150, z=0, color="lightgray"):
    xs = np.linspace(-size, size, 2)
    ys = np.linspace(-size, size, 2)
    xx, yy = np.meshgrid(xs, xs)
    zz = np.full_like(xx, z)

    fig.add_trace(go.Surface(
        x=xx, y=yy, z=zz,
        opacity=0.3,
        colorscale=[[0, color], [1, color]],
        showscale=False,
        hoverinfo="skip",
    ))

    return fig

def add_polygon(fig, points, color="green", opacity=0.4, outline_color="darkgreen"):
    """Строит закрашенный многоугольник по упорядоченным вершинам points."""
    n = len(points)
    if n < 3:
        return fig

    xs = [p.x for p in points]
    ys = [p.y for p in points]
    zs = [p.z for p in points]

    # веерная триангуляция от вершины 0: (0,1,2), (0,2,3), (0,3,4), ...
    i_idx = [0] * (n - 2)
    j_idx = list(range(1, n - 1))
    k_idx = list(range(2, n))

    fig.add_trace(go.Mesh3d(
        x=xs, y=ys, z=zs,
        i=i_idx, j=j_idx, k=k_idx,
        color=color,
        opacity=opacity,
        flatshading=True,
        hoverinfo="skip",
        showlegend=False,
    ))

    # контур многоугольника (замыкаем на первую точку)
    xs_line = xs + [xs[0]]
    ys_line = ys + [ys[0]]
    zs_line = zs + [zs[0]]

    fig.add_trace(go.Scatter3d(
        x=xs_line, y=ys_line, z=zs_line,
        mode="lines",
        line=dict(color=outline_color, width=5),
        showlegend=False,
        hoverinfo="skip",
    ))

    return fig

@app.callback(
    Output("model-graph", "figure"),
    Input("angle-store", "data"),
    Input("femur", "value"),
    Input("tibia", "value"),
    Input("body-f", "value"),
    Input("body-m", "value"),
    Input("body-s", "value"),
    Input("coxa-len", "value"),
    Input("femur-len", "value"),
    Input("tibia-len", "value"),
    State("camera-store", "data"),
)
def update_graph(alpha, beta, gamma, f, m, s, coxa_len, femur_len, tibia_len, camera):
    hexapod = Hexapod(f, m, s, coxa_len, femur_len, tibia_len)
    hexapod.update_pose(alpha, beta, gamma)
    # contacts = hexapod.find_ground_contact()

    # print(contacts)
    # print(alpha, beta, gamma)
    
    fig = go.Figure()
    add_ground(fig)
    # add_polygon(fig, contacts, color="green", opacity=0.4)
    add_body(fig, body=hexapod.body)
    add_legs(fig, legs=hexapod.legs[0])
    add_legs(fig, legs=hexapod.legs[1])
    add_legs(fig, legs=hexapod.legs[2])
    add_legs(fig, legs=hexapod.legs[3])
    add_legs(fig, legs=hexapod.legs[4])
    add_legs(fig, legs=hexapod.legs[5])

    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False, range=[-100, 100], dtick=2, title="X"),
            yaxis=dict(visible=False, range=[-100, 100], dtick=2, title="Y"),
            zaxis=dict(visible=False, range=[-100, 100], dtick=2),
            bgcolor="rgba(0,0,0,0)",
            camera=camera or DEFAULT_CAMERA,
            aspectmode="cube",
        ),
        uirevision="constant",
        margin=dict(l=0, r=0, t=0, b=0),
    )
    return fig



if __name__ == "__main__":
    app.run(debug=True)