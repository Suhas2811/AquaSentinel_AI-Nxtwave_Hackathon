
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
# PAGE HEADER
# ==========================================

st.markdown("## System Overview")

st.caption(
    "Predictive urban water intelligence and decision support"
)

st.divider()


# ==========================================
# LOAD FORECAST DATA
# ==========================================

forecast_df = None
forecast_error = None

if FORECAST_PATH.exists():

    try:
        forecast_df = pd.read_csv(FORECAST_PATH)

        required_columns = {
            "sensor_id",
            "date",
            "predicted_consumption"
        }

        missing_columns = required_columns - set(forecast_df.columns)

        if missing_columns:
            forecast_error = (
                "Forecast CSV is missing required columns: "
                + ", ".join(sorted(missing_columns))
            )
            forecast_df = None

        elif forecast_df.empty:
            forecast_error = "The forecast CSV contains no records."
            forecast_df = None

        else:
            forecast_df["date"] = pd.to_datetime(
                forecast_df["date"],
                errors="coerce"
            )

            forecast_df["predicted_consumption"] = pd.to_numeric(
                forecast_df["predicted_consumption"],
                errors="coerce"
            )

            if (
                forecast_df["date"].isna().any()
                or forecast_df["predicted_consumption"].isna().any()
            ):
                forecast_error = (
                    "The forecast CSV contains invalid dates "
                    "or consumption values."
                )
                forecast_df = None

    except (
        OSError,
        pd.errors.ParserError,
        UnicodeDecodeError
    ) as error:

        forecast_error = f"Unable to read forecast CSV: {error}"

else:
    forecast_error = (
        f"Forecast file not found: {FORECAST_PATH}"
    )


# ==========================================
# SYSTEM METRICS
# ==========================================

if forecast_df is not None:

    sensor_count = forecast_df["sensor_id"].nunique()
    prediction_count = len(forecast_df)
    forecast_days = forecast_df["date"].nunique()

else:

    sensor_count = 0
    prediction_count = 0
    forecast_days = 0


col1, col2, col3, col4 = st.columns(4)

col1.metric("Trained Sensors", sensor_count)
col2.metric("Forecast Horizon", f"{forecast_days} Days")
col3.metric("Forecast Predictions", prediction_count)
col4.metric("Forecast Model", "Hybrid Ridge")


st.divider()


# ==========================================
# INTELLIGENCE PIPELINE
# ==========================================

st.subheader("Intelligence Pipeline")

pipeline = st.columns(4)

pipeline[0].markdown("### 01 · Predict")
pipeline[0].caption("Forecast future water demand")

pipeline[1].markdown("### 02 · Detect")
pipeline[1].caption("Investigate unusual consumption")

pipeline[2].markdown("### 03 · Optimize")
pipeline[2].caption("Allocate resources equitably")

pipeline[3].markdown("### 04 · Explain")
pipeline[3].caption("AI-assisted decision support")


st.divider()


# ==========================================
# FORECAST DATASET PREVIEW
# ==========================================

st.subheader("Latest Forecast Dataset")

if forecast_df is not None:

    display_df = forecast_df.copy()

    display_df["date"] = (
        display_df["date"].dt.strftime("%Y-%m-%d")
    )

    display_df["predicted_consumption"] = (
        display_df["predicted_consumption"].round(6)
    )

    # ======================================
    # PREMIUM DARK TABLE
    # ======================================

    styled_forecast = (
        display_df.head(10)
        .style
        .set_properties(**{
            "background-color": "#17283B",
            "color": "#E6EDF5",
            "border-color": "#304459",
            "text-align": "left"
        })
        .set_table_styles([
            {
                "selector": "th",
                "props": [
                    ("background-color", "#20364B"),
                    ("color", "#54D6C4"),
                    ("border-color", "#304459"),
                    ("font-weight", "600")
                ]
            },
            {
                "selector": "td",
                "props": [
                    ("border-color", "#304459")
                ]
            }
        ])
    )

    st.dataframe(
        styled_forecast,
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        f"Showing 10 of {prediction_count} forecast records"
    )


    # ======================================
    # SENSOR-WISE AVERAGE FORECAST
    # ======================================

    st.divider()

    st.subheader("Average Forecast by Sensor")

    sensor_summary = (
        forecast_df.groupby("sensor_id")[
            "predicted_consumption"
        ]
        .mean()
        .reset_index()
    )

    sensor_summary.columns = [
        "Sensor ID",
        "Average Predicted Consumption"
    ]

    sensor_summary["Average Predicted Consumption"] = (
        sensor_summary["Average Predicted Consumption"].round(6)
    )


    # ======================================
    # INTERACTIVE PLOTLY CHART
    # ======================================

    fig = px.bar(
        sensor_summary,
        x="Sensor ID",
        y="Average Predicted Consumption",
        color="Average Predicted Consumption",
        color_continuous_scale=[
            "#20364B",
            "#39B9D3",
            "#54D6C4"
        ],
        text_auto=".4f",
        hover_data={
            "Sensor ID": True,
            "Average Predicted Consumption": ":.6f"
        }
    )

    fig.update_layout(
        template="plotly_dark",

        paper_bgcolor="#101B2A",
        plot_bgcolor="#101B2A",

        font=dict(
            family="Arial",
            color="#E6EDF5",
            size=13
        ),

        title=dict(
            text="Average Predicted Consumption by Sensor",
            font=dict(
                size=18,
                color="#54D6C4"
            )
        ),

        xaxis_title="Sensor ID",

        yaxis_title=(
            "Average Recorded Consumption (dataset units)"
        ),

        coloraxis_showscale=False,

        margin=dict(
            l=20,
            r=20,
            t=65,
            b=30
        ),

        height=430,

        hoverlabel=dict(
            bgcolor="#20364B",
            font_color="#E6EDF5"
        )
    )

    fig.update_traces(
        marker_line_width=0,
        textposition="outside",
        textfont=dict(
            color="#E6EDF5",
            size=11
        ),
        cliponaxis=False
    )

    fig.update_xaxes(
        showgrid=False,
        color="#A8BACB"
    )

    fig.update_yaxes(
        gridcolor="#304459",
        zerolinecolor="#304459",
        color="#A8BACB"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


else:

    st.warning(forecast_error)


st.divider()


# ==========================================
# PROJECT STATUS
# ==========================================

st.info(
    "Prototype status: Household-level historical observations "
    "combined with simulated urban infrastructure. "
    "This system is a decision-support prototype, "
    "not a live municipal controller."
)


# ==========================================
# FOOTER
# ==========================================

st.caption(
    "AquaSentinel AI | Urban Water Intelligence"
)
