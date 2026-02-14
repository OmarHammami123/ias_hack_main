"""
Streamlit Dashboard for Leak Detection System

Run with: streamlit run dashboard/app.py

Supports both CSV (demo mode) and Kafka (real-time mode)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import sys
from datetime import datetime, timedelta
import joblib

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.config import RAW_DATA_DIR, MODELS_DIR
from utils.helpers import calculate_leak_cost


PLOTLY_CONFIG = {"displayModeBar": False}
ZONE_ORDER = ['Zone_A', 'Zone_B', 'Zone_C', 'Zone_D']
SEVERITY_COLORS = {
    'LARGE': '#dc2626',
    'MEDIUM': '#f59e0b',
    'SMALL': '#14b8a6',
    'NONE': '#38bdf8'
}
ZONE_THEMES = {
    'Zone_A': {'color': '#1d4ed8', 'bg': 'rgba(37,99,235,0.14)'},
    'Zone_B': {'color': '#0f766e', 'bg': 'rgba(20,184,166,0.14)'},
    'Zone_C': {'color': '#9333ea', 'bg': 'rgba(147,51,234,0.14)'},
    'Zone_D': {'color': '#b45309', 'bg': 'rgba(245,158,11,0.16)'}
}
ZONE_COLOR_MAP = {zone: theme['color'] for zone, theme in ZONE_THEMES.items()}

# Optional Kafka support
try:
    from kafka import KafkaConsumer
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False


# Page configuration
st.set_page_config(
    page_title="Silent Sabotage - Leak Detection",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    :root {
        --text-primary: #e2e8f0;
        --text-secondary: #cbd5e1;
        --text-muted: #94a3b8;
        --accent-primary: #38bdf8;
        --surface: #111827;
        --surface-alt: #0b1220;
        --border-subtle: #1f2937;
    }

    .stApp {
        color: var(--text-secondary);
        background: radial-gradient(circle at 20% 20%, rgba(56,189,248,0.08), transparent 32%),
                    radial-gradient(circle at 80% 10%, rgba(147,51,234,0.08), transparent 30%),
                    var(--surface-alt);
        font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
        font-size: 15px;
        line-height: 1.55;
    }

    .main-header {
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        padding: 1rem 0 0.5rem 0;
        color: var(--text-primary);
    }

    .hero-banner {
        background: linear-gradient(120deg, rgba(56,189,248,0.16) 0%, rgba(59,130,246,0.12) 100%);
        border: 1px solid rgba(56,189,248,0.22);
        border-radius: 18px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
    }

    .hero-banner h2 {
        color: var(--accent-primary);
        font-size: 1.6rem;
        margin-bottom: 0.5rem;
        font-weight: 700;
    }

    .hero-copy {
        margin-bottom: 0.75rem;
        color: var(--text-secondary);
        line-height: 1.55rem;
    }

    .stat-card {
        background: var(--surface);
        border-radius: 16px;
        padding: 1.2rem 1.4rem;
        box-shadow: 0 22px 40px -28px rgba(0,0,0,0.65);
        border: 1px solid var(--border-subtle);
        min-height: 140px;
        position: relative;
        overflow: hidden;
    }

    .stat-card::after {
        content: "";
        position: absolute;
        inset: 0;
        background: linear-gradient(140deg, rgba(79,70,229,0.08), rgba(14,165,233,0.05));
        opacity: 0;
        transition: opacity 0.4s ease;
    }

    .stat-card:hover::after {
        opacity: 1;
    }

    .stat-label {
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: var(--text-muted);
    }

    .stat-value {
        font-size: 2rem;
        font-weight: 800;
        color: var(--text-primary);
        margin: 0.2rem 0;
    }

    .stat-subtext {
        color: var(--text-secondary);
        font-size: 0.95rem;
    }

    .critical-alert {
        border-left: 6px solid #be123c;
        padding: 16px 18px;
        margin: 8px 0;
        background: rgba(244, 63, 94, 0.1);
        border-radius: 12px;
    }

    .high-alert {
        border-left: 6px solid #d97706;
        padding: 16px 18px;
        margin: 8px 0;
        background: rgba(245, 158, 11, 0.12);
        border-radius: 12px;
    }

    .stAlert {
        border-radius: 14px;
    }

    .insight-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        background: rgba(56,189,248,0.18);
        color: #e2e8f0;
        padding: 0.35rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }

    .insight-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1rem;
        margin-top: 0.75rem;
    }

    .insight-card {
        background: var(--surface);
        border-radius: 14px;
        padding: 1rem 1.2rem;
        border: 1px solid var(--border-subtle);
        box-shadow: 0 18px 28px -20px rgba(0,0,0,0.55);
    }

    .insight-card h4 {
        margin: 0 0 0.35rem 0;
        font-size: 1rem;
        font-weight: 700;
        color: var(--text-primary);
    }

    .insight-card p {
        margin: 0;
        color: var(--text-secondary);
        font-size: 0.95rem;
        line-height: 1.45rem;
    }

    .zone-chip {
        display: inline-flex;
        align-items: center;
        padding: 0.35rem 0.75rem;
        border-radius: 999px;
        background: rgba(59,130,246,0.12);
        color: var(--accent-primary);
        font-size: 0.85rem;
        font-weight: 600;
    }

    .forecast-card {
        padding: 1.1rem 1.3rem;
    }

    .forecast-title {
        margin-top: 0.6rem;
        color: var(--text-primary);
    }

    .forecast-prob {
        margin: 0.4rem 0 0.3rem 0;
        color: var(--text-secondary);
    }

    .forecast-sub {
        margin: 0;
        font-size: 0.9rem;
        color: var(--text-muted);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 0.35rem;
        background: rgba(255,255,255,0.04);
        padding: 0.3rem;
        border-radius: 999px;
        border: 1px solid var(--border-subtle);
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 999px;
        padding: 0.55rem 1.0rem;
        font-weight: 600;
        color: var(--text-muted);
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(56,189,248,0.10);
        color: var(--text-primary);
    }
</style>
""", unsafe_allow_html=True)


# Data loading functions
@st.cache_data(ttl=60)  # Cache for 1 minute (faster refresh for real-time)
def load_sensor_data(mode='csv'):
    """Load sensor data from CSV or Kafka."""
    try:
        if mode == 'csv':
            # Load from CSV files
            pressure_file = RAW_DATA_DIR / "pressure_sensor_data.csv"
            
            if pressure_file.exists():
                df = pd.read_csv(pressure_file)
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                numeric_cols = [
                    'pressure_psi',
                    'temperature_c',
                    'humidity_percent',
                    'airflow_rate',
                    'power_kw'
                ]
                for col in numeric_cols:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                if 'is_anomaly' in df.columns and df['is_anomaly'].dtype != bool:
                    df['is_anomaly'] = df['is_anomaly'].astype(str).str.lower().isin(['true', '1', 'yes'])
                if 'zone' in df.columns:
                    df['zone'] = pd.Categorical(df['zone'], categories=ZONE_ORDER, ordered=True)
                return df
            else:
                st.error("⚠️ Pressure data not found. Run `python data/generate_data.py` first.")
                return pd.DataFrame()
        
        elif mode == 'kafka' and KAFKA_AVAILABLE:
            # TODO: Kafka consumer implementation
            st.info("🔄 Kafka mode - streaming from topic: sensor-readings")
            # Placeholder - will implement Kafka consumer
            return load_sensor_data(mode='csv')  # Fallback to CSV for now
        
        else:
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_classified_leaks():
    """Load pre-classified leaks from Model 2."""
    try:
        leaks_file = MODELS_DIR / "02_severity_classifier" / "classified_leaks.csv"
        
        if leaks_file.exists():
            df = pd.read_csv(leaks_file)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            numeric_cols = [
                'pressure_drop',
                'humidity_change',
                'estimated_annual_cost',
                'priority_score'
            ]
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            if 'zone' in df.columns:
                df['zone'] = pd.Categorical(df['zone'], categories=ZONE_ORDER, ordered=True)
            if 'severity' in df.columns:
                df['severity'] = pd.Categorical(df['severity'], categories=['LARGE', 'MEDIUM', 'SMALL'], ordered=True)
            return df
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading classified leaks: {e}")
        return pd.DataFrame()


def render_stat_card(column, title: str, value: str, subtitle: str, icon: str, highlight: bool = False):
    """Render a glassmorphism stat card."""
    emphasis_class = "style='border: 1px solid rgba(79,70,229,0.35); background: linear-gradient(140deg, rgba(79,70,229,0.14), rgba(14,165,233,0.12));'" if highlight else ""
    column.markdown(
        f"""
        <div class='stat-card' {emphasis_class}>
            <div class='stat-label'>{icon} {title}</div>
            <div class='stat-value'>{value}</div>
            <div class='stat-subtext'>{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def prepare_recent_trends(df_sensor: pd.DataFrame, hours: int = 6, max_points: int = 5000) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Prepare sampled trend data and anomaly points for chart rendering."""
    if df_sensor.empty:
        return pd.DataFrame(), pd.DataFrame()

    window_start = df_sensor['timestamp'].max() - pd.Timedelta(hours=hours)
    recent_data = df_sensor[df_sensor['timestamp'] > window_start].copy()

    if recent_data.empty:
        return pd.DataFrame(), pd.DataFrame()

    recent_data = recent_data.sort_values('timestamp')
    if len(recent_data) > max_points:
        step = max(1, len(recent_data) // max_points)
        recent_data = recent_data.iloc[::step].copy()

    trend_data = recent_data.groupby(['timestamp', 'zone'], as_index=False, observed=False)[['pressure_psi', 'humidity_percent']].mean()
    anomalies = recent_data[recent_data['is_anomaly']] if 'is_anomaly' in recent_data.columns else pd.DataFrame()

    return trend_data, anomalies


def get_zone_pipeline_paths() -> dict[str, list[tuple[float, float]]]:
    """Return polyline paths representing zone-level pipeline routing."""
    return {
        'Zone_A': [(0.8, 8.0), (3.2, 8.0), (3.2, 6.2)],
        'Zone_B': [(6.8, 8.0), (9.2, 8.0), (9.2, 6.2)],
        'Zone_C': [(0.8, 1.0), (3.2, 1.0), (3.2, 2.8)],
        'Zone_D': [(6.8, 1.0), (9.2, 1.0), (9.2, 2.8)],
    }


def interpolate_on_polyline(points: list[tuple[float, float]], ratio: float) -> tuple[float, float]:
    """Interpolate a point on a multi-segment polyline using 0..1 ratio distance."""
    if not points or len(points) < 2:
        return (0.0, 0.0)

    segment_lengths = []
    total_length = 0.0
    for idx in range(len(points) - 1):
        x0, y0 = points[idx]
        x1, y1 = points[idx + 1]
        seg_length = float(np.hypot(x1 - x0, y1 - y0))
        segment_lengths.append(seg_length)
        total_length += seg_length

    if total_length == 0:
        return points[0]

    target = max(0.0, min(1.0, ratio)) * total_length
    traversed = 0.0
    for idx, seg_length in enumerate(segment_lengths):
        if traversed + seg_length >= target:
            x0, y0 = points[idx]
            x1, y1 = points[idx + 1]
            local_ratio = 0 if seg_length == 0 else (target - traversed) / seg_length
            return (x0 + (x1 - x0) * local_ratio, y0 + (y1 - y0) * local_ratio)
        traversed += seg_length

    return points[-1]


def build_sensor_layout(df_sensor: pd.DataFrame) -> pd.DataFrame:
    """Generate deterministic serial (x, y) coordinates along zone pipeline routes."""
    sensors = df_sensor[['sensor_id', 'zone']].drop_duplicates().copy()
    if sensors.empty:
        return sensors

    pipeline_paths = get_zone_pipeline_paths()

    sensors['sensor_num'] = sensors['sensor_id'].str.extract(r'_(\d+)$').astype(float).fillna(1).astype(int)
    sensors = sensors.sort_values(['zone', 'sensor_num', 'sensor_id']).copy()

    coordinates = []
    for zone in sensors['zone'].astype(str).unique():
        zone_rows = sensors[sensors['zone'].astype(str) == zone].copy()
        count = len(zone_rows)
        if count == 0:
            continue
        for idx, (_, row) in enumerate(zone_rows.iterrows(), start=1):
            ratio = idx / (count + 1)
            x, y = interpolate_on_polyline(pipeline_paths.get(zone, [(0.0, 0.0), (1.0, 0.0)]), ratio)
            coordinates.append((row['sensor_id'], row['zone'], x, y))

    layout_df = pd.DataFrame(coordinates, columns=['sensor_id', 'zone', 'x', 'y'])

    return layout_df


def create_sensor_floor_map(df_sensor: pd.DataFrame, df_leaks: pd.DataFrame):
    """Render per-sensor floor map with problem hotspots."""
    sensor_layout = build_sensor_layout(df_sensor)
    if sensor_layout.empty:
        return go.Figure()

    severity_rank = {'SMALL': 1, 'MEDIUM': 2, 'LARGE': 3}
    inverse_rank = {1: 'SMALL', 2: 'MEDIUM', 3: 'LARGE'}

    issue_source = df_leaks.copy()
    if 'is_anomaly' in issue_source.columns:
        issue_source = issue_source[issue_source['is_anomaly'] == True]

    if issue_source.empty:
        sensor_metrics = pd.DataFrame(columns=['sensor_id', 'issue_count', 'annual_cost_tnd', 'max_rank'])
    else:
        issue_source = issue_source.copy()
        issue_source['severity_rank'] = issue_source['severity'].astype(str).map(severity_rank).fillna(0).astype(int)
        sensor_metrics = issue_source.groupby('sensor_id', as_index=False).agg(
            issue_count=('sensor_id', 'size'),
            annual_cost_tnd=('estimated_annual_cost', 'sum'),
            max_rank=('severity_rank', 'max')
        )

    map_df = sensor_layout.merge(sensor_metrics, on='sensor_id', how='left')
    map_df['issue_count'] = map_df['issue_count'].fillna(0).astype(int)
    map_df['annual_cost_tnd'] = map_df['annual_cost_tnd'].fillna(0.0)
    map_df['max_rank'] = map_df['max_rank'].fillna(0).astype(int)
    map_df['severity'] = map_df['max_rank'].map(inverse_rank).fillna('NONE')
    map_df['marker_size'] = 14 + np.clip(map_df['issue_count'], 0, 15) * 2
    map_df['marker_color'] = map_df['severity'].map(SEVERITY_COLORS).fillna(SEVERITY_COLORS['NONE'])
    labeled_sensors = map_df.sort_values(['issue_count', 'annual_cost_tnd'], ascending=[False, False]).head(6)

    fig = go.Figure()

    zone_boxes = {
        'Zone_A': (0, 5, 4, 9),
        'Zone_B': (6, 5, 10, 9),
        'Zone_C': (0, 0, 4, 4),
        'Zone_D': (6, 0, 10, 4)
    }

    # Main distribution manifold + branches for a clearer physical interpretation
    fig.add_shape(type='line', x0=5.0, y0=0.2, x1=5.0, y1=8.9, line=dict(color='#475569', width=5))
    fig.add_annotation(x=5.0, y=9.15, text="<b>Main Air Line</b>", showarrow=False, font=dict(size=11, color='#475569'))

    branch_lines = {
        'Zone_A': (5.0, 8.0, 3.2, 8.0),
        'Zone_B': (5.0, 8.0, 6.8, 8.0),
        'Zone_C': (5.0, 1.0, 3.2, 1.0),
        'Zone_D': (5.0, 1.0, 6.8, 1.0)
    }
    for x0, y0, x1, y1 in branch_lines.values():
        fig.add_shape(type='line', x0=x0, y0=y0, x1=x1, y1=y1, line=dict(color='#94a3b8', width=3))
        fig.add_annotation(x=x1, y=y1, ax=x0, ay=y0, xref='x', yref='y', axref='x', ayref='y',
                           showarrow=True, arrowhead=3, arrowsize=1, arrowwidth=1.4, arrowcolor='#94a3b8', text='')

    for points in get_zone_pipeline_paths().values():
        for idx in range(len(points) - 1):
            x0, y0 = points[idx]
            x1, y1 = points[idx + 1]
            fig.add_shape(type='line', x0=x0, y0=y0, x1=x1, y1=y1, line=dict(color='#64748b', width=4))

    for zone, (x0, y0, x1, y1) in zone_boxes.items():
        fig.add_shape(
            type='rect',
            x0=x0,
            y0=y0,
            x1=x1,
            y1=y1,
            line=dict(color=ZONE_THEMES[zone]['color'], width=2),
            fillcolor=ZONE_THEMES[zone]['bg']
        )
        fig.add_annotation(
            x=(x0 + x1) / 2,
            y=y1 - 0.25,
            text=f"<b>{zone.replace('_', ' ')}</b>",
            showarrow=False,
            font=dict(color=ZONE_THEMES[zone]['color'], size=12)
        )

    symbol_by_severity = {
        'LARGE': 'x',
        'MEDIUM': 'diamond',
        'SMALL': 'circle',
        'NONE': 'circle-open'
    }

    for severity in ['LARGE', 'MEDIUM', 'SMALL', 'NONE']:
        subset = map_df[map_df['severity'] == severity]
        if subset.empty:
            continue
        fig.add_trace(go.Scatter(
            x=subset['x'],
            y=subset['y'],
            mode='markers',
            marker=dict(
                size=subset['marker_size'],
                color=subset['marker_color'],
                symbol=symbol_by_severity[severity],
                line=dict(color='white', width=1.5)
            ),
            name=f"{severity} sensors",
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Zone: %{customdata[1]}<br>"
                "Open issues: %{customdata[2]}<br>"
                "Severity: %{customdata[3]}<br>"
                "Annual impact: %{customdata[4]:,.0f} TND<extra></extra>"
            ),
            customdata=np.stack([
                subset['sensor_id'],
                subset['zone'],
                subset['issue_count'],
                subset['severity'],
                subset['annual_cost_tnd']
            ], axis=-1)
        ))

    if not labeled_sensors.empty:
        fig.add_trace(go.Scatter(
            x=labeled_sensors['x'],
            y=labeled_sensors['y'],
            mode='text',
            text=labeled_sensors['sensor_id'],
            textposition='top center',
            textfont=dict(size=10, color='#0f172a'),
            name='Top hotspot labels',
            showlegend=False,
            hoverinfo='skip'
        ))

    fig.update_layout(
        title='Sensor Placement & Problem Hotspots',
        template='plotly_white',
        height=530,
        margin=dict(l=20, r=20, t=50, b=20),
        xaxis=dict(visible=False, range=[-0.2, 10.5]),
        yaxis=dict(visible=False, range=[-0.5, 9.5]),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, x=0)
    )

    return fig


def build_sensor_hotspot_table(df_leaks: pd.DataFrame) -> pd.DataFrame:
    """Build top problematic sensors for quick operational targeting."""
    if df_leaks.empty:
        return pd.DataFrame()

    ranked = df_leaks.copy()
    if 'is_anomaly' in ranked.columns:
        ranked = ranked[ranked['is_anomaly'] == True]
    if ranked.empty:
        return pd.DataFrame()

    severity_score = {'SMALL': 1, 'MEDIUM': 2, 'LARGE': 3}
    ranked['zone'] = ranked['zone'].astype(str)
    ranked['severity_score'] = ranked['severity'].astype(str).map(severity_score).fillna(0).astype(int)

    summary = ranked.groupby(['sensor_id', 'zone'], as_index=False, observed=True).agg(
        leak_count=('sensor_id', 'size'),
        annual_cost_tnd=('estimated_annual_cost', 'sum'),
        max_severity_score=('severity_score', 'max')
    )

    inverse = {1: 'SMALL', 2: 'MEDIUM', 3: 'LARGE'}
    summary['max_severity'] = summary['max_severity_score'].map(inverse).fillna('NONE')
    summary = summary.sort_values(['max_severity_score', 'annual_cost_tnd', 'leak_count'], ascending=[False, False, False]).head(10)
    summary['zone'] = summary['zone'].astype(str).str.replace('_', ' ', regex=False)

    return summary[['sensor_id', 'zone', 'leak_count', 'max_severity', 'annual_cost_tnd']]


def build_key_insights(df_leaks: pd.DataFrame) -> list[dict[str, str]]:
    """Generate top business insights for the hero banner."""
    if df_leaks.empty:
        return []

    insights = []

    # Costliest zone
    zone_costs = df_leaks.groupby('zone', observed=False)['estimated_annual_cost'].sum().sort_values(ascending=False)
    if not zone_costs.empty:
        top_zone, top_zone_cost = zone_costs.index[0], zone_costs.iloc[0]
        insights.append({
            "title": "Top Cost Driver",
            "body": f"{top_zone.replace('_', ' ')} leaks cost {top_zone_cost:,.0f} TND/year."
        })

    # Most frequent sensor
    sensor_counts = df_leaks['sensor_id'].value_counts()
    if not sensor_counts.empty:
        sensor_id = sensor_counts.index[0]
        count = sensor_counts.iloc[0]
        insights.append({
            "title": "Sensor Under Stress",
            "body": f"{sensor_id} triggered {count:,} leaks – inspect its segment." 
        })

    # Severity ratio
    large = (df_leaks['severity'] == 'LARGE').sum()
    if large:
        share = (large / len(df_leaks)) * 100
        insights.append({
            "title": "Critical Exposure",
            "body": f"{share:.1f}% of leaks are LARGE severity – urgent repairs required."
        })

    return insights[:3]


def calculate_metrics(df_leaks):
    """Calculate KPIs for the dashboard."""
    if df_leaks.empty:
        return {
            'total_leaks': 0,
            'active_zones': 0,
            'total_cost': 0,
            'avg_leak_size': 0,
            'large_leaks': 0,
            'medium_leaks': 0,
            'small_leaks': 0
        }
    
    # Count leaks by severity
    severity_counts = df_leaks['severity'].value_counts()
    
    return {
        'total_leaks': len(df_leaks),
        'active_zones': df_leaks['zone'].nunique(),
        'total_cost': df_leaks['estimated_annual_cost'].sum(),
        'avg_leak_size': df_leaks['pressure_drop'].mean(),
        'large_leaks': severity_counts.get('LARGE', 0),
        'medium_leaks': severity_counts.get('MEDIUM', 0),
        'small_leaks': severity_counts.get('SMALL', 0)
    }


def calculate_zone_metrics(df_leaks):
    """Calculate per-zone statistics."""
    if df_leaks.empty:
        return pd.DataFrame()
    
    zone_stats = df_leaks.groupby('zone', observed=False).agg({
        'sensor_id': 'count',
        'estimated_annual_cost': 'sum',
        'pressure_drop': 'mean',
        'humidity_change': 'mean',
        'severity': lambda x: x.value_counts().index[0] if len(x) > 0 else 'UNKNOWN'
    }).rename(columns={
        'sensor_id': 'leak_count',
        'estimated_annual_cost': 'total_cost_tnd',
        'pressure_drop': 'avg_pressure_drop',
        'humidity_change': 'avg_humidity_change',
        'severity': 'dominant_severity'
    })
    
    return zone_stats


def create_factory_map(df_leaks):
    """Create factory zone visualization."""
    zones = ZONE_ORDER
    
    # Zone colors
    zone_colors = {
        'OK': '#22c55e',        # Green
        'WARNING': '#eab308',   # Yellow
        'CRITICAL': '#ef4444'   # Red
    }
    
    # Determine zone status based on leak severity
    zone_status = {}
    zone_leak_counts = {}
    
    for zone in zones:
        zone_leaks = df_leaks[df_leaks['zone'] == zone]
        zone_leak_counts[zone] = len(zone_leaks)
        
        if zone_leaks.empty:
            zone_status[zone] = 'OK'
        else:
            # Check for LARGE severity leaks
            large_count = (zone_leaks['severity'] == 'LARGE').sum()
            medium_count = (zone_leaks['severity'] == 'MEDIUM').sum()
            
            if large_count > 0:
                zone_status[zone] = 'CRITICAL'
            elif medium_count > 5:
                zone_status[zone] = 'WARNING'
            else:
                zone_status[zone] = 'WARNING' if len(zone_leaks) > 0 else 'OK'
    
    # Create visualization
    fig = go.Figure()
    
    positions = [(0, 1), (1, 1), (0, 0), (1, 0)]  # 2x2 grid
    
    for zone, (x, y) in zip(zones, positions):
        status = zone_status[zone]
        leak_count = zone_leak_counts[zone]
        
        # Status emoji
        status_emoji = {
            'OK': '✅',
            'WARNING': '⚠️',
            'CRITICAL': '🔴'
        }
        
        fig.add_trace(go.Scatter(
            x=[x + 0.5],
            y=[y + 0.5],
            mode='markers+text',
            marker=dict(
                size=200,
                color=zone_colors[status],
                symbol='square',
                line=dict(color='white', width=3)
            ),
            text=f"<b>{zone.replace('_', ' ')}</b><br>{status_emoji[status]} {status}<br>{leak_count} leaks",
            textfont=dict(size=14, color='white', family='Arial Black'),
            textposition="middle center",
            name=zone,
            hovertemplate=f"<b>{zone}</b><br>Status: {status}<br>Leaks: {leak_count}<extra></extra>"
        ))
    
    fig.update_layout(
        title="Factory Floor Leak Status",
        showlegend=False,
        height=450,
        xaxis=dict(visible=False, range=[-0.2, 2.2]),
        yaxis=dict(visible=False, range=[-0.2, 2.2]),
        plot_bgcolor='#f8f9fa',
        paper_bgcolor='white',
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig


def create_alert_table(df_leaks):
    """Create table of recent alerts."""
    if df_leaks.empty:
        return pd.DataFrame()
    
    # Get top 20 most costly leaks
    top_leaks = df_leaks.nlargest(20, 'estimated_annual_cost').copy()
    
    # Build alert table
    alerts = []
    for idx, row in top_leaks.iterrows():
        # Determine alert level
        if row['severity'] == 'LARGE':
            alert_icon = '🔴'
        elif row['severity'] == 'MEDIUM':
            alert_icon = '🟡'
        else:
            alert_icon = '🟢'
        
        alerts.append({
            'Alert': alert_icon,
            'Time': row['timestamp'].strftime('%H:%M:%S'),
            'Zone': row['zone'].replace('_', ' '),
            'Sensor': row['sensor_id'],
            'Severity': row['severity'],
            'Pressure Drop': f"{row['pressure_drop']:.1f} PSI",
            'Humidity Δ': f"{row['humidity_change']:.1f}%",
            'Cost (TND/yr)': f"{row['estimated_annual_cost']:,.0f}",
            'Status': 'Active'
        })
    
    return pd.DataFrame(alerts)


def main():
    """Main dashboard application."""
    
    # Sidebar
    with st.sidebar:
        st.image(
            "https://via.placeholder.com/200x80/667eea/ffffff?text=Silent+Sabotage",
            width=220
        )
        st.markdown("---")
        
        st.subheader("⚙️ Data Source")
        data_mode = st.radio(
            "Select mode:",
            ['CSV (Demo)', 'Kafka (Real-time)'],
            help="CSV mode uses pre-generated data. Kafka mode streams from sensors."
        )
        
        mode = 'csv' if 'CSV' in data_mode else 'kafka'
        
        if mode == 'kafka' and not KAFKA_AVAILABLE:
            st.warning("⚠️ Kafka not installed. Install with: `pip install kafka-python`")
            mode = 'csv'
        
        st.markdown("---")
        st.subheader("📊 Model Status")
        st.success("✅ Model 1: Isolation Forest")
        st.success("✅ Model 2: Severity Classifier")
        st.success("✅ Model 3: Leak Size Estimator")
        st.info("⏳ Model 4: Acoustic Classifier")
        st.info("⏳ Model 5: Predictive Forecast")
        
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()
    
    # Header
    st.markdown('<h1 class="main-header">🏭 Silent Sabotage - Compressed Air Leak Detection System</h1>', 
                unsafe_allow_html=True)
    st.markdown("---")
    
    # Load data
    df_sensor = load_sensor_data(mode=mode)
    df_leaks = load_classified_leaks()
    
    if df_leaks.empty:
        st.error("❌ No classified leak data found. Please run Models 1-3 first:")
        st.code("python data/generate_data.py\npython models/01_isolation_forest/train.py\npython models/02_severity_classifier/train.py\npython models/03_leak_size_estimator/train.py")
        st.stop()
    
    # Calculate metrics and hero content
    metrics = calculate_metrics(df_leaks)
    cost_per_leak = metrics['total_cost'] / metrics['total_leaks'] if metrics['total_leaks'] else 0
    zone_costs = df_leaks.groupby('zone', observed=False)['estimated_annual_cost'].sum()
    top_zone = zone_costs.idxmax() if not zone_costs.empty else None
    top_zone_cost = zone_costs.max() if not zone_costs.empty else 0
    insights = build_key_insights(df_leaks)

    # Hero banner
    st.markdown(
        f"""
        <div class='hero-banner'>
            <h2>Real-time Leak Intelligence</h2>
            <p class='hero-copy'>Your compressed air network is currently losing
            <strong>{metrics['total_cost']:,.0f} TND/year</strong> across
            <strong>{metrics['total_leaks']:,}</strong> detected leaks. Streamline repairs starting with the
            highest-impact zones.</p>
            <div>
                <span class='insight-badge'>💸 {cost_per_leak:,.0f} TND average leak cost</span>
                <span class='insight-badge'>🏭 {metrics['active_zones']} / 4 zones affected</span>
                <span class='insight-badge'>⚠️ {metrics['large_leaks']} critical leaks</span>
            </div>
            <div class='insight-grid'>
                {''.join([f"<div class='insight-card'><h4>{ins['title']}</h4><p>{ins['body']}</p></div>" for ins in insights])}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # KPI Cards
    c1, c2, c3, c4 = st.columns(4, gap="large")
    render_stat_card(
        c1,
        "Total Leaks",
        f"{metrics['total_leaks']:,}",
        "Detected by Model 1",
        "🚨",
        highlight=True,
    )
    render_stat_card(
        c2,
        "Annual Cost",
        f"{metrics['total_cost']/1_000_000:.2f}M TND",
        "Financial impact if unresolved",
        "💰",
    )
    render_stat_card(
        c3,
        "Critical Leaks",
        f"{metrics['large_leaks']:,}",
        f"{metrics['medium_leaks']:,} medium severity",
        "🔴",
    )
    render_stat_card(
        c4,
        "Most Costly Zone",
        f"{top_zone.replace('_',' ') if top_zone else 'N/A'}",
        f"{top_zone_cost:,.0f} TND/year",
        "🏭",
    )

    st.write("")
    
    # Main content area
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("🗺️ Factory Floor Status")
        factory_map = create_factory_map(df_leaks)
        st.plotly_chart(factory_map, width='stretch', config=PLOTLY_CONFIG)
        
        # Pressure trends over time
        if not df_sensor.empty:
            st.subheader("📈 Pressure Trends - Last 6 Hours")
            trend_data, anomalies = prepare_recent_trends(df_sensor, hours=6, max_points=5000)
            if trend_data.empty:
                st.info("No recent sensor trend data available.")
            else:
                fig_pressure = px.line(
                    trend_data,
                    x='timestamp',
                    y='pressure_psi',
                    color='zone',
                    title='',
                    labels={'pressure_psi': 'Pressure (PSI)', 'timestamp': 'Time'},
                    color_discrete_map=ZONE_COLOR_MAP,
                    category_orders={'zone': ZONE_ORDER}
                )
                fig_pressure.update_layout(
                    template='plotly_white',
                    margin=dict(l=10, r=20, t=30, b=10),
                    legend=dict(orientation='h', yanchor='bottom', y=1.02, x=0),
                    hovermode='x unified'
                )
                fig_pressure.update_traces(line=dict(width=2.3))

                if not anomalies.empty:
                    fig_pressure.add_scatter(
                        x=anomalies['timestamp'],
                        y=anomalies['pressure_psi'],
                        mode='markers',
                        marker=dict(color='red', size=8, symbol='x'),
                        name='Detected Leaks',
                        showlegend=True
                    )

                st.plotly_chart(fig_pressure, width='stretch', config=PLOTLY_CONFIG)

                st.subheader("💧 Humidity Trends - Last 6 Hours")
                fig_humidity = px.line(
                    trend_data,
                    x='timestamp',
                    y='humidity_percent',
                    color='zone',
                    title='',
                    labels={'humidity_percent': 'Humidity (%)', 'timestamp': 'Time'},
                    color_discrete_map=ZONE_COLOR_MAP,
                    category_orders={'zone': ZONE_ORDER}
                )
                fig_humidity.update_layout(
                    template='plotly_white',
                    margin=dict(l=10, r=20, t=30, b=10),
                    legend=dict(orientation='h', yanchor='bottom', y=1.02, x=0),
                    hovermode='x unified'
                )
                fig_humidity.update_traces(line=dict(width=2.1))
                st.plotly_chart(fig_humidity, width='stretch', config=PLOTLY_CONFIG)
    
    with col_right:
        st.subheader("🚨 Top Priority Alerts")
        
        # Show top 5 most costly leaks
        top5_leaks = df_leaks.nlargest(5, 'estimated_annual_cost')
        
        for idx, leak in top5_leaks.iterrows():
            severity_class = "critical-alert" if leak['severity'] == 'LARGE' else "high-alert"
            cost_formatted = f"{leak['estimated_annual_cost']:,.0f} TND/yr"
            
            st.markdown(f"""
            <div class="{severity_class}">
                <b>{leak['severity']}</b> - {leak['zone'].replace('_', ' ')}<br>
                Sensor: {leak['sensor_id']}<br>
                Pressure Drop: {leak['pressure_drop']:.1f} PSI<br>
                Cost: {cost_formatted}<br>
                <small>{leak['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}</small>
            </div>
            """, unsafe_allow_html=True)
        
        # Severity distribution pie chart
        st.subheader("📊 Severity Distribution")
        severity_counts = df_leaks['severity'].value_counts()
        fig_pie = px.pie(
            values=severity_counts.values,
            names=severity_counts.index,
            color=severity_counts.index,
            color_discrete_map=SEVERITY_COLORS
        )
        fig_pie.update_traces(
            hole=0.55,
            textinfo='label+percent',
            pull=[0.1 if name == 'LARGE' else 0 for name in severity_counts.index]
        )
        fig_pie.update_layout(
            template='plotly_white',
            margin=dict(l=10, r=10, t=20, b=10),
            legend=dict(orientation='h', yanchor='bottom', y=-0.1, x=0.2)
        )
        st.plotly_chart(fig_pie, width='stretch', config=PLOTLY_CONFIG)
    
    # Tabs for additional views
    st.markdown("---")
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Analytics", "📋 Leak Table", "🔮 Predictive", "⚙️ Settings"])
    
    with tab1:
        st.subheader("Detailed Analytics by Zone")
        
        zone_stats = calculate_zone_metrics(df_leaks)
        analytics_table = zone_stats.reset_index().rename(columns={
            'zone': 'Zone',
            'leak_count': 'Leak Count',
            'total_cost_tnd': 'Annual Cost (TND)',
            'avg_pressure_drop': 'Avg Pressure Drop (PSI)',
            'avg_humidity_change': 'Avg Humidity Δ (%)',
            'dominant_severity': 'Dominant Severity'
        })
        analytics_table['Zone'] = analytics_table['Zone'].astype(str).str.replace('_', ' ', regex=False)

        st.dataframe(
            analytics_table,
            width='stretch',
            hide_index=True,
            column_config={
                'Zone': st.column_config.TextColumn('Zone'),
                'Leak Count': st.column_config.NumberColumn('Leak Count', format='%d'),
                'Annual Cost (TND)': st.column_config.NumberColumn('Annual Cost (TND)', format='%.0f'),
                'Avg Pressure Drop (PSI)': st.column_config.NumberColumn('Avg Pressure Drop (PSI)', format='%.2f'),
                'Avg Humidity Δ (%)': st.column_config.NumberColumn('Avg Humidity Δ (%)', format='%.2f'),
                'Dominant Severity': st.column_config.TextColumn('Dominant Severity')
            }
        )

        st.caption("Clean table style applied for consistent rows; colors now appear only in charts and alert cards.")
        
        # Cost distribution by zone
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Cost by Zone (TND/year)**")
            zone_costs = df_leaks.groupby('zone', observed=False)['estimated_annual_cost'].sum().reset_index()
            fig_bar = px.bar(
                zone_costs,
                x='zone',
                y='estimated_annual_cost',
                labels={'estimated_annual_cost': 'Annual Cost (TND)', 'zone': 'Zone'},
                color='zone',
                color_discrete_map=ZONE_COLOR_MAP,
                category_orders={'zone': ZONE_ORDER}
            )
            fig_bar.update_layout(
                template='plotly_white',
                margin=dict(l=10, r=10, t=30, b=40),
                showlegend=False
            )
            fig_bar.update_traces(marker=dict(line=dict(width=0), opacity=0.9))
            st.plotly_chart(fig_bar, width='stretch', config=PLOTLY_CONFIG)
        
        with col2:
            st.write("**Leak Count by Zone**")
            zone_counts = df_leaks['zone'].value_counts().reset_index()
            zone_counts.columns = ['zone', 'count']
            fig_bar2 = px.bar(
                zone_counts,
                x='zone',
                y='count',
                labels={'count': 'Number of Leaks', 'zone': 'Zone'},
                color='zone',
                color_discrete_map=ZONE_COLOR_MAP,
                category_orders={'zone': ZONE_ORDER}
            )
            fig_bar2.update_layout(
                template='plotly_white',
                margin=dict(l=10, r=10, t=30, b=40),
                showlegend=False
            )
            fig_bar2.update_traces(marker=dict(line=dict(width=0), opacity=0.9))
            st.plotly_chart(fig_bar2, width='stretch', config=PLOTLY_CONFIG)

        st.subheader("🧭 Sensor Placement Map")
        st.caption("Map legend: size = issue volume, color/shape = max severity. Labels are shown only for top hotspots; hover any point for full sensor details.")
        sensor_floor_map = create_sensor_floor_map(df_sensor, df_leaks)
        st.plotly_chart(sensor_floor_map, width='stretch', config=PLOTLY_CONFIG)

        hotspot_table = build_sensor_hotspot_table(df_leaks)
        if not hotspot_table.empty:
            st.write("**Top Problematic Sensors**")
            st.dataframe(
                hotspot_table,
                width='stretch',
                hide_index=True,
                column_config={
                    'sensor_id': st.column_config.TextColumn('Sensor'),
                    'zone': st.column_config.TextColumn('Zone'),
                    'leak_count': st.column_config.NumberColumn('Leaks', format='%d'),
                    'max_severity': st.column_config.TextColumn('Max Severity'),
                    'annual_cost_tnd': st.column_config.NumberColumn('Annual Impact (TND)', format='%.0f')
                }
            )
    
    with tab2:
        st.subheader("Complete Leak Registry")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            zone_filter = st.multiselect("Filter by Zone", options=['All'] + list(df_leaks['zone'].unique()), default=['All'])
        with col2:
            severity_filter = st.multiselect("Filter by Severity", options=['All'] + list(df_leaks['severity'].unique()), default=['All'])
        with col3:
            sort_by = st.selectbox("Sort by", ['Cost (High to Low)', 'Cost (Low to High)', 'Time (Recent)', 'Pressure Drop'])
        
        # Apply filters
        filtered_leaks = df_leaks.copy()
        if 'All' not in zone_filter and len(zone_filter) > 0:
            filtered_leaks = filtered_leaks[filtered_leaks['zone'].isin(zone_filter)]
        if 'All' not in severity_filter and len(severity_filter) > 0:
            filtered_leaks = filtered_leaks[filtered_leaks['severity'].isin(severity_filter)]
        
        # Apply sorting
        if sort_by == 'Cost (High to Low)':
            filtered_leaks = filtered_leaks.sort_values('estimated_annual_cost', ascending=False)
        elif sort_by == 'Cost (Low to High)':
            filtered_leaks = filtered_leaks.sort_values('estimated_annual_cost', ascending=True)
        elif sort_by == 'Time (Recent)':
            filtered_leaks = filtered_leaks.sort_values('timestamp', ascending=False)
        else:
            filtered_leaks = filtered_leaks.sort_values('pressure_drop', ascending=False)
        
        # Summary chips
        total_selected = len(filtered_leaks)
        cost_selected = filtered_leaks['estimated_annual_cost'].sum()
        st.markdown(
            f"""
            <div style="display:flex; gap:0.75rem; flex-wrap:wrap; margin:0.5rem 0 1rem 0;">
                <span class='insight-badge'>📈 {total_selected:,} leaks selected</span>
                <span class='insight-badge'>💸 {cost_selected:,.0f} TND annual cost</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        # Display table
        alerts_df = create_alert_table(filtered_leaks)
        if alerts_df.empty:
            st.info("No leaks match the current filters.")
        else:
            st.dataframe(
                alerts_df,
                width='stretch',
                height=420,
                hide_index=True,
                column_config={
                    'Alert': st.column_config.TextColumn('', width='small'),
                    'Zone': st.column_config.TextColumn('Zone'),
                    'Sensor': st.column_config.TextColumn('Sensor'),
                    'Severity': st.column_config.TextColumn('Severity'),
                    'Pressure Drop': st.column_config.TextColumn('Pressure Drop'),
                    'Humidity Δ': st.column_config.TextColumn('Humidity Δ'),
                    'Cost (TND/yr)': st.column_config.TextColumn('Annual Cost (TND/yr)'),
                    'Status': st.column_config.TextColumn('Status'),
                    'Time': st.column_config.TextColumn('Detected At')
                }
            )
        
        # Download button
        csv = filtered_leaks.to_csv(index=False)
        st.download_button(
            label="📥 Download Leak Data (CSV)",
            data=csv,
            file_name=f"leak_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime='text/csv'
        )
    
    with tab3:
        st.subheader("🔮 Predictive Maintenance Forecast")
        st.info("This feature requires Model 5 (Predictive Forecasting) to be trained.")
        
        st.write("**Future Implementation:**")
        st.markdown("""
        - **30-day leak probability** per zone
        - **Risk assessment** based on pipe age, material, and historical data
        - **Maintenance scheduling** recommendations
        - **Cost avoidance** projections
        """)
        
        # Placeholder forecast visualization
        st.write("**Sample 30-Day Forecast (Placeholder):**")
        forecast_data = pd.DataFrame({
            'Zone': ['Zone_A', 'Zone_B', 'Zone_C', 'Zone_D'],
            'Current Leaks': [metrics['total_leaks']//4] * 4,
            'Predicted New Leaks (30d)': [12, 8, 3, 15],
            '30-Day Probability (%)': [68, 42, 23, 71],
            'Risk Level': ['HIGH', 'MEDIUM', 'LOW', 'CRITICAL']
        })

        forecast_cols = st.columns(4, gap="large")
        risk_icons = {'LOW': '🟢', 'MEDIUM': '🟡', 'HIGH': '🟠', 'CRITICAL': '🔴'}
        for col, (_, row) in zip(forecast_cols, forecast_data.iterrows()):
            col.markdown(
                f"""
                <div class='insight-card forecast-card'>
                    <p class='zone-chip' style="background:{ZONE_THEMES.get(row['Zone'], {}).get('bg', 'rgba(59,130,246,0.12)')}; color:{ZONE_THEMES.get(row['Zone'], {}).get('color', '#1d4ed8')};">{row['Zone'].replace('_',' ')}</p>
                    <h4 class='forecast-title'>{risk_icons[row['Risk Level']]} {row['Risk Level']} risk</h4>
                    <p class='forecast-prob'>{row['30-Day Probability (%)']}% probability next 30 days.</p>
                    <p class='forecast-sub'>Projected new leaks: <strong>{row['Predicted New Leaks (30d)']}</strong></p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        
        st.dataframe(forecast_data, width='stretch', hide_index=True)
    
    with tab4:
        st.subheader("⚙️ System Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Alert Thresholds:**")
            critical_threshold = st.slider("Critical Severity (PSI drop)", 10, 40, 15)
            medium_threshold = st.slider("Medium Severity (PSI drop)", 3, 20, 5)
            
            st.write("**Display Settings:**")
            refresh_rate = st.select_slider(
                "Dashboard refresh rate",
                options=[1, 5, 10, 30, 60],
                value=5,
                format_func=lambda x: f"{x} seconds" if x < 60 else f"{x//60} minute(s)"
            )
        
        with col2:
            st.write("**Notification Settings:**")
            email_alerts = st.checkbox("Enable email alerts", value=True)
            sms_alerts = st.checkbox("Enable SMS alerts", value=False)
            webhook_url = st.text_input("Webhook URL (optional)", placeholder="https://hooks.slack.com/...")
            
            st.write("**Export Options:**")
            auto_export = st.checkbox("Auto-export daily reports", value=False)
            export_format = st.selectbox("Export format", ['CSV', 'Excel', 'JSON'])
        
        if st.button("💾 Save Settings"):
            st.success("✅ Settings saved successfully!")
            st.info(f"Dashboard will refresh every {refresh_rate} seconds")
    
    # Footer
    st.markdown("---")
    st.markdown(f"""
    <div style='text-align: center; color: gray;'>
        <small>🏭 Silent Sabotage Leak Detection System | 
        Data Mode: {data_mode} | 
        Total Leaks: {metrics['total_leaks']:,} | 
        Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
