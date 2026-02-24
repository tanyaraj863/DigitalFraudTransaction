import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ------------------------------------------------
# Page Config
# ------------------------------------------------
st.set_page_config(
    page_title="Fintech Payment Analytics",
    page_icon="💳",
    layout="wide"
)

# ------------------------------------------------
# Load Data
# ------------------------------------------------
@st.cache_data
def load_data():
    return pd.read_csv("final.csv")

df = load_data()

# ------------------------------------------------
# Header
# ------------------------------------------------
st.title("💳 Digital Payment Failure Analytics")
st.markdown("### 📊 Enterprise Transaction Monitoring Dashboard")

# ------------------------------------------------
# Sidebar Filters
# ------------------------------------------------
st.sidebar.header("🔎 Filters")

status_filter = st.sidebar.multiselect(
    "Select Status",
    df['status'].unique(),
    default=df['status'].unique()
)

hour_filter = st.sidebar.slider(
    "Select Hour Range",
    int(df['hour'].min()),
    int(df['hour'].max()),
    (int(df['hour'].min()), int(df['hour'].max()))
)

filtered_df = df[
    (df['status'].isin(status_filter)) &
    (df['hour'] >= hour_filter[0]) &
    (df['hour'] <= hour_filter[1])
]

# ------------------------------------------------
# KPI Section
# ------------------------------------------------
total_txn = len(filtered_df)
total_fail = filtered_df['failure_flag'].sum()
total_success = total_txn - total_fail
failure_rate = (total_fail / total_txn) * 100 if total_txn > 0 else 0
success_rate = 100 - failure_rate

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Total Transactions", total_txn)
col2.metric("Total Success", total_success)
col3.metric("Total Failures", total_fail)
col4.metric("Failure Rate (%)", round(failure_rate, 2))
col5.metric("Success Rate (%)", round(success_rate, 2))

st.markdown("---")

# ------------------------------------------------
# Charts Row 1
# ------------------------------------------------
colA, colB = st.columns(2)

# Hourly Failure Trend
with colA:
    st.subheader("⏱ Failure Rate by Hour")
    hourly = filtered_df.groupby('hour')['failure_flag'].mean() * 100
    fig_hour = px.line(
        hourly,
        markers=True,
        labels={"value": "Failure Rate (%)", "hour": "Hour"},
    )
    st.plotly_chart(fig_hour, use_container_width=True)

# Success vs Failure Donut
with colB:
    st.subheader("📌 Success vs Failure Distribution")
    status_counts = filtered_df['status'].value_counts()
    fig_donut = go.Figure(data=[go.Pie(
        labels=status_counts.index,
        values=status_counts.values,
        hole=.5
    )])
    st.plotly_chart(fig_donut, use_container_width=True)

st.markdown("---")

# ------------------------------------------------
# Charts Row 2
# ------------------------------------------------
colC, colD = st.columns(2)

# Amount Category Failure
if 'amount_category' in filtered_df.columns:
    with colC:
        st.subheader("💰 Failure by Amount Category")
        amount_fail = filtered_df.groupby('amount_category')['failure_flag'].mean() * 100
        fig_amount = px.bar(
            amount_fail,
            labels={"value": "Failure Rate (%)", "amount_category": "Amount Category"},
        )
        st.plotly_chart(fig_amount, use_container_width=True)

# Daily Transaction Volume
with colD:
    if 'transaction_date' in filtered_df.columns:
        st.subheader("📅 Daily Transaction Volume")
        daily = filtered_df.groupby('transaction_date').size()
        fig_daily = px.line(daily, markers=True)
        st.plotly_chart(fig_daily, use_container_width=True)

st.markdown("---")

# ------------------------------------------------
# Risky Senders Table
# ------------------------------------------------
st.subheader("🚨 Top Risky Senders")

sender_risk = (
    filtered_df.groupby('sender_name')
    .agg(total_transactions=('failure_flag', 'count'),
         total_failures=('failure_flag', 'sum'))
)

sender_risk['failure_rate_%'] = (
    sender_risk['total_failures'] /
    sender_risk['total_transactions']
) * 100

sender_risk = sender_risk.sort_values(by='failure_rate_%', ascending=False).head(10)

st.dataframe(sender_risk)

# ------------------------------------------------
# Download Button
# ------------------------------------------------
st.download_button(
    label="📥 Download Filtered Data",
    data=filtered_df.to_csv(index=False),
    file_name="filtered_transactions.csv",
    mime="text/csv"
)
