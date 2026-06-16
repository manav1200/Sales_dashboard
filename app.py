import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import sqlite3
from queries import (
    yoy_growth, regional_performance,
    top_products, customer_segments, sales_over_time
)

#Page config
st.set_page_config(page_title="Sales KPI Dashboard", layout="wide", page_icon=":bar_chart:")

st.title("Sales KPI Analytics Dashboard")
st.caption("Superstore Retail Data")

#Sidebar filters
conn = sqlite3.connect("sales.db")

regions = ["All"] + pd.read_sql(
    "SELECT DISTINCT region FROM orders", conn
)["region"].tolist()

categories = ["All"] + pd.read_sql(
    "SELECT DISTINCT category FROM orders", conn
)["category"].tolist()

years = pd.read_sql(
    "SELECT DISTINCT CAST(strftime('%Y', order_date) AS INTEGER) AS year FROM orders ORDER BY year",
    conn
)["year"].tolist()

conn.close()

with st.sidebar:
    st.header("Filters")
    sel_region = st.selectbox("Region", regions)
    sel_category = st.selectbox("Category", categories)
    sel_years = st.multiselect("Year(s)", years, default=years)

#KPI Cards
conn = sqlite3.connect("sales.db")

filters = []
if sel_region != "All":
    filters.append(f"region = '{sel_region}'")

if sel_category != "All":
    filters.append(f"category = '{sel_category}'")

if sel_years:
    filters.append(f"year IN ({','.join(map(str, sel_years))})")

where = "WHERE " + " AND ".join(filters) if filters else ""

summary = pd.read_sql(f"""
    SELECT 
        SUM(sales) as sales, 
        SUM(profit) as profit,
        COUNT(DISTINCT order_id) as orders,
        COUNT(DISTINCT customer_id) as customers
    FROM orders {where}
""", conn).iloc[0]

conn.close()

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Revenue", f"${summary['sales']:,.0f}")
c2.metric("Total Profit", f"${summary['profit']:,.0f}")
c3.metric("Total Orders", f"{summary['orders']:,}")
c4.metric("Unique Customers", f"{summary['customers']:,}")

st.divider()

#Row 1: Revenue trend + YoY growth
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Monthly Revenue Trend")
    trend = sales_over_time(sel_region, sel_category)

    fig = px.line(
        trend,
        x="month",
        y=["monthly_sales", "monthly_profit"],
        labels={"value": "Amount ($)", "month": "Month"},
        color_discrete_map={
            "monthly_sales": "#1f77b4",
            "monthly_profit": "#2ca02c"
        }
    )

    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("YoY Growth")
    yoy = yoy_growth()

    fig2 = px.bar(
        yoy,
        x="year",
        y="sales_growth_pct",
        color="sales_growth_pct",
        color_continuous_scale="RdYlGn",
        labels={"sales_growth_pct": "Growth %"}
    )

    st.plotly_chart(fig2, use_container_width=True)

# ── Row 2: Regional breakdown + Product profitability ────────────
col3, col4 = st.columns(2)

with col3:
    st.subheader("Regional Performance by Category")
    reg = regional_performance()

    fig3 = px.bar(
        reg,
        x="region",
        y="total_sales",
        color="category",
        barmode="group",
        labels={"total_sales": "Sales ($)"}
    )

    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.subheader("Product Profitability (Top 15)")
    prod = top_products()

    fig4 = px.bar(
        prod,
        x="total_profit",
        y="sub_category",
        orientation="h",
        color="margin_pct",
        color_continuous_scale="Blues",
        labels={
            "total_profit": "Profit ($)",
            "sub_category": ""
        }
    )

    st.plotly_chart(fig4, use_container_width=True)

# ── Row 3: Customer segments + Margin table ──────────────────────
col5, col6 = st.columns(2)

with col5:
    st.subheader("Customer Segment Analysis")
    seg = customer_segments()

    fig5 = px.pie(
        seg,
        names="segment",
        values="total_sales",
        hole=0.45,
        color_discrete_sequence=px.colors.qualitative.Set2
    )

    st.plotly_chart(fig5, use_container_width=True)

with col6:
    st.subheader("Segment Revenue Summary")

    st.dataframe(
        seg.style.format({
            "total_sales": "${:,.0f}",
            "total_profit": "${:,.0f}",
            "avg_revenue_per_customer": "${:,.2f}"
        }),
        use_container_width=True
    )