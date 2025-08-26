import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ================================
# CONFIGURATION
# ================================
st.set_page_config(
    page_title="Digital Payments Dashboard",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================================
# LOAD DATA
# ================================
data_dir = Path("processed_data")
t1 = pd.read_csv(data_dir / "clean_t1.csv")
t2 = pd.read_csv(data_dir / "clean_t2.csv")
t5 = pd.read_csv(data_dir / "clean_t5.csv")

# ================================
# SIDEBAR FILTERS
# ================================
st.sidebar.header("Filters")

# ✅ Get common years across all datasets
common_years = sorted(set(t1["year"]).intersection(t2["year"]).intersection(t5["year"]))

# ✅ Year selection
selected_year = st.sidebar.selectbox("Select Year", common_years, index=len(common_years) - 1)

# ✅ Filtered datasets for selected year
filtered_t1 = t1[t1["year"] == selected_year]
filtered_t2 = t2[t2["year"] == selected_year]
filtered_t5 = t5[t5["year"] == selected_year]

# ================================
# KPIs SECTION
# ================================
st.title("💳 Digital Payments Dashboard")
st.markdown("#### Key Metrics Overview")

col1, col2, col3, col4 = st.columns(4)

kpi1 = filtered_t1["e_payments_per_capita"].sum() if not filtered_t1.empty else 0
kpi2 = filtered_t5["pos_per_1000"].sum() if not filtered_t5.empty else 0
kpi3 = filtered_t5["atm_per_1000"].sum() if not filtered_t5.empty else 0
kpi4 = filtered_t2["value"].sum() if not filtered_t2.empty else 0

with col1:
    st.metric("E-Payments per Capita", f"{kpi1:,.2f}")
with col2:
    st.metric("POS Terminals per 1,000", f"{kpi2:,.2f}")
with col3:
    st.metric("ATMs per 1,000", f"{kpi3:,.2f}")
with col4:
    st.metric("Total Payment Value (RM)", f"{kpi4/1e9:,.2f}B")

st.markdown("---")

# ================================
# HELPER FUNCTION: CHART WITH GREYED OUT HANDLING
# ================================
def display_chart(df, fig_func, greyed=False, **kwargs):
    """Handles missing data and shows greyed-out charts if needed"""
    if df.empty:
        # Create greyed-out empty figure
        fig = fig_func(pd.DataFrame({kwargs["x"]: [], kwargs["y"]: []}), **kwargs)
        fig.update_traces(marker=dict(color="lightgrey"), line=dict(color="lightgrey"))
        fig.update_layout(title=f"{kwargs.get('title', '')} (No data)", plot_bgcolor="#1E1E1E")
        st.plotly_chart(fig, use_container_width=True)
    else:
        # Show normal chart
        fig = fig_func(df, **kwargs)
        st.plotly_chart(fig, use_container_width=True)

# ================================
# 📈 E-Payments per Capita Over Time
# ================================
st.subheader("📈 E-Payments per Capita Over Time")
display_chart(
    t1,
    px.line,
    x="year",
    y="e_payments_per_capita",
    markers=True,
    template="plotly_dark",
    color_discrete_sequence=["#00CC96"],
    title="E-Payments per Capita"
)

st.markdown("---")

# ================================
# 💰 Payment Instruments Analysis
# ================================
st.subheader("💰 Payment Instruments Analysis")
display_chart(
    t2,
    px.line,
    x="year",
    y="volume",
    color="instrument",
    markers=True,
    template="plotly_dark",
    title="Payment Volume by Instrument"
)

st.markdown("---")

# ================================
# 🏦 Infrastructure: POS vs ATMs
# ================================
st.subheader("🏦 Infrastructure: POS vs ATMs per 1,000")
if filtered_t5.empty:
    # Greyed-out placeholder
    empty_df = pd.DataFrame({"year": [], "pos_per_1000": []})
    fig_pos_atm = px.bar(
        empty_df,
        x="year",
        y="pos_per_1000",
        template="plotly_dark",
        color_discrete_sequence=["lightgrey"],
        labels={"pos_per_1000": "POS per 1,000"}
    )
    fig_pos_atm.update_layout(title="POS vs ATMs (No data)")
    st.plotly_chart(fig_pos_atm, use_container_width=True)
else:
    fig_pos_atm = px.bar(
        t5,
        x="year",
        y="pos_per_1000",
        template="plotly_dark",
        color_discrete_sequence=["#636EFA"],
        labels={"pos_per_1000": "POS per 1,000"}
    )
    fig_pos_atm.add_scatter(
        x=t5["year"],
        y=t5["atm_per_1000"],
        mode="lines+markers",
        name="ATMs per 1,000",
        line=dict(color="#EF553B", width=3)
    )
    st.plotly_chart(fig_pos_atm, use_container_width=True)

st.markdown("---")

# ================================
# 📊 Market Share Pie Charts
# ================================
st.subheader("📊 Market Share of Payment Instruments")
col5, col6 = st.columns(2)

if filtered_t2.empty:
    # Greyed-out placeholders
    empty_df = pd.DataFrame({"instrument": [], "volume": [], "value": []})
    fig_volume_pie = px.pie(
        empty_df,
        values="volume",
        names="instrument",
        template="plotly_dark",
        title="Volume Share (No data)",
        color_discrete_sequence=["lightgrey"]
    )
    fig_value_pie = px.pie(
        empty_df,
        values="value",
        names="instrument",
        template="plotly_dark",
        title="Value Share (No data)",
        color_discrete_sequence=["lightgrey"]
    )
    col5.plotly_chart(fig_volume_pie, use_container_width=True)
    col6.plotly_chart(fig_value_pie, use_container_width=True)
else:
    volume_share = filtered_t2.groupby("instrument")["volume"].sum().reset_index()
    fig_volume_pie = px.pie(
        volume_share,
        values="volume",
        names="instrument",
        template="plotly_dark",
        color_discrete_sequence=px.colors.qualitative.Dark24,
        title="Volume Share"
    )
    col5.plotly_chart(fig_volume_pie, use_container_width=True)

    value_share = filtered_t2.groupby("instrument")["value"].sum().reset_index()
    fig_value_pie = px.pie(
        value_share,
        values="value",
        names="instrument",
        template="plotly_dark",
        color_discrete_sequence=px.colors.qualitative.Dark24,
        title="Value Share"
    )
    col6.plotly_chart(fig_value_pie, use_container_width=True)

# ================================
# FOOTER
# ================================
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: gray;'>© 2025 Digital Payments Dashboard | Built with Streamlit & Plotly</p>",
    unsafe_allow_html=True
)
