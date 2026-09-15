import plotly.graph_objects as go

from dash import Dash, html, dcc, Input, Output, State

from heaxapod_model.point import Point

DEFAULT_CAMERA = dict(eye=dict(x=1.25, y=1.25, z=1.25))

app = Dash(__name__)
app.layout = html.Div(
    [
        html.Div(
            [
                dcc.Store(id="camera-store", data=DEFAULT_CAMERA),
                dcc.Store(id="angle-store", data=0),
                dcc.Interval(id="tick", interval=50, n_intervals=0),
                html.Div(
                    [
                        html.Label("Угол поворота Coxa (град)"),
                        dcc.Slider(id="coxa", min=-90, max=90, step=1, value=0, marks={-90: "-90", 0: "0", 90: "90"}, updatemode="drag"),
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


@app.callback(
    Output("model-graph", "figure"),
    Input("angle-store", "data"),
    State("camera-store", "data"),
)
def update_graph(coxa_value, camera):
    origin = Point(0, 0, 0, "Origin")
    tip = Point(50, 0, 0, "CoxaTip")

    rotated_tip = tip.rotxyz(0, 0, coxa_value)

    fig = go.Figure()
    fig.add_trace(go.Scatter3d(
        x=[0, rotated_tip.x], y=[0, rotated_tip.y], z=[0, rotated_tip.z],
        mode="lines+markers"
    ))

    fig.add_trace(go.Scatter3d(x=[-100, 100], y=[0, 0], z=[0, 0], mode="lines", line=dict(color="red", width=2), showlegend=False))
    fig.add_trace(go.Scatter3d(x=[0, 0], y=[-100, 100], z=[0, 0], mode="lines", line=dict(color="green", width=2), showlegend=False))
    fig.add_trace(go.Scatter3d(x=[0, 0], y=[0, 0], z=[-100, 100], mode="lines", line=dict(color="blue", width=2), showlegend=False))

    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False, range=[-100, 100], dtick=2, title="X"),
            yaxis=dict(visible=False, range=[-100, 100], dtick=2, title="Y"),
            zaxis=dict(showticklabels=False, title="", range=[-100, 100], dtick=2),
            bgcolor="rgba(0,0,0,0)",
            camera=camera or DEFAULT_CAMERA,
        ),
        uirevision="constant",
        margin=dict(l=0, r=0, t=0, b=0),
    )
    return fig

if __name__ == "__main__":
    app.run(debug=True)