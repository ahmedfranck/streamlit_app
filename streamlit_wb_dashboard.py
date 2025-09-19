\"\"\"
Streamlit dashboard: World Bank WDI sample dashboard
File: streamlit_wb_dashboard.py
To run:
    pip install streamlit pandas numpy plotly scikit-learn
    streamlit run streamlit_wb_dashboard.py --server.port 8501
\"\"\"

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from io import BytesIO

@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    return df

df = load_data("/mnt/data/WB_WDI_WIDEF.csv")

st.set_page_config(layout="wide", page_title="World Bank WDI Dashboard")

st.title("World Bank WDI — Sample Dashboard")
st.markdown("Interactive dashboard built with Streamlit. Filters on the left.")

# Attempt to identify columns for country, year and indicators
possible_country_cols = [c for c in df.columns if c.lower() in ['country', 'country_name', 'countryname', 'country code', 'iso3c', 'iso2c']]
possible_year_cols = [c for c in df.columns if c.lower() in ['year']]
# Heuristic: find a 'year' column or wide format where years are columns
if 'year' in df.columns.str.lower().tolist() or 'Year' in df.columns:
    year_mode = 'long'
else:
    year_mode = 'wide'

# Try to detect a country column
country_col = None
for c in df.columns:
    if c.lower() in ['country', 'country_name', 'countryname', 'country name', 'country_name ' ,'Country']:
        country_col = c
        break
# Fallback: take the first non-numeric column
if country_col is None:
    for c in df.columns:
        if df[c].dtype == object:
            country_col = c
            break

# Identify numeric indicator columns (exclude country and any 'indicator' textual columns)
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

# Sidebar: filters
st.sidebar.header("Filters")
countries = sorted(df[country_col].dropna().unique().tolist()) if country_col else []
selected_countries = st.sidebar.multiselect("Select countries", countries, default=countries[:5])

# Year selection (if wide, try to detect years as integer-like column names)
year_cols = []
if year_mode == 'wide':
    # pick numeric-like column names (e.g. '1960', '1961', ...)
    for c in df.columns:
        try:
            int(c)
            year_cols.append(int(c))
        except Exception:
            pass
    year_cols = sorted(year_cols)
else:
    if 'Year' in df.columns:
        year_cols = sorted(df['Year'].dropna().unique().astype(int).tolist())
    elif 'year' in df.columns:
        year_cols = sorted(df['year'].dropna().unique().astype(int).tolist())

if year_cols:
    min_y, max_y = min(year_cols), max(year_cols)
    selected_year_range = st.sidebar.slider("Year range", min_value=min_y, max_value=max_y, value=(min_y, max_y))
else:
    selected_year_range = None

# Indicator selectors
indicator_options = numeric_cols
selected_indicator = st.sidebar.selectbox("Primary indicator (time series)", indicator_options, index=0 if indicator_options else None)
x_indicator = st.sidebar.selectbox("X for scatter", indicator_options, index=1 if len(indicator_options) > 1 else 0)
y_indicator = st.sidebar.selectbox("Y for scatter", indicator_options, index=2 if len(indicator_options) > 2 else 0)
heatmap_inds = st.sidebar.multiselect("Indicators for correlation heatmap (up to 12)", indicator_options, default=indicator_options[:6])

# Filter dataframe by selected countries and years (best-effort for wide or long format)
df_f = df.copy()
if country_col:
    if selected_countries:
        df_f = df_f[df_f[country_col].isin(selected_countries)]
if selected_year_range and year_cols:
    if year_mode == 'long':
        if 'Year' in df_f.columns:
            df_f = df_f[(df_f['Year'] >= selected_year_range[0]) & (df_f['Year'] <= selected_year_range[1])]
        elif 'year' in df_f.columns:
            df_f = df_f[(df_f['year'] >= selected_year_range[0]) & (df_f['year'] <= selected_year_range[1])]
    else:
        # For wide mode, we'll melt only the numeric year columns for time-series visuals
        pass

# Main layout: KPIs
kpi1, kpi2, kpi3 = st.columns(3)
if selected_indicator and selected_indicator in df_f.columns:
    series = df_f[selected_indicator].dropna()
    kpi1.metric("Mean", f"{series.mean():,.2f}" if not series.empty else "n/a")
    kpi2.metric("Median", f"{series.median():,.2f}" if not series.empty else "n/a")
    kpi3.metric("Max", f"{series.max():,.2f}" if not series.empty else "n/a")
else:
    kpi1.metric("Mean", "n/a"); kpi2.metric("Median", "n/a"); kpi3.metric("Max", "n/a")

st.markdown("---")

# Time series: if data is long format or we can melt wide-year columns
st.subheader("Time series — Primary indicator")
ts_df = None
if year_mode == 'long' and ('Year' in df.columns or 'year' in df.columns):
    ycol = 'Year' if 'Year' in df.columns else 'year'
    ts_df = df_f[[country_col, ycol, selected_indicator]].dropna()
    ts_df = ts_df.rename(columns={ycol: 'Year'})
else:
    # melt year columns that look numeric
    year_str_cols = [c for c in df.columns if c.isdigit()]
    if year_str_cols:
        ts_df = df_melt = df_f.melt(id_vars=[country_col], value_vars=year_str_cols, var_name='Year', value_name=selected_indicator)
        ts_df['Year'] = ts_df['Year'].astype(int)
        ts_df = ts_df.dropna(subset=[selected_indicator])
if ts_df is not None and not ts_df.empty:
    if selected_year_range:
        ts_df = ts_df[(ts_df['Year'] >= selected_year_range[0]) & (ts_df['Year'] <= selected_year_range[1])]
    fig = px.line(ts_df, x='Year', y=selected_indicator, color=country_col, markers=True, title=f"{selected_indicator} over time")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No time-series data detected for the selected indicator and dataset layout.")

st.markdown("---")

# Scatter with regression
st.subheader("Scatter plot with linear regression") 
scatter_df = df_f[[country_col, x_indicator, y_indicator]].dropna()
if not scatter_df.empty:
    fig_scatter = px.scatter(scatter_df, x=x_indicator, y=y_indicator, hover_data=[country_col], trendline='ols', title=f"{y_indicator} vs {x_indicator}")
    st.plotly_chart(fig_scatter, use_container_width=True)
else:
    st.info("Not enough data to build scatter plot.")

st.markdown("---")

# Heatmap correlation
st.subheader("Correlation heatmap") 
hm_inds = heatmap_inds[:12]
corr_df = df_f[hm_inds].dropna()
if not corr_df.empty and len(hm_inds) >= 2:
    corr = corr_df.corr()
    fig_hm = go.Figure(data=go.Heatmap(z=corr.values, x=corr.columns, y=corr.index, colorbar=dict(title='corr')))
    fig_hm.update_layout(title='Indicator correlation heatmap')
    st.plotly_chart(fig_hm, use_container_width=True)
else:
    st.info("Not enough numeric indicators selected for heatmap.")

st.markdown("---")

# Scatter matrix (pairwise)
st.subheader("Scatter matrix (pairwise)")
if len(hm_inds) >= 2:
    fig_sm = px.scatter_matrix(df_f[hm_inds].dropna().iloc[:1000], dimensions=hm_inds, title='Pairwise scatter matrix (sample up to 1000 rows)')
    st.plotly_chart(fig_sm, use_container_width=True)
else:
    st.info("Select at least 2 indicators for the pairwise chart.")

st.markdown("---")

# Data download
st.subheader("Download filtered data")
csv = df_f.to_csv(index=False).encode('utf-8')
st.download_button(label='Download CSV of filtered data', data=csv, file_name='wdi_filtered.csv', mime='text/csv')

st.markdown("---")
st.caption("This dashboard is a template — tweak indicator choices and layout to fit your storytelling needs.")
