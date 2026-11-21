
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path


# ==========================================
# PROJECT PATHS
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

FORECAST_PATH = (
    PROJECT_ROOT
    / "evaluation"
    / "seven_day_forecast.csv"
)


# ==========================================
# THEME CONSTANTS
# ==========================================

COLORS = {
    "background": "#101B2A",
    "surface": "#17283B",
    "surface_light": "#20364B",
    "primary": "#54D6C4",
    "secondary": "#39B9D3",
    "text": "#E6EDF5",
    "muted": "#A8BACB",
    "border": "#304459",
}


# ==========================================
# LOAD AND VALIDATE FORECAST DATA
# ==========================================

@st.cache_data
def load_forecast(file_path, modified_time):

    if not Path(file_path).exists():
        return None, "Forecast CSV file was not found."

    try:
        data = pd.read_csv(file_path)

        required_columns = {
            "sensor_id",
            "date",
            "predicted_consumption"
        }

        missing_columns = required_columns - set(data.columns)

        if missing_columns:
            return None, (
                "Missing required columns: "
                + ", ".join(sorted(missing_columns))
            )

        if data.empty:
            return None, "The forecast CSV contains no records."

        data["sensor_id"] = data["sensor_id"].astype("string").str.strip()

        data["date"] = pd.to_datetime(
            data["date"],
            errors="coerce"
        )

        data["predicted_consumption"] = pd.to_numeric(
            data["predicted_consumption"],
            errors="coerce"
        )

        if (
            data["sensor_id"].isna().any()
            or data["sensor_id"].eq("").any()
        ):
            return None, "The forecast CSV contains invalid sensor IDs."

        if (
            data["date"].isna().any()
            or data["predicted_consumption"].isna().any()
        ):
            return None, (
                "The forecast CSV contains invalid dates "
                "or consumption values."
            )

        if not data["predicted_consumption"].map(
            lambda value: pd.notna(value) and abs(value) != float("inf")
        ).all():
            return None, "The forecast CSV contains non-finite values."

        if (data["predicted_consumption"] < 0).any():
            return None, "Negative predicted consumption values were found."

        data = data.sort_values(
            ["date", "sensor_id"]
        ).reset_index(drop=True)

        return data, None

    except (OSError, pd.errors.ParserError, UnicodeDecodeError) as error:
        return None, f"Unable to read forecast CSV: {error}"


modified_time = (
    FORECAST_PATH.stat().st_mtime
    if FORECAST_PATH.exists()
    else None
)

forecast, forecast_error = load_forecast(
    str(FORECAST_PATH),
    modified_time
)


# ==========================================
# PAGE HEADER
# ==========================================

st.markdown(
    """
    <div style="
        color: #54D6C4;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1.5px;">
        PREDICTIVE INTELLIGENCE
    </div>
    """,
    unsafe_allow_html=True
)

st.title("Demand Forecasting")

st.markdown(
    "Seven-day water consumption forecasts across "
    "selected household sensors."
)

st.divider()


# ==========================================
# VALIDATE FORECAST AVAILABILITY
# ==========================================

if forecast is None:
    st.error(forecast_error)

    st.info(
        "Generate the seven-day forecast before using this module."
    )

    st.stop()


# ==========================================
# SUMMARY METRICS
# ==========================================

sensor_count = forecast["sensor_id"].nunique()
forecast_days = forecast["date"].nunique()
prediction_count = len(forecast)

average_prediction = forecast[
    "predicted_consumption"
].mean()

total_prediction = forecast[
    "predicted_consumption"
].sum()

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Forecast Sensors",
    sensor_count
)

col2.metric(
    "Forecast Horizon",
    f"{forecast_days} Days"
)

col3.metric(
    "Total Predictions",
    prediction_count
)

col4.metric(
    "Average Predicted Value",
    f"{average_prediction:.5f}"
)

st.divider()


# ==========================================
# FORECAST EXPLORER
# ==========================================

st.subheader("Forecast Explorer")

sensor_options = [
    "All Sensors"
] + sorted(forecast["sensor_id"].unique().tolist())

selected_sensor = st.selectbox(
    "Select Sensor",
    sensor_options
)

if selected_sensor == "All Sensors":
    chart_data = forecast.copy()
else:
    chart_data = forecast[
        forecast["sensor_id"] == selected_sensor
    ].copy()


# ==========================================
# SELECTED SENSOR METRICS
# ==========================================

metric1, metric2, metric3 = st.columns(3)

metric1.metric(
    "Selected Forecast Records",
    len(chart_data)
)

metric2.metric(
    "Average Predicted Consumption",
    f"{chart_data['predicted_consumption'].mean():.5f}"
)

metric3.metric(
    "Maximum Predicted Consumption",
    f"{chart_data['predicted_consumption'].max():.5f}"
)


# ==========================================
# SEVEN-DAY FORECAST TREND
# ==========================================

st.divider()

st.subheader("Seven-Day Consumption Forecast")

if selected_sensor == "All Sensors":

    fig = px.line(
        chart_data,
        x="date",
        y="predicted_consumption",
        color="sensor_id",
        markers=True,
        template="plotly_dark",
        labels={
            "date": "Forecast Date",
            "predicted_consumption": "Predicted Consumption",
            "sensor_id": "Sensor ID"
        },
        title="Predicted Consumption Across Sensors"
    )

else:

    fig = px.line(
        chart_data,
        x="date",
        y="predicted_consumption",
        markers=True,
        template="plotly_dark",
        labels={
            "date": "Forecast Date",
            "predicted_consumption": "Predicted Consumption"
        },
        title=f"Seven-Day Forecast — {selected_sensor}"
    )

fig.update_layout(
    paper_bgcolor=COLORS["background"],
    plot_bgcolor=COLORS["surface"],
    font=dict(color=COLORS["text"]),
    title_font=dict(color=COLORS["primary"], size=17),
    legend_title_text="Sensor ID",
    hovermode="x unified",
    margin=dict(l=20, r=20, t=55, b=20),
    xaxis=dict(
        showgrid=False,
        title="Forecast Date"
    ),
    yaxis=dict(
        gridcolor=COLORS["border"],
        title="Predicted Consumption (dataset units)"
    )
)

fig.update_traces(
    line=dict(width=2),
    marker=dict(size=7)
)

st.plotly_chart(
    fig,
    use_container_width=True
)


# ==========================================
# SENSOR-WISE FORECAST COMPARISON
# ==========================================

st.divider()

st.subheader("Sensor-wise Forecast Comparison")

sensor_summary = (
    forecast.groupby("sensor_id")["predicted_consumption"]
    .agg(
        Average="mean",
        Minimum="min",
        Maximum="max",
        Total="sum"
    )
    .reset_index()
)

sensor_summary = sensor_summary.round(6)

bar_fig = px.bar(
    sensor_summary,
    x="sensor_id",
    y="Average",
    text="Average",
    color="Average",
    color_continuous_scale=[
        "#20364B",
        "#39B9D3",
        "#54D6C4"
    ],
    template="plotly_dark",
    title="Average Predicted Consumption by Sensor",
    labels={
        "sensor_id": "Sensor ID",
        "Average": "Average Predicted Consumption"
    }
)

bar_fig.update_traces(
    texttemplate="%{text:.5f}",
    textposition="outside"
)

bar_fig.update_layout(
    paper_bgcolor=COLORS["background"],
    plot_bgcolor=COLORS["background"],
    font=dict(color=COLORS["text"]),
    title_font=dict(color=COLORS["primary"], size=17),
    showlegend=False,
    coloraxis_showscale=False,
    margin=dict(l=20, r=20, t=55, b=20),
    xaxis=dict(showgrid=False),
    yaxis=dict(gridcolor=COLORS["border"])
)

st.plotly_chart(
    bar_fig,
    use_container_width=True
)


# ==========================================
# SENSOR SUMMARY TABLE
# ==========================================

st.subheader("Forecast Statistics")

st.dataframe(
    sensor_summary,
    use_container_width=True,
    hide_index=True
)


# ==========================================
# DETAILED FORECAST RECORDS
# ==========================================

st.divider()

with st.expander("View Detailed Forecast Records"):

    display_data = chart_data.copy()

    display_data["date"] = (
        display_data["date"].dt.strftime("%Y-%m-%d")
    )

    display_data["predicted_consumption"] = (
        display_data["predicted_consumption"].round(6)
    )

    st.dataframe(
        display_data,
        use_container_width=True,
        hide_index=True
    )


# ==========================================
# DOWNLOAD FORECAST
# ==========================================

st.divider()

st.subheader("Export Forecast Data")

csv_data = chart_data.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="Download Forecast CSV",
    data=csv_data,
    file_name="aquasentinel_seven_day_forecast.csv",
    mime="text/csv",
    use_container_width=False
)


# ==========================================
# MODEL INFORMATION
# ==========================================

st.info(
    "Forecasts are generated from historical household sensor "
    "observations. Consumption values retain the dataset's "
    "recorded units; the source documentation has an unresolved "
    "unit discrepancy."
)


# ==========================================
# FOOTER
# ==========================================

st.caption(
    "AquaSentinel AI | Demand Forecasting | "
    "Historical Household Sensor Data"
)
