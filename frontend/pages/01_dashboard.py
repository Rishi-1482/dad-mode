import sqlite3

import pandas as pd
import plotly.express as px
import streamlit as st


DB_PATH = "data/memory.db"


st.set_page_config(
    page_title="Dad Mode Dashboard",
    page_icon="📊",
    layout="wide",
)


st.title("📊 Dad Mode Dashboard")
st.caption("AI usage and performance")


@st.cache_data(ttl=5)
def load_logs():

    with sqlite3.connect(DB_PATH) as conn:

        df = pd.read_sql_query(
            """
            SELECT
                id,
                conversation_id,
                route,
                tools,
                latency_ms,
                success,
                model,
                input_tokens,
                output_tokens,
                created_at
            FROM request_logs
            ORDER BY created_at
            """,
            conn,
        )

    if not df.empty:
        df["created_at"] = pd.to_datetime(
            df["created_at"]
        )

    return df


if st.button("🔄 Refresh"):

    st.cache_data.clear()
    st.rerun()


df = load_logs()


if df.empty:

    st.info(
        "No requests recorded yet. "
        "Use Dad Mode first."
    )

    st.stop()


# ---------------------------------
# Metrics
# ---------------------------------

total_requests = len(df)

average_latency = df["latency_ms"].mean()

successful_requests = df["success"].sum()

success_rate = (
    successful_requests / total_requests
) * 100


col1, col2, col3, col4 = st.columns(4)


col1.metric(
    "Total Requests",
    total_requests,
)

col2.metric(
    "Avg Latency",
    f"{average_latency:.0f} ms",
)

col3.metric(
    "Success Rate",
    f"{success_rate:.1f}%",
)

col4.metric(
    "Conversations",
    df["conversation_id"].nunique(),
)

total_input = df["input_tokens"].sum()
total_output = df["output_tokens"].sum()
total_tokens = total_input + total_output

estimated_cost = (
    (total_input / 1_000_000) * 0.15
    + (total_output / 1_000_000) * 0.60
)

col3.metric(
    "Total Input Tokens",
    f"{total_input:,}",
)

col2.metric(
    "Total Output Tokens",
    f"{total_output:,}",
)

col1.metric(
    "Total Cost",
    f"${estimated_cost:.4f}",
)


st.divider()


# ---------------------------------
# Requests by route
# ---------------------------------

route_counts = (
    df["route"]
    .value_counts()
    .reset_index()
)

route_counts.columns = [
    "route",
    "count",
]


fig_routes = px.bar(
    route_counts,
    x="route",
    y="count",
    title="Requests by Route",
)
fig_routes.update_traces(width=0.2)
fig_routes.update_layout(bargap=0.1)

st.plotly_chart(
    fig_routes,
    use_container_width=True,
)


# ---------------------------------
# Latency over time
# ---------------------------------

fig_latency = px.line(
    df,
    x="created_at",
    y="latency_ms",
    title="Latency Over Time",
    markers=True,
)

st.plotly_chart(
    fig_latency,
    use_container_width=True,
)


# ---------------------------------
# Tool usage
# ---------------------------------

tool_rows = []

for tools in df["tools"].dropna():

    if not tools:
        continue

    for tool in tools.split(","):

        if tool:
            tool_rows.append(tool)


if tool_rows:

    tool_counts = (
        pd.Series(tool_rows)
        .value_counts()
        .reset_index()
    )

    tool_counts.columns = [
        "tool",
        "count",
    ]

    fig_tools = px.bar(
        tool_counts,
        x="tool",
        y="count",
        title="Tool Usage",
    )
    fig_tools.update_traces(width=0.2)
    fig_tools.update_layout(bargap=0.1)

    st.plotly_chart(
        fig_tools,
        use_container_width=True,
    )


# ---------------------------------
# Recent requests
# ---------------------------------

st.subheader("Recent Requests")

st.dataframe(
    df.sort_values(
        "created_at",
        ascending=False,
    ).head(20),
    use_container_width=True,
)