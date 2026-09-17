import plotly.graph_objects as go

from dash import Dash, html, dcc, Input, Output, State

from hexapod
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
                                        dcc.Input(id="body-f", type="number", value=30, min=0, step=1, style={"width": "40px"}),
                                    ],
                                    style={"marginRight": "10px"},
                                ),
                                html.Div(
                                    [
                                        html.Label("M", style={"fontSize": "12px"}),
                                        dcc.Input(id="body-m", type="number", value=50, min=0, step=1, style={"width": "40px"}),
                                    ],
                                    style={"marginRight": "10px"},
                                ),
                                html.Div(
                                    [
                                        html.Label("S", style={"fontSize": "12px"}),
                                        dcc.Input(id="body-s", type="number", value=50, min=0, step=1, style={"width": "40px"}),
                                    ],
                                    style={"marginRight": "10px"},
                                ),
                                html.Div(
                                    [
                                        html.Label("Coxa", style={"fontSize": "12px"}),
                                        dcc.Input(id="body-f", type="number", value=30, min=0, step=1, style={"width": "40px"}),
                                    ],
                                    style={"marginRight": "10px"},
                                ),
                                html.Div(
                                    [
                                        html.Label("Femur", style={"fontSize": "12px"}),
                                        dcc.Input(id="body-m", type="number", value=30, min=0, step=1, style={"width": "40px"}),
                                    ],
                                    style={"marginRight": "10px"},
                                ),
                                html.Div(
                                    [
                                        html.Label("Tibia", style={"fontSize": "12px"}),
                                        dcc.Input(id="body-s", type="number", value=30, min=0, step=1, style={"width": "40px"}),
                                    ],
                                ),
                            ],
                            style={"display": "flex", "marginBottom": "20px"},
                        ),
                        html.Label("Угол поворота Coxa (град)"),
                        dcc.Slider(id="coxa", min=-90, max=90, step=1, value=0, marks={-90: "-90", 0: "0", 90: "90"}, updatemode="drag"),
                        dcc.Slider(id="femur", min=-90, max=90, step=1, value=0, marks={-90: "-90", 0: "0", 90: "90"}, updatemode="drag"),
                        dcc.Slider(id="tibia", min=-90, max=90, step=1, value=0, marks={-90: "-90", 0: "0", 90: "90"}, updatemode="drag"),
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

@app.callback(
    Output("model-graph", "figure"),
    Input("angle-store", "data"),
    Input("femur", "value"),
    Input("tibia", "value"),
    Input("body-f", "value"),
    Input("body-m", "value"),
    Input("body-s", "value"),
    State("camera-store", "data"),
)
def update_graph(alpha, beta, gamma, f, m, s, camera):
    # body = Body(f, m, s)
    # leg1 = Leg(body.points[0], 20, 20, 20)
    # leg2 = Leg(body.points[1], 20, 20, 20)
    # leg3 = Leg(body.points[2], 20, 20, 20)
    # leg4 = Leg(body.points[3], -20, -20, -20)
    # leg5 = Leg(body.points[4], -20, -20, -20)
    # leg6 = Leg(body.points[5], -20, -20, -20)
    # print(alpha, beta, gamma)
    # leg1.pose(alpha, beta, gamma)
    # leg2.pose(alpha, beta, gamma)
    # leg3.pose(alpha, beta, gamma)
    # leg4.pose(alpha, beta, gamma)
    # leg5.pose(alpha, beta, gamma)
    # leg6.pose(alpha, beta, gamma)

    fig = go.Figure()
    # add_body(fig, body=body)
    # add_legs(fig, legs=leg1)
    # add_legs(fig, legs=leg2)
    # add_legs(fig, legs=leg3)
    # add_legs(fig, legs=leg4)
    # add_legs(fig, legs=leg5)
    # add_legs(fig, legs=leg6)

    # add_line(fig, leg1.body, leg1.coxa, color="blue")
    # add_line(fig, leg1.coxa, leg1.femur, color="blue")
    # add_line(fig, leg1.femur, leg1.tibia, color="blue")

    # fig.add_trace(go.Scatter3d(x=[-100, 100], y=[0, 0], z=[0, 0], mode="lines", line=dict(color="red", width=2), showlegend=False))
    # fig.add_trace(go.Scatter3d(x=[0, 0], y=[-100, 100], z=[0, 0], mode="lines", line=dict(color="green", width=2), showlegend=False))
    # fig.add_trace(go.Scatter3d(x=[0, 0], y=[0, 0], z=[-100, 100], mode="lines", line=dict(color="blue", width=2), showlegend=False))

    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False, range=[-100, 100], dtick=2, title="X"),
            yaxis=dict(visible=False, range=[-100, 100], dtick=2, title="Y"),
            zaxis=dict(showticklabels=False, title="", range=[-100, 100], dtick=2),
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