import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Ohio Commercial Truck Safety — Rumpke Analysis",
    page_icon="🚛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CUSTOM CSS
# ============================================================
st.markdown("""
<style>
    .main { background-color: #0a0c0f; }
    .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    .metric-card {
        background: #111418;
        border: 1px solid #1f2530;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    .alert-box {
        background: rgba(255,59,59,0.08);
        border: 1px solid rgba(255,59,59,0.3);
        border-left: 4px solid #ff3b3b;
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 24px;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #111418;
        border-radius: 8px;
        color: #6b7280;
        border: 1px solid #1f2530;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1f2530;
        color: white;
    }
    div[data-testid="metric-container"] {
        background: #111418;
        border: 1px solid #1f2530;
        border-radius: 12px;
        padding: 16px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# LOAD DATA
# ============================================================
@st.cache_data
def load_data():
    # Load combined 2019-2026 MCMIS sheet
    df = pd.read_excel("OH_crash_260327.xlsx", sheet_name="OH 2019 - 2026 MCMIS")
    df['Crash Date'] = pd.to_datetime(df['Crash Date'], errors='coerce')
    df['Is_Rumpke'] = df['Carrier Name'].str.contains('Rumpke', case=False, na=False)
    # Rumpke territory counties
    df['Is_Rumpke_Territory'] = df['County Name'].isin([
        'Hamilton', 'Butler', 'Clermont', 'Warren', 'Montgomery',
        'Clark', 'Greene', 'Franklin', 'Delaware', 'Licking'
    ])
    return df

df = load_data()
rumpke_df = df[df['Is_Rumpke']].copy()
ohio_df = df.copy()

# ============================================================
# SIDEBAR FILTERS
# ============================================================
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Rumpke_logo.svg/320px-Rumpke_logo.svg.png", width=180)
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔧 Filters")

years = sorted(df['Crash Year'].dropna().unique().astype(int).tolist())
selected_years = st.sidebar.multiselect("Crash Year", years, default=[2022, 2023, 2024, 2025])

weather_opts = df['Weather Condition Desc'].dropna().unique().tolist()
selected_weather = st.sidebar.multiselect("Weather Condition", weather_opts, default=weather_opts)

truck_only = st.sidebar.checkbox("Trucks Only (exclude buses)", value=True)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📍 Focus Area")
focus = st.sidebar.radio("View", ["All Ohio", "Rumpke Territory Only", "Rumpke Vehicles Only"])

st.sidebar.markdown("---")
st.sidebar.markdown("""
**Data Source**  
FMCSA MCMIS Crash File  
Ohio 2019–2026  
Updated: March 27, 2026  
[fmcsa.dot.gov](https://www.fmcsa.dot.gov)
""")

# ============================================================
# APPLY FILTERS
# ============================================================
filtered = df.copy()
if selected_years:
    filtered = filtered[filtered['Crash Year'].isin(selected_years)]
if selected_weather:
    filtered = filtered[filtered['Weather Condition Desc'].isin(selected_weather)]
if truck_only:
    filtered = filtered[filtered['Truck Bus Indicator'] == 'Truck']
if focus == "Rumpke Territory Only":
    filtered = filtered[filtered['Is_Rumpke_Territory']]
elif focus == "Rumpke Vehicles Only":
    filtered = filtered[filtered['Is_Rumpke']]

rumpke_filtered = filtered[filtered['Is_Rumpke']]

# ============================================================
# HEADER
# ============================================================
st.markdown("""
<div style='margin-bottom:8px'>
    <h1 style='color:white;font-size:28px;margin:0'>🚛 Ohio Commercial Truck Crash Intelligence</h1>
    <p style='color:#6b7280;font-size:14px;margin:4px 0 0 0'>
        FMCSA MCMIS Data · 2019–2026 · Rumpke Waste & Recycling Focus
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class='alert-box'>
    <strong style='color:#ff3b3b'>📊 Key Finding:</strong>
    <span style='color:#9ca3af'> Rumpke vehicles were involved in <strong style='color:white'>{len(rumpke_df):,} crashes</strong> 
    across Ohio from 2019–2026, with <strong style='color:white'>{rumpke_df['Fatalities'].sum()} fatalities</strong> and 
    <strong style='color:white'>{rumpke_df['Injuries'].sum():,} injuries</strong>. 
    Hamilton County accounts for the highest concentration of Rumpke crashes — directly tied to their Cincinnati HQ operations.</span>
</div>
""", unsafe_allow_html=True)

# ============================================================
# KPI ROW
# ============================================================
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Crashes (Filtered)", f"{len(filtered):,}")
k2.metric("Rumpke Crashes", f"{len(rumpke_filtered):,}", f"{round(len(rumpke_filtered)/len(filtered)*100,1)}% of total" if len(filtered) > 0 else "")
k3.metric("Fatalities", f"{int(filtered['Fatalities'].sum()):,}")
k4.metric("Injuries", f"{int(filtered['Injuries'].sum()):,}")
k5.metric("Rumpke Fatalities", f"{int(rumpke_filtered['Fatalities'].sum())}", delta_color="inverse")

st.markdown("---")

# ============================================================
# TABS
# ============================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📍 County Hotspots",
    "📅 Trends Over Time",
    "☁️ Weather & Conditions",
    "🚛 Rumpke Deep Dive",
    "💡 Recommendations"
])

# ============================================================
# TAB 1 — COUNTY HOTSPOTS
# ============================================================
with tab1:
    st.subheader("County-Level Crash Concentration")
    col1, col2 = st.columns([1.5, 1])

    with col1:
        county_crashes = filtered.groupby('County Name').agg(
            crashes=('Crash ID', 'count'),
            fatalities=('Fatalities', 'sum'),
            injuries=('Injuries', 'sum'),
            rumpke_crashes=('Is_Rumpke', 'sum')
        ).reset_index().sort_values('crashes', ascending=False)

        fig = px.bar(
            county_crashes.head(20),
            x='County Name', y='crashes',
            color='rumpke_crashes',
            color_continuous_scale=['#1f2530', '#ff3b3b'],
            title='Top 20 Ohio Counties by Commercial Truck Crashes',
            labels={'crashes': 'Total Crashes', 'rumpke_crashes': 'Rumpke Crashes'},
            template='plotly_dark'
        )
        fig.update_layout(
            plot_bgcolor='#111418', paper_bgcolor='#111418',
            font_color='#9ca3af', title_font_color='white',
            coloraxis_colorbar=dict(title="Rumpke<br>Crashes")
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Rumpke Territory Counties")
        rumpke_territory = county_crashes[county_crashes['County Name'].isin([
            'Hamilton', 'Butler', 'Clermont', 'Warren', 'Montgomery',
            'Clark', 'Greene', 'Franklin', 'Delaware', 'Licking'
        ])].sort_values('rumpke_crashes', ascending=False)

        for _, row in rumpke_territory.iterrows():
            pct = round(row['rumpke_crashes']/row['crashes']*100, 1) if row['crashes'] > 0 else 0
            color = '#ff3b3b' if pct > 5 else '#f59e0b' if pct > 2 else '#22c55e'
            st.markdown(f"""
            <div style='background:#111418;border:1px solid #1f2530;border-radius:8px;
                        padding:10px 14px;margin-bottom:8px;'>
                <div style='display:flex;justify-content:space-between;align-items:center'>
                    <span style='color:white;font-weight:500'>{row['County Name']}</span>
                    <span style='color:{color};font-family:monospace;font-size:12px'>
                        {int(row['rumpke_crashes'])} Rumpke / {int(row['crashes'])} total
                    </span>
                </div>
                <div style='background:#1f2530;border-radius:4px;height:4px;margin-top:6px'>
                    <div style='background:{color};width:{min(pct*5,100)}%;height:4px;border-radius:4px'></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Severity by county
    st.markdown("#### Crash Severity by County (Top 15)")
    county_sev = filtered[filtered['Fatalities'] > 0].groupby('County Name')['Fatalities'].sum().reset_index()
    county_sev = county_sev.sort_values('Fatalities', ascending=False).head(15)
    fig2 = px.bar(
        county_sev, x='County Name', y='Fatalities',
        color='Fatalities', color_continuous_scale=['#f59e0b', '#ff3b3b'],
        title='Fatal Commercial Truck Crashes by County',
        template='plotly_dark'
    )
    fig2.update_layout(plot_bgcolor='#111418', paper_bgcolor='#111418',
                       font_color='#9ca3af', title_font_color='white')
    st.plotly_chart(fig2, use_container_width=True)

# ============================================================
# TAB 2 — TRENDS OVER TIME
# ============================================================
with tab2:
    st.subheader("Crash Trends Over Time")

    col1, col2 = st.columns(2)

    with col1:
        yearly = filtered.groupby('Crash Year').agg(
            crashes=('Crash ID', 'count'),
            fatalities=('Fatalities', 'sum'),
            injuries=('Injuries', 'sum')
        ).reset_index()
        yearly_rumpke = rumpke_df.groupby('Crash Year').agg(
            rumpke_crashes=('Crash ID', 'count')
        ).reset_index()
        yearly = yearly.merge(yearly_rumpke, on='Crash Year', how='left').fillna(0)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=yearly['Crash Year'], y=yearly['crashes'],
            name='All Ohio Trucks', line=dict(color='#3b82f6', width=2),
            fill='tozeroy', fillcolor='rgba(59,130,246,0.1)'
        ))
        fig.add_trace(go.Scatter(
            x=yearly['Crash Year'], y=yearly['rumpke_crashes'],
            name='Rumpke Only', line=dict(color='#ff3b3b', width=2),
            fill='tozeroy', fillcolor='rgba(255,59,59,0.15)'
        ))
        fig.update_layout(
            title='Annual Crash Volume — Ohio Trucks vs Rumpke',
            plot_bgcolor='#111418', paper_bgcolor='#111418',
            font_color='#9ca3af', title_font_color='white',
            legend=dict(bgcolor='#111418', bordercolor='#1f2530'),
            template='plotly_dark'
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        dow = filtered.groupby('Day of Week Category')['Crash ID'].count().reset_index()
        dow.columns = ['Day', 'Crashes']
        day_order = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        dow['Day'] = pd.Categorical(dow['Day'], categories=day_order, ordered=True)
        dow = dow.sort_values('Day')
        fig2 = px.bar(
            dow, x='Day', y='Crashes',
            color='Crashes', color_continuous_scale=['#1f2530', '#f59e0b'],
            title='Crashes by Day of Week',
            template='plotly_dark'
        )
        fig2.update_layout(plot_bgcolor='#111418', paper_bgcolor='#111418',
                           font_color='#9ca3af', title_font_color='white')
        st.plotly_chart(fig2, use_container_width=True)

    # Time of Day
    tod = filtered.groupby('Time of Day Category')['Crash ID'].count().reset_index()
    tod.columns = ['Time of Day', 'Crashes']
    tod = tod.sort_values('Crashes', ascending=False)
    fig3 = px.bar(
        tod, x='Time of Day', y='Crashes',
        color='Crashes', color_continuous_scale=['#1f2530', '#ff3b3b'],
        title='Crashes by Time of Day',
        template='plotly_dark'
    )
    fig3.update_layout(plot_bgcolor='#111418', paper_bgcolor='#111418',
                       font_color='#9ca3af', title_font_color='white')
    st.plotly_chart(fig3, use_container_width=True)

# ============================================================
# TAB 3 — WEATHER & CONDITIONS
# ============================================================
with tab3:
    st.subheader("Weather & Road Condition Analysis")
    col1, col2 = st.columns(2)

    with col1:
        weather = filtered.groupby('Weather Condition Desc').agg(
            crashes=('Crash ID', 'count'),
            fatalities=('Fatalities', 'sum')
        ).reset_index().sort_values('crashes', ascending=False)
        fig = px.pie(
            weather, values='crashes', names='Weather Condition Desc',
            title='Crash Distribution by Weather',
            color_discrete_sequence=px.colors.sequential.RdBu,
            template='plotly_dark'
        )
        fig.update_layout(plot_bgcolor='#111418', paper_bgcolor='#111418',
                          font_color='#9ca3af', title_font_color='white')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        road = filtered.groupby('Road Surface Condition Desc').agg(
            crashes=('Crash ID', 'count'),
            fatalities=('Fatalities', 'sum')
        ).reset_index().sort_values('crashes', ascending=False)
        fig2 = px.bar(
            road, x='crashes', y='Road Surface Condition Desc',
            orientation='h',
            color='fatalities', color_continuous_scale=['#1f2530', '#ff3b3b'],
            title='Crashes by Road Surface Condition',
            template='plotly_dark'
        )
        fig2.update_layout(plot_bgcolor='#111418', paper_bgcolor='#111418',
                           font_color='#9ca3af', title_font_color='white')
        st.plotly_chart(fig2, use_container_width=True)

    # Light conditions
    light = filtered.groupby('Light Condition Desc').agg(
        crashes=('Crash ID', 'count'),
        fatalities=('Fatalities', 'sum')
    ).reset_index().sort_values('crashes', ascending=False)
    fig3 = px.bar(
        light, x='Light Condition Desc', y='crashes',
        color='fatalities', color_continuous_scale=['#1f2530', '#ff3b3b'],
        title='Crashes by Light Condition (darker = more fatal)',
        template='plotly_dark'
    )
    fig3.update_layout(plot_bgcolor='#111418', paper_bgcolor='#111418',
                       font_color='#9ca3af', title_font_color='white')
    st.plotly_chart(fig3, use_container_width=True)

# ============================================================
# TAB 4 — RUMPKE DEEP DIVE
# ============================================================
with tab4:
    st.subheader("🚛 Rumpke Crash Deep Dive — 2019 to 2026")

    st.markdown(f"""
    <div class='alert-box'>
        <strong style='color:#ff3b3b'>Rumpke-Specific Finding:</strong>
        <span style='color:#9ca3af'> Rumpke vehicles were involved in <strong style='color:white'>{len(rumpke_df):,} crashes</strong> 
        across Ohio from 2019 to 2026. Of these, <strong style='color:white'>{rumpke_df['Fatalities'].sum()} resulted in fatalities</strong>. 
        Hamilton County had the most Rumpke crashes — consistent with their Cincinnati headquarters and highest driver density.</span>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        rumpke_county = rumpke_df.groupby('County Name').agg(
            crashes=('Crash ID', 'count'),
            fatalities=('Fatalities', 'sum'),
            injuries=('Injuries', 'sum')
        ).reset_index().sort_values('crashes', ascending=False).head(15)
        fig = px.bar(
            rumpke_county, x='County Name', y='crashes',
            color='fatalities', color_continuous_scale=['#3b82f6', '#ff3b3b'],
            title='Rumpke Crashes by County (color = fatalities)',
            template='plotly_dark'
        )
        fig.update_layout(plot_bgcolor='#111418', paper_bgcolor='#111418',
                          font_color='#9ca3af', title_font_color='white')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        rumpke_year = rumpke_df.groupby('Crash Year').agg(
            crashes=('Crash ID', 'count'),
            fatalities=('Fatalities', 'sum'),
            injuries=('Injuries', 'sum')
        ).reset_index()
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=rumpke_year['Crash Year'], y=rumpke_year['crashes'],
            name='Crashes', marker_color='#3b82f6'
        ))
        fig2.add_trace(go.Scatter(
            x=rumpke_year['Crash Year'], y=rumpke_year['injuries'],
            name='Injuries', line=dict(color='#f59e0b', width=2),
            yaxis='y2'
        ))
        fig2.update_layout(
            title='Rumpke Annual Crashes & Injuries',
            yaxis=dict(title='Crashes'),
            yaxis2=dict(title='Injuries', overlaying='y', side='right'),
            plot_bgcolor='#111418', paper_bgcolor='#111418',
            font_color='#9ca3af', title_font_color='white',
            legend=dict(bgcolor='#111418'),
            template='plotly_dark'
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Rumpke weather
    rumpke_weather = rumpke_df.groupby('Weather Condition Desc')['Crash ID'].count().reset_index()
    rumpke_weather.columns = ['Weather', 'Rumpke Crashes']
    rumpke_weather = rumpke_weather.sort_values('Rumpke Crashes', ascending=False)
    fig3 = px.bar(
        rumpke_weather, x='Weather', y='Rumpke Crashes',
        color='Rumpke Crashes', color_continuous_scale=['#1f2530', '#ff3b3b'],
        title='Rumpke Crashes by Weather Condition',
        template='plotly_dark'
    )
    fig3.update_layout(plot_bgcolor='#111418', paper_bgcolor='#111418',
                       font_color='#9ca3af', title_font_color='white')
    st.plotly_chart(fig3, use_container_width=True)

    # Raw data table
    st.markdown("#### Recent Rumpke Crashes (2024–2026)")
    recent = rumpke_df[rumpke_df['Crash Year'] >= 2024][[
        'Crash Year', 'Crash Date', 'County Name', 'City',
        'Fatalities', 'Injuries', 'Weather Condition Desc',
        'Light Condition Desc', 'Road Surface Condition Desc'
    ]].sort_values('Crash Date', ascending=False)
    st.dataframe(recent, use_container_width=True, height=300)

# ============================================================
# TAB 5 — RECOMMENDATIONS
# ============================================================
with tab5:
    st.subheader("💡 Data-Driven Safety Recommendations for Rumpke")

    st.markdown("""
    <div class='alert-box'>
        <strong style='color:#ff3b3b'>Analyst Note:</strong>
        <span style='color:#9ca3af'> The following recommendations are derived directly from FMCSA MCMIS crash data 
        (2019–2026) for Ohio commercial truck operations, with specific focus on Rumpke vehicle crash patterns. 
        These complement the OSHA facility injury analysis in Project 1.</span>
    </div>
    """, unsafe_allow_html=True)

    recs = [
        {
            "tag": "🔴 URGENT",
            "color": "#ff3b3b",
            "title": "Hamilton County Route Safety Program",
            "body": f"""Hamilton County has the highest concentration of Rumpke crashes in Ohio 
            ({rumpke_df[rumpke_df['County Name']=='Hamilton']['Crash ID'].count()} crashes 2019–2026). 
            As Rumpke's Cincinnati HQ and highest driver density county, this requires a dedicated 
            route-level safety audit — identifying specific intersections, roads, and time windows 
            where incidents cluster. Recommend overlaying Netradyne driver event data with these crash 
            locations to identify systemic patterns."""
        },
        {
            "tag": "🟡 HIGH PRIORITY",
            "color": "#f59e0b",
            "title": "Adverse Weather Driver Protocol — Snow & Rain Response",
            "body": f"""Of Rumpke's {len(rumpke_df):,} Ohio crashes, a significant share occurred 
            during rain and snow conditions. Ohio winters are severe and collection routes don't stop 
            for weather. Recommend developing a weather-triggered safety protocol: when snow/ice 
            conditions are forecasted, automatically reduce route speeds, increase following-distance 
            alerts in Netradyne, and trigger pre-shift safety briefings at affected depots."""
        },
        {
            "tag": "🔵 STRATEGIC",
            "color": "#3b82f6",
            "title": "2026 New Facility Crash Risk Pre-Assessment",
            "body": f"""Rumpke is opening facilities in Clark County (depot), Union Township (Clermont), 
            and Zanesville in 2026. FMCSA data shows Clark County has existing commercial truck crash 
            patterns that new Rumpke routes will intersect. Recommend conducting a pre-opening route 
            risk assessment for each new facility using this crash data — identifying high-risk 
            intersections before drivers encounter them."""
        },
        {
            "tag": "🔵 STRATEGIC",
            "color": "#3b82f6",
            "title": "Connect FMCSA Crash Data to Netradyne Safety Scores",
            "body": """Currently, Rumpke's Netradyne system tracks driver behavior (harsh braking, 
            speeding, distraction) but this data lives separately from external crash records. 
            By integrating FMCSA crash location data with Netradyne route data, Rumpke can identify 
            which specific road segments are both high-crash AND high-driver-event — creating a 
            predictive risk map that flags dangerous routes before an incident occurs. 
            This is the next evolution of their safety intelligence infrastructure."""
        }
    ]

    for rec in recs:
        st.markdown(f"""
        <div style='background:#111418;border:1px solid #1f2530;border-radius:12px;
                    padding:24px;margin-bottom:16px;'>
            <div style='display:inline-block;background:rgba(255,255,255,0.05);
                        border:1px solid {rec["color"]}33;border-radius:20px;
                        padding:3px 12px;margin-bottom:10px;
                        font-size:11px;font-family:monospace;color:{rec["color"]}'>
                {rec["tag"]}
            </div>
            <h3 style='color:white;margin:0 0 10px 0;font-size:18px'>{rec["title"]}</h3>
            <p style='color:#9ca3af;line-height:1.7;margin:0'>{rec["body"]}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style='text-align:center;color:#6b7280;font-size:12px;font-family:monospace'>
        Data: FMCSA MCMIS Ohio Crash Records 2019–2026 · Snapshot: March 27, 2026<br>
        Built for: Rumpke Safety Data Analyst Application · Rumpke Waste & Recycling · Cincinnati, OH
    </div>
    """, unsafe_allow_html=True)
