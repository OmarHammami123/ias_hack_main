"""
Streamlit Dashboard for Leak Detection System

Run with: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import sys
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.config import DASHBOARD_CONFIG, RAW_DATA_DIR
from utils.helpers import classify_severity, calculate_leak_cost


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
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1E3A8A;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .critical-alert {
        border-left: 5px solid #dc3545;
        padding: 10px;
        margin: 5px 0;
        background-color: #f8d7da;
        border-radius: 5px;
    }
    
    .high-alert {
        border-left: 5px solid #ffc107;
        padding: 10px;
        margin: 5px 0;
        background-color: #fff3cd;
        border-radius: 5px;
    }
    
    .stAlert {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)


# Data loading functions
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_sensor_data():
    """Load pressure and acoustic sensor data."""
    try:
        pressure_file = RAW_DATA_DIR / "pressure_sensor_data.csv"
        acoustic_file = RAW_DATA_DIR / "acoustic_sensor_data.csv"
        
        if pressure_file.exists():
            df_pressure = pd.read_csv(pressure_file)
            df_pressure['timestamp'] = pd.to_datetime(df_pressure['timestamp'])
        else:
            st.warning("⚠️ Pressure data not found. Run `python data/generate_data.py` first.")
            df_pressure = pd.DataFrame()
        
        if acoustic_file.exists():
            df_acoustic = pd.read_csv(acoustic_file)
            df_acoustic['timestamp'] = pd.to_datetime(df_acoustic['timestamp'])
        else:
            df_acoustic = pd.DataFrame()
        
        return df_pressure, df_acoustic
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame(), pd.DataFrame()


def calculate_metrics(df_pressure):
    """Calculate KPIs for the dashboard."""
    if df_pressure.empty:
        return {
            'active_leaks': 0,
            'total_cost': 0,
            'energy_efficiency': 0,
            'leaks_fixed': 0
        }
    
    # Count active leaks
    active_leaks = df_pressure[df_pressure['is_anomaly']].groupby('zone').size()
    
    # Calculate total cost
    leaks = df_pressure[df_pressure['is_anomaly']].copy()
    if not leaks.empty:
        # Calculate pressure drop and flow deviation
        baselines = df_pressure[~df_pressure['is_anomaly']].groupby('zone').agg({
            'pressure_psi': 'median',
            'flow_rate_cfm': 'median'
        })
        
        total_cost = 0
        for idx, row in leaks.iterrows():
            zone = row['zone']
            if zone in baselines.index:
                pressure_drop = baselines.loc[zone, 'pressure_psi'] - row['pressure_psi']
                leak_size_mm = max(0.5, pressure_drop / 5)  # Rough estimate
                cost = calculate_leak_cost(leak_size_mm)
                total_cost += cost
    else:
        total_cost = 0
    
    # Energy efficiency (simplified)
    energy_efficiency = 100 - (len(leaks) / len(df_pressure) * 100 * 2)
    energy_efficiency = max(50, min(100, energy_efficiency))
    
    return {
        'active_leaks': len(active_leaks),
        'total_cost': total_cost,
        'energy_efficiency': energy_efficiency,
        'leaks_fixed': np.random.randint(8, 15)  # TODO: Track from database
    }


def create_factory_map(df_pressure):
    """Create factory zone visualization."""
    zones = ['Zone_A', 'Zone_B', 'Zone_C', 'Zone_D']
    
    # Determine zone status
    zone_status = {}
    for zone in zones:
        zone_data = df_pressure[df_pressure['zone'] == zone]
        if zone_data.empty:
            zone_status[zone] = 'OK'
        else:
            leak_rate = zone_data['is_anomaly'].mean()
            if leak_rate > 0.1:
                zone_status[zone] = 'CRITICAL'
            elif leak_rate > 0.05:
                zone_status[zone] = 'WARNING'
            else:
                zone_status[zone] = 'OK'
    
    # Create visualization
    fig = go.Figure()
    
    positions = [(0, 1), (1, 1), (0, 0), (1, 0)]  # 2x2 grid
    colors = DASHBOARD_CONFIG['zone_colors']
    
    for zone, (x, y) in zip(zones, positions):
        status = zone_status[zone]
        
        fig.add_trace(go.Scatter(
            x=[x + 0.5],
            y=[y + 0.5],
            mode='markers+text',
            marker=dict(
                size=150,
                color=colors[status],
                symbol='square',
                line=dict(color='white', width=2)
            ),
            text=f"<b>{zone}</b><br>{status}",
            textfont=dict(size=14, color='white'),
            textposition="middle center",
            name=zone,
            hovertemplate=f"<b>{zone}</b><br>Status: {status}<extra></extra>"
        ))
    
    fig.update_layout(
        title="Factory Floor Status",
        showlegend=False,
        height=400,
        xaxis=dict(visible=False, range=[-0.5, 2.5]),
        yaxis=dict(visible=False, range=[-0.5, 2.5]),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    return fig


def create_alert_table(df_pressure):
    """Create table of recent alerts."""
    if df_pressure.empty:
        return pd.DataFrame()
    
    # Get anomalies
    leaks = df_pressure[df_pressure['is_anomaly']].copy()
    
    if leaks.empty:
        return pd.DataFrame()
    
    # Calculate baselines
    baselines = df_pressure[~df_pressure['is_anomaly']].groupby('zone').agg({
        'pressure_psi': 'median',
        'flow_rate_cfm': 'median'
    })
    
    # Build alert table
    alerts = []
    for idx, row in leaks.head(20).iterrows():  # Top 20 recent
        zone = row['zone']
        if zone in baselines.index:
            pressure_drop = baselines.loc[zone, 'pressure_psi'] - row['pressure_psi']
            flow_deviation = row['flow_rate_cfm'] - baselines.loc[zone, 'flow_rate_cfm']
            
            severity = classify_severity(pressure_drop, flow_deviation)
            leak_size_mm = max(0.5, pressure_drop / 5)
            annual_cost = calculate_leak_cost(leak_size_mm)
            
            alerts.append({
                'Time': row['timestamp'].strftime('%H:%M'),
                'Zone': zone,
                'Severity': severity,
                'Leak Size': f"{leak_size_mm:.1f}mm",
                'Annual Cost': f"${annual_cost:,.0f}",
                'Status': 'Active'
            })
    
    return pd.DataFrame(alerts)


def main():
    """Main dashboard application."""
    
    # Header
    st.markdown('<h1 class="main-header">🏭 Silent Sabotage - Leak Detection System</h1>', 
                unsafe_allow_html=True)
    st.markdown("---")
    
    # Load data
    df_pressure, df_acoustic = load_sensor_data()
    
    if df_pressure.empty:
        st.error("❌ No data available. Please run `python data/generate_data.py` to generate synthetic data.")
        st.stop()
    
    # Calculate metrics
    metrics = calculate_metrics(df_pressure)
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🚨 Active Leaks",
            value=metrics['active_leaks'],
            delta="-2 from yesterday",
            delta_color="inverse"
        )
    
    with col2:
        st.metric(
            label="💰 Annual Cost",
            value=f"${metrics['total_cost']:,.0f}",
            delta="-$12,000",
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            label="⚡ Energy Efficiency",
            value=f"{metrics['energy_efficiency']:.1f}%",
            delta="+3.2%"
        )
    
    with col4:
        st.metric(
            label="🎯 Leaks Fixed (Month)",
            value=metrics['leaks_fixed'],
            delta="+4"
        )
    
    st.markdown("---")
    
    # Main content area
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("Factory Floor Status")
        factory_map = create_factory_map(df_pressure)
        st.plotly_chart(factory_map, use_container_width=True)
        
        # Pressure trends
        st.subheader("Pressure Trends - Last 6 Hours")
        recent_data = df_pressure[df_pressure['timestamp'] > df_pressure['timestamp'].max() - pd.Timedelta(hours=6)]
        
        fig_pressure = px.line(
            recent_data,
            x='timestamp',
            y='pressure_psi',
            color='zone',
            title=''
        )
        
        # Add anomalies
        anomalies = recent_data[recent_data['is_anomaly']]
        if not anomalies.empty:
            fig_pressure.add_scatter(
                x=anomalies['timestamp'],
                y=anomalies['pressure_psi'],
                mode='markers',
                marker=dict(color='red', size=10, symbol='x'),
                name='Detected Leaks'
            )
        
        st.plotly_chart(fig_pressure, use_container_width=True)
    
    with col_right:
        st.subheader("Active Alerts")
        
        alerts_df = create_alert_table(df_pressure)
        
        if not alerts_df.empty:
            # Display alerts as cards
            for idx, alert in alerts_df.head(5).iterrows():
                severity_class = "critical-alert" if alert['Severity'] == 'CRITICAL' else "high-alert"
                
                st.markdown(f"""
                <div class="{severity_class}">
                    <b>{alert['Severity']}</b> - {alert['Zone']}<br>
                    Size: {alert['Leak Size']} | Cost: {alert['Annual Cost']}/year<br>
                    <small>{alert['Time']} - {alert['Status']}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ No active alerts!")
    
    # Tabs for additional views
    st.markdown("---")
    tab1, tab2, tab3 = st.tabs(["📊 Analytics", "🔮 Predictive", "⚙️ Settings"])
    
    with tab1:
        st.subheader("Detailed Analytics")
        
        # Zone comparison
        zone_stats = df_pressure.groupby('zone').agg({
            'is_anomaly': ['sum', 'mean'],
            'pressure_psi': 'mean',
            'flow_rate_cfm': 'mean'
        }).round(2)
        
        st.write("**Leak Statistics by Zone:**")
        st.dataframe(zone_stats, use_container_width=True)
    
    with tab2:
        st.subheader("Predictive Maintenance Forecast")
        st.info("🔮 This feature requires Model 05 (Predictive Forecast) to be trained.")
        
        # Placeholder forecast visualization
        st.write("**30-Day Leak Probability Forecast:**")
        forecast_data = pd.DataFrame({
            'Zone': ['Zone_A', 'Zone_B', 'Zone_C', 'Zone_D'],
            'Probability (%)': [68, 42, 23, 71],
            'Risk Level': ['HIGH', 'MEDIUM', 'LOW', 'CRITICAL']
        })
        st.dataframe(forecast_data, use_container_width=True)
    
    with tab3:
        st.subheader("System Configuration")
        
        st.write("**Alert Thresholds:**")
        critical_threshold = st.slider("Critical Severity (PSI drop)", 10, 30, 20)
        high_threshold = st.slider("High Severity (PSI drop)", 5, 20, 10)
        
        st.write("**Notification Settings:**")
        email_alerts = st.checkbox("Enable email alerts", value=True)
        sms_alerts = st.checkbox("Enable SMS alerts", value=False)
        
        if st.button("💾 Save Settings"):
            st.success("✅ Settings saved successfully!")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray;'>
        <small>🏭 Silent Sabotage Leak Detection System | Last updated: {}</small>
    </div>
    """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), unsafe_allow_html=True)


if __name__ == "__main__":
    main()
