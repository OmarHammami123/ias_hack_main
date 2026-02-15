import argparse
import random
from datetime import datetime
from typing import Dict, List

import dash
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, Input, Output
import numpy as np
import plotly.graph_objects as go

# Simple pipe network definition
NODES = {
    "Compressor": (0, 2),
    "Manifold_A": (2, 2),
    "Manifold_B": (2, 1),
    "Zone_A1": (4, 2.5),
    "Zone_A2": (4, 1.5),
    "Zone_B1": (4, 1.0),
    "Zone_B2": (4, 0.0),
    "Return": (6, 1),
}

EDGES = [
    ("Compressor", "Manifold_A", "Pipe_A0"),
    ("Compressor", "Manifold_B", "Pipe_B0"),
    ("Manifold_A", "Zone_A1", "Pipe_A1"),
    ("Manifold_A", "Zone_A2", "Pipe_A2"),
    ("Manifold_B", "Zone_B1", "Pipe_B1"),
    ("Manifold_B", "Zone_B2", "Pipe_B2"),
    ("Zone_A1", "Return", "Pipe_R1"),
    ("Zone_B1", "Return", "Pipe_R2"),
]

VALVES = {"Pipe_A1", "Pipe_B1", "Pipe_R2"}

PIPE_CHOICES = [edge[2] for edge in EDGES]

app: Dash = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.CYBORG],
    title="Leak Network Dashboard",
)


def simulate_metrics(leak_pipe: str) -> Dict[str, float]:
    base_pressure = 120
    base_flow = 450
    leak_penalty = 0 if leak_pipe == "None" else 30
    return {
        "pressure": round(base_pressure - leak_penalty + random.uniform(-3, 3), 2),
        "flow": round(base_flow - leak_penalty * 2 + random.uniform(-10, 10), 2),
        "leak_score": 0.05 if leak_pipe == "None" else round(random.uniform(0.65, 0.95), 2),
        "timestamp": datetime.now().strftime("%H:%M:%S"),
    }


def build_network_figure(leak_pipe: str) -> go.Figure:
    fig = go.Figure()

    # Draw pipes
    for start, end, pipe_id in EDGES:
        xs = [NODES[start][0], NODES[end][0]]
        ys = [NODES[start][1], NODES[end][1]]
        color = "#ff4d4d" if pipe_id == leak_pipe else "#00e0ff"
        width = 6 if pipe_id == leak_pipe else 4
        fig.add_trace(
            go.Scatter(
                x=xs,
                y=ys,
                mode="lines",
                line=dict(color=color, width=width),
                hovertemplate=f"{pipe_id}<extra></extra>",
                name=pipe_id,
                showlegend=False,
            )
        )

    # Draw nodes
    fig.add_trace(
        go.Scatter(
            x=[p[0] for p in NODES.values()],
            y=[p[1] for p in NODES.values()],
            mode="markers+text",
            marker=dict(size=18, color="#1f2937", line=dict(color="#00e0ff", width=2)),
            text=[n for n in NODES.keys()],
            textposition="top center",
            hoverinfo="text",
            showlegend=False,
        )
    )

    # Draw valves
    valve_x = []
    valve_y = []
    for start, end, pipe_id in EDGES:
        if pipe_id in VALVES:
            valve_x.append((NODES[start][0] + NODES[end][0]) / 2)
            valve_y.append((NODES[start][1] + NODES[end][1]) / 2)
    fig.add_trace(
        go.Scatter(
            x=valve_x,
            y=valve_y,
            mode="markers",
            marker=dict(symbol="square", size=12, color="#fbbf24", line=dict(color="#111827", width=1)),
            hovertemplate="Valve<extra></extra>",
            showlegend=False,
        )
    )

    fig.update_layout(
        height=520,
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor="#0b1221",
        paper_bgcolor="#0b1221",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
    )
    return fig


def build_pressure_chart(leak_pipe: str) -> go.Figure:
    times = list(range(-9, 1))
    base = 120
    leak_drop = 0 if leak_pipe == "None" else 25
    noise = np.random.normal(0, 2, size=len(times))
    values = base - leak_drop + noise
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=times,
            y=values,
            mode="lines+markers",
            line=dict(color="#00e0ff"),
            fill="tozeroy",
            fillcolor="rgba(0,224,255,0.15)",
            name="Pressure (psi)",
        )
    )
    fig.update_layout(
        title="Pressure Trend (last 10 mins)",
        xaxis_title="Minutes",
        yaxis_title="PSI",
        plot_bgcolor="#0b1221",
        paper_bgcolor="#0b1221",
        font=dict(color="#e5e7eb"),
        height=300,
    )
    return fig


def build_spectrogram(leak_pipe: str) -> go.Figure:
    freqs = np.linspace(0, 8000, 64)
    times = np.linspace(0, 4, 40)
    t_grid, f_grid = np.meshgrid(times, freqs)
    base = np.sin(2 * np.pi * f_grid / 8000)
    leak_energy = 0 if leak_pipe == "None" else np.random.uniform(1.5, 2.5)
    power = np.abs(base + leak_energy * np.random.rand(*base.shape))

    fig = go.Figure(
        data=go.Heatmap(
            z=power,
            x=times,
            y=freqs,
            colorscale="Turbo",
            colorbar=dict(title="Energy"),
        )
    )
    fig.update_layout(
        title="Acoustic Spectrogram (mic feed)",
        xaxis_title="Time (s)",
        yaxis_title="Frequency (Hz)",
        height=320,
        plot_bgcolor="#0b1221",
        paper_bgcolor="#0b1221",
        font=dict(color="#e5e7eb"),
    )
    return fig


app.layout = dbc.Container(
    [
        html.H2("Industrial Leak Network", className="text-center my-3"),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Label("Select leak location"),
                        dcc.Dropdown(
                            options=[{"label": "No Leak", "value": "None"}]
                            + [{"label": p, "value": p} for p in PIPE_CHOICES],
                            value="None",
                            id="leak-pipe",
                            clearable=False,
                        ),
                        html.Div(id="kpi-cards", className="mt-3"),
                    ],
                    md=4,
                ),
                dbc.Col(dcc.Graph(id="network-graph"), md=8),
            ],
            align="center",
        ),
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="pressure-chart"), md=6),
                dbc.Col(dcc.Graph(id="spectrogram"), md=6),
            ]
        ),
        dcc.Interval(id="refresh-interval", interval=5000, n_intervals=0),
    ],
    fluid=True,
)


def render_kpis(metrics: Dict[str, float]) -> List[dbc.Card]:
    cards = [
        dbc.Card(
            [
                dbc.CardHeader("Pressure (psi)"),
                dbc.CardBody(html.H4(f"{metrics['pressure']}")),
            ],
            color="dark",
            className="mb-2",
        ),
        dbc.Card(
            [
                dbc.CardHeader("Flow (cfm)"),
                dbc.CardBody(html.H4(f"{metrics['flow']}")),
            ],
            color="dark",
            className="mb-2",
        ),
        dbc.Card(
            [
                dbc.CardHeader("Leak probability"),
                dbc.CardBody(html.H4(f"{metrics['leak_score']:.2f}")),
            ],
            color="dark",
            className="mb-2",
        ),
        dbc.Card(
            [
                dbc.CardHeader("Updated"),
                dbc.CardBody(html.Small(metrics["timestamp"])),
            ],
            color="secondary",
            className="mb-2",
        ),
    ]
    return cards


@app.callback(
    Output("network-graph", "figure"),
    Output("pressure-chart", "figure"),
    Output("spectrogram", "figure"),
    Output("kpi-cards", "children"),
    Input("leak-pipe", "value"),
    Input("refresh-interval", "n_intervals"),
)
def update_dashboard(leak_pipe: str, _: int):
    metrics = simulate_metrics(leak_pipe)
    network_fig = build_network_figure(leak_pipe)
    pressure_fig = build_pressure_chart(leak_pipe)
    spectrogram_fig = build_spectrogram(leak_pipe)
    cards = render_kpis(metrics)
    return network_fig, pressure_fig, spectrogram_fig, dbc.Row([dbc.Col(c, md=6) for c in cards])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1", help="Host interface, use 0.0.0.0 to listen on all")
    parser.add_argument("--port", type=int, default=8502, help="Port to serve the Dash app")
    parser.add_argument("--debug", action="store_true", help="Enable Dash debug mode")
    args = parser.parse_args()

    app.run(debug=args.debug, host=args.host, port=args.port)
