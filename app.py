
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="E‑Mobility Sales & Ops Dashboard", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("sales_ebus_sample.csv", parse_dates=["date"])
    return df

df = load_data()

# Sidebar Filters
st.sidebar.title("Filters")
min_date = df["date"].min()
max_date = df["date"].max()
date_range = st.sidebar.date_input("Date range", [min_date, max_date])

regions = st.sidebar.multiselect("Region", sorted(df["region"].unique()), default=sorted(df["region"].unique()))
countries = st.sidebar.multiselect("Country", sorted(df["country"].unique()))
products = st.sidebar.multiselect("Product", sorted(df["product"].unique()))
reps = st.sidebar.multiselect("Sales rep", sorted(df["sales_rep"].unique()))
channels = st.sidebar.multiselect("Channel", sorted(df["channel"].unique()))
segments = st.sidebar.multiselect("Segment", sorted(df["segment"].unique()))

# Apply filters
mask = (
    (df["date"] >= pd.to_datetime(date_range[0])) &
    (df["date"] <= pd.to_datetime(date_range[-1])) &
    (df["region"].isin(regions))
)

if countries:
    mask &= df["country"].isin(countries)
if products:
    mask &= df["product"].isin(products)
if reps:
    mask &= df["sales_rep"].isin(reps)
if channels:
    mask &= df["channel"].isin(channels)
if segments:
    mask &= df["segment"].isin(segments)

f = df.loc[mask].copy()

# KPIs
total_revenue = f["revenue_usd"].sum()
units = f["units_sold"].sum()
avg_uptime = f["fleet_uptime"].mean()
avg_battery = f["battery_health"].mean()
co2_saved = f["co2_saved_tons"].sum()

st.title("E‑Mobility Sales and Operations Dashboard")
st.caption("Sample portfolio dashboard for demonstration with synthetic data.")

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Revenue (USD)", f"{total_revenue:,.0f}")
k2.metric("Units sold", int(units))
k3.metric("Avg fleet uptime", f"{avg_uptime*100:,.1f}%")
k4.metric("Avg battery health", f"{avg_battery*100:,.1f}%")
k5.metric("CO₂ saved (tons)", f"{co2_saved:,.1f}")

# Charts
tab1, tab2, tab3, tab4 = st.tabs(["Trends", "By Product", "By Region and Rep", "Data"])

with tab1:
    st.subheader("Revenue trend")
    ts = f.groupby(pd.Grouper(key="date", freq="W"))["revenue_usd"].sum().reset_index()
    if not ts.empty:
        fig = px.line(ts, x="date", y="revenue_usd", markers=True, labels={"revenue_usd": "Revenue (USD)", "date": "Week"})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data for the current filters.")

with tab2:
    st.subheader("Top products by revenue")
    prod = f.groupby("product", as_index=False)["revenue_usd"].sum().sort_values("revenue_usd", ascending=False).head(10)
    if not prod.empty:
        fig = px.bar(prod, x="product", y="revenue_usd", labels={"revenue_usd": "Revenue (USD)", "product": "Product"})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data for the current filters.")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Units sold by product")
        prod_units = f.groupby("product", as_index=False)["units_sold"].sum().sort_values("units_sold", ascending=False)
        if not prod_units.empty:
            figu = px.bar(prod_units, x="product", y="units_sold", labels={"units_sold": "Units", "product": "Product"})
            st.plotly_chart(figu, use_container_width=True)
        else:
            st.info("No data for the current filters.")
    with c2:
        st.subheader("Revenue share")
        share = prod.copy()
        if not share.empty:
            figp = px.pie(share, names="product", values="revenue_usd")
            st.plotly_chart(figp, use_container_width=True)
        else:
            st.info("No data for the current filters.")

with tab3:
    st.subheader("Revenue by region")
    reg = f.groupby("region", as_index=False)["revenue_usd"].sum().sort_values("revenue_usd", ascending=False)
    if not reg.empty:
        fig = px.bar(reg, x="revenue_usd", y="region", orientation="h", labels={"revenue_usd": "Revenue (USD)", "region": "Region"})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data for the current filters.")

    st.subheader("Sales rep performance")
    rep = f.groupby("sales_rep", as_index=False)["revenue_usd"].sum().sort_values("revenue_usd", ascending=False)
    if not rep.empty:
        fig = px.bar(rep, x="sales_rep", y="revenue_usd", labels={"revenue_usd": "Revenue (USD)", "sales_rep": "Sales rep"})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data for the current filters.")

with tab4:
    st.subheader("Filtered dataset")
    st.dataframe(f.sort_values("date", ascending=False), use_container_width=True)
    st.download_button("Download filtered CSV", data=f.to_csv(index=False), file_name="filtered_sales.csv", mime="text/csv")

with st.expander("About this demo"):
    st.markdown(
        '''
        **Purpose**: sample portfolio dashboard that demonstrates BI skills in filtering, KPIs, and visuals.  
        **Use cases**: sales performance tracking, fleet operations monitoring, sustainability metrics.  
        **Data**: synthetic, generated for this demonstration.
        '''
    )
