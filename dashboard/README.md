# 🏭 Leak Detection Dashboard

**Team Member:** ___________  
**Priority:** ✅ Must Have  
**Estimated Time:** 3-4 hours  
**Status:** 🔴 Not Started

## 📋 Your Task

Build an **interactive Streamlit dashboard** to visualize the leak detection system in action.

## 🎯 What It Does

This is what the **judges will see** during your demo:
- Real-time factory status overview
- Zone-based leak visualization
- Alert management system
- Energy efficiency metrics
- Predictive maintenance forecast (if Model 05 is ready)

**The dashboard SELLS your solution. Make it impressive!**

## 🖥️ Dashboard Structure

```
┌─────────────────────────────────────────────┐
│  🏭 Silent Sabotage - Leak Detection System │
│                                             │
│  ┌───────────┬───────────┬───────────┐     │
│  │ Active    │ Energy    │ Annual    │     │
│  │ Leaks: 5  │ Loss: 12% │ Cost: $85K│     │
│  └───────────┴───────────┴───────────┘     │
│                                             │
│  Factory Floor Map:                         │
│  ┌─────────────────────────────────┐       │
│  │   [Zone A: OK]    [Zone B: ⚠️ ]  │       │
│  │                                 │       │
│  │   [Zone C: 🔴]    [Zone D: OK]  │       │
│  └─────────────────────────────────┘       │
│                                             │
│  Active Alerts:                             │
│  🔴 CRITICAL - Zone C - Leak #003 - $18K/yr│
│  ⚠️  HIGH     - Zone B - Leak #007 - $12K/yr│
│                                             │
│  [Tabs: Overview | Alerts | Analytics |    │
│         Predictive | Settings]              │
└─────────────────────────────────────────────┘
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
# If not already synced
uv sync

# Or add packages if needed
# uv add streamlit plotly
```

### 2. Run the Dashboard
```bash
streamlit run app.py
```

### 3. Open Browser
```
Local URL: http://localhost:8501
```

## 📁 File Structure

```
dashboard/
├── app.py                    # Main dashboard application
├── pages/
│   ├── 1_Overview.py         # Factory overview
│   ├── 2_Alerts.py           # Alert management
│   ├── 3_Analytics.py        # Detailed analytics
│   ├── 4_Predictive.py       # Forecast visualization
│   └── 5_Settings.py         # Configuration
├── components/
│   ├── factory_map.py        # Zone visualization
│   ├── metrics.py            # KPI cards
│   └── charts.py             # Reusable charts
├── utils/
│   ├── data_loader.py        # Load model outputs
│   └── styling.py            # CSS and themes
└── README.md                 # This file
```

## 🎨 Key Components

### 1. **KPI Cards (Top of Dashboard)**

```python
import streamlit as st

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="🚨 Active Leaks",
        value=5,
        delta=-2,  # -2 from yesterday
        delta_color="inverse"  # Red for positive, green for negative
    )

with col2:
    st.metric(
        label="💰 Annual Cost",
        value="$85,200",
        delta="-$12,000"
    )

with col3:
    st.metric(
        label="⚡ Energy Efficiency",
        value="71%",
        delta="+3%"
    )

with col4:
    st.metric(
        label="🎯 Leaks Fixed This Month",
        value=12,
        delta="+4"
    )
```

### 2. **Factory Zone Map**

```python
import plotly.graph_objects as go

# Create 2x2 grid representing factory zones
zones = ['Zone_A', 'Zone_B', 'Zone_C', 'Zone_D']
zone_status = ['OK', 'WARNING', 'CRITICAL', 'OK']
zone_colors = {
    'OK': '#28a745',
    'WARNING': '#ffc107',
    'CRITICAL': '#dc3545'
}

fig = go.Figure()

# Add rectangles for each zone
positions = [(0, 1), (1, 1), (0, 0), (1, 0)]  # (x, y) for 2x2 grid

for zone, status, (x, y) in zip(zones, zone_status, positions):
    fig.add_trace(go.Scatter(
        x=[x + 0.5],
        y=[y + 0.5],
        mode='markers+text',
        marker=dict(
            size=100,
            color=zone_colors[status],
            symbol='square'
        ),
        text=f"{zone}<br>{status}",
        textposition="middle center",
        name=zone
    ))

fig.update_layout(
    title="Factory Floor Status",
    showlegend=False,
    height=400,
    xaxis=dict(visible=False),
    yaxis=dict(visible=False)
)

st.plotly_chart(fig, use_container_width=True)
```

### 3. **Alert Table**

```python
import pandas as pd

alerts = pd.DataFrame({
    'Time': ['10:30', '09:15', '08:45', '07:20'],
    'Zone': ['Zone_C', 'Zone_B', 'Zone_C', 'Zone_A'],
    'Severity': ['CRITICAL', 'HIGH', 'HIGH', 'MEDIUM'],
    'Leak Size': ['4.2mm', '2.8mm', '3.1mm', '1.5mm'],
    'Annual Cost': ['$18,500', '$12,200', '$14,800', '$4,200'],
    'Status': ['Active', 'Active', 'Investigating', 'Scheduled']
})

# Color code severity
def highlight_severity(row):
    colors = {
        'CRITICAL': 'background-color: #dc3545; color: white',
        'HIGH': 'background-color: #ffc107',
        'MEDIUM': 'background-color: #17a2b8; color: white',
        'LOW': 'background-color: #28a745; color: white'
    }
    return [colors.get(row['Severity'], '')] * len(row)

st.dataframe(
    alerts.style.apply(highlight_severity, axis=1),
    use_container_width=True
)
```

### 4. **Pressure Trend Chart**

```python
import plotly.express as px

# Load pressure data
pressure_data = pd.read_csv('data/raw/pressure_sensor_data.csv')
pressure_data['timestamp'] = pd.to_datetime(pressure_data['timestamp'])

# Filter to recent data (last 24 hours)
recent_data = pressure_data[pressure_data['timestamp'] > pd.Timestamp.now() - pd.Timedelta(hours=24)]

fig = px.line(
    recent_data,
    x='timestamp',
    y='pressure_psi',
    color='zone',
    title='Pressure Trends - Last 24 Hours'
)

# Add horizontal line for normal pressure
fig.add_hline(y=125, line_dash="dash", line_color="green", annotation_text="Normal")

# Highlight anomalies
anomalies = recent_data[recent_data['is_anomaly']]
fig.add_scatter(
    x=anomalies['timestamp'],
    y=anomalies['pressure_psi'],
    mode='markers',
    marker=dict(color='red', size=10, symbol='x'),
    name='Detected Leaks'
)

st.plotly_chart(fig, use_container_width=True)
```

### 5. **Energy Efficiency Gauge**

```python
fig = go.Figure(go.Indicator(
    mode="gauge+number+delta",
    value=71,
    domain={'x': [0, 1], 'y': [0, 1]},
    title={'text': "Energy Efficiency Score"},
    delta={'reference': 90, 'suffix': " (Industry Best)"},
    gauge={
        'axis': {'range': [None, 100]},
        'bar': {'color': "darkblue"},
        'steps': [
            {'range': [0, 50], 'color': "#dc3545"},
            {'range': [50, 75], 'color': "#ffc107"},
            {'range': [75, 100], 'color': "#28a745"}
        ],
        'threshold': {
            'line': {'color': "red", 'width': 4},
            'thickness': 0.75,
            'value': 90
        }
    }
))

st.plotly_chart(fig, use_container_width=True)
```

## 📊 Dashboard Tabs/Pages

### Tab 1: Overview (Main Landing)
- Factory status at a glance
- Zone map
- Top 5 critical alerts
- Energy efficiency score
- Real-time metrics

### Tab 2: Alerts & Incidents
- Complete alert history
- Filterable table (by zone, severity, date)
- Alert details and status
- Maintenance notes
- Export to PDF/Excel

### Tab 3: Analytics & Insights
- Historical trends
- Leak frequency by zone
- Cost analysis
- Pressure gradient visualization
- Sensor health monitoring

### Tab 4: Predictive Maintenance (Model 05)
- 30-day forecast by zone
- Risk heatmap
- Inspection schedule
- Expected savings
- Component failure predictions

### Tab 5: Settings & Configuration
- Threshold adjustments
- Alert notification settings
- Zone configuration
- Model retraining
- Export/import data

## 🎨 Styling & Theme

### Custom CSS:
```python
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1E3A8A;
        text-align: center;
        padding: 1rem;
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
    }
    
    .zone-ok {
        color: #28a745;
        font-weight: bold;
    }
    
    .zone-critical {
        color: #dc3545;
        font-weight: bold;
        animation: blink 1s infinite;
    }
    
    @keyframes blink {
        50% { opacity: 0.5; }
    }
</style>
""", unsafe_allow_html=True)
```

## 🔄 Real-Time Updates

### Auto-refresh every 5 seconds:
```python
import time

# Add auto-refresh
st_autorefresh = st.empty()

refresh_interval = 5  # seconds

while True:
    # Load latest data
    latest_data = load_latest_sensor_data()
    
    # Update dashboard
    with st_autorefresh:
        display_dashboard(latest_data)
    
    time.sleep(refresh_interval)
```

## 💡 Advanced Features

### 1. **Interactive Filters**
```python
# Sidebar filters
st.sidebar.header("Filters")

selected_zones = st.sidebar.multiselect(
    "Select Zones",
    options=['Zone_A', 'Zone_B', 'Zone_C', 'Zone_D'],
    default=['Zone_A', 'Zone_B', 'Zone_C', 'Zone_D']
)

severity_filter = st.sidebar.multiselect(
    "Severity Level",
    options=['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'],
    default=['CRITICAL', 'HIGH']
)

date_range = st.sidebar.date_input(
    "Date Range",
    value=(pd.Timestamp.now() - pd.Timedelta(days=7), pd.Timestamp.now())
)
```

### 2. **Download Reports**
```python
import io

# Generate PDF report
def generate_pdf_report(data):
    # Use reportlab or similar
    pass

if st.button("📥 Download Report"):
    pdf_buffer = generate_pdf_report(alerts)
    st.download_button(
        label="Download PDF",
        data=pdf_buffer,
        file_name="leak_report.pdf",
        mime="application/pdf"
    )
```

### 3. **Model Performance Dashboard**
```python
# Show model metrics
st.subheader("Model Performance")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Isolation Forest Accuracy", "92.3%")
    
with col2:
    st.metric("Acoustic Classifier Accuracy", "88.1%")
    
with col3:
    st.metric("Forecast Precision", "71.2%")
```

## 🐛 Troubleshooting

**Dashboard won't load:**
```bash
# Check Streamlit version
streamlit --version

# Resync dependencies
uv sync

# Or upgrade specific package
uv add streamlit --upgrade
```

**Charts not displaying:**
```bash
uv add plotly --upgrade
```

**"Empty DataFrame" error:**
- Make sure you've run `python data/generate_data.py`
- Check file paths are correct
- Verify CSV files exist in `data/raw/`

**Slow performance:**
- Cache data loading with `@st.cache_data`
- Reduce data points in charts
- Use sampling for large datasets

## 📝 Deliverables

- [ ] Working Streamlit dashboard
- [ ] All tabs/pages implemented
- [ ] Factory zone map visualization
- [ ] Alert management system
- [ ] Analytics charts
- [ ] Predictive maintenance page (if Model 05 ready)
- [ ] Custom styling and branding
- [ ] Screenshot of dashboard for pitch deck

## 🎤 Demo Tips

### For the Hackathon Presentation:

1. **Start with Overview Tab**
   - Show the factory at a glance
   - Point out energy efficiency score

2. **Click on a CRITICAL Zone**
   - "As you can see, Zone C has a critical leak"
   - Show estimated cost: "$18K per year"

3. **Go to Analytics Tab**
   - Show pressure trend dropping
   - "Our model detected this anomaly 2 hours ago"

4. **Switch to Predictive Tab**
   - "Here's where it gets interesting..."
   - "We predict Zone D will develop a leak in 5 days"
   - "Proactive maintenance can save $18K"

5. **End with Impact**
   - "Total detected: $85K in annual losses"
   - "After repairs: Factory efficiency up 12%"

## 🚀 Bonus Features

### 1. **Mobile View**
```python
# Responsive layout
if st.session_state.get('mobile_view', False):
    # Stack components vertically
    pass
```

### 2. **Email Alerts**
```python
import smtplib

def send_alert_email(leak_details):
    # Send email to maintenance team
    pass
```

### 3. **AR View Mockup**
Use an iframe to show a Figma prototype:
```python
st.markdown("""
<iframe 
    src="https://figma.com/embed/..." 
    width="100%" 
    height="600px"
></iframe>
""", unsafe_allow_html=True)
```

---

**Questions?** The dashboard is your DEMO. Make it visual, make it impressive! 🎨
