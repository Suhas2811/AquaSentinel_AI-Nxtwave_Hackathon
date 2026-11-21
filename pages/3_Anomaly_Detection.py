
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path
from sklearn.ensemble import IsolationForest

# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Anomaly Detection | AquaSentinel AI",
    page_icon="🔍",
    layout="wide",
)

# ============================================================
# 2. PROJECT PATHS AND MODEL SETTINGS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "HSB_Sensor_Daily_Features.csv"
)

FEATURES = [
    "daily_consumption",
    "event_count",
    "mean_event_value",
    "maximum_event_value",
    "consumption_change",
]

CONTAMINATION = 0.02
MIN_SENSOR_RECORDS = 30
N_ESTIMATORS = 50
RANDOM_STATE = 42
MAX_NORMAL_CHART_POINTS = 15000

# ============================================================
# 3. PAGE HEADER
# ============================================================

st.markdown(
    """
    <div style="
        color: #54D6C4;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 1.5px;">
        INTELLIGENCE AND MONITORING
    </div>
    """,
    unsafe_allow_html=True,
)

st.title("Anomaly Detection")

st.markdown(
    "Identify unusual household water-consumption patterns "
    "using sensor-level unsupervised machine learning."
)

st.divider()

# ============================================================
# 4. LOAD DATA
# ============================================================

@st.cache_data(show_spinner=False)
def load_data(path_string, modified_time):
    data = pd.read_csv(path_string)
    data["date"] = pd.to_datetime(
        data["date"],
        errors="coerce"
    )
    return data


if not DATA_PATH.is_file():
    st.error(
        "Required dataset not found: "
        "data/processed/HSB_Sensor_Daily_Features.csv"
    )

    st.info(
        "Generate the sensor daily feature dataset "
        "before opening this page."
    )

    st.stop()


try:
    df = load_data(
        str(DATA_PATH),
        DATA_PATH.stat().st_mtime
    )

except Exception as error:
    st.error(f"Unable to load the dataset: {error}")
    st.stop()


# ============================================================
# 5. VALIDATE AND PREPARE DATA
# ============================================================

REQUIRED_COLUMNS = [
    "sensor_id",
    "date",
    *FEATURES,
]

missing_columns = [
    column
    for column in REQUIRED_COLUMNS
    if column not in df.columns
]

if missing_columns:
    st.error(
        "Dataset is missing required columns: "
        + ", ".join(missing_columns)
    )
    st.stop()


initial_rows = len(df)

df["sensor_id"] = (
    df["sensor_id"]
    .astype("string")
    .str.strip()
)

df["date"] = pd.to_datetime(
    df["date"],
    errors="coerce"
)

df = df.dropna(
    subset=["date", "sensor_id"]
).copy()

df = df[df["sensor_id"] != ""].copy()


for column in FEATURES:
    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )


df[FEATURES] = df[FEATURES].replace(
    [np.inf, -np.inf],
    np.nan
)


removed_rows = initial_rows - len(df)

if removed_rows > 0:
    st.warning(
        f"{removed_rows:,} rows were excluded because "
        "their date or sensor identifier was invalid."
    )


if df.empty:
    st.error("No valid records remain after data validation.")
    st.stop()


df = df.sort_values(
    ["sensor_id", "date"]
).reset_index(drop=True)


# ============================================================
# 6. SENSOR-LEVEL ISOLATION FOREST
# ============================================================

@st.cache_data(show_spinner=False)
def detect_anomalies(
    data,
    feature_columns,
    contamination,
    minimum_records,
    estimators,
    random_state,
):

    results = []

    for sensor_id, sensor_data in data.groupby(
        "sensor_id",
        sort=False
    ):

        sensor_data = sensor_data.sort_values(
            "date"
        ).copy()

        valid = sensor_data.dropna(
            subset=list(feature_columns)
        ).copy()

        if len(valid) < minimum_records:
            continue

        X = valid[
            list(feature_columns)
        ].astype("float32")

        model = IsolationForest(
            n_estimators=estimators,
            max_samples="auto",
            contamination=contamination,
            random_state=random_state,
            n_jobs=1,
        )

        predictions = model.fit_predict(X)

        scores = -model.decision_function(X)

        valid["anomaly_prediction"] = predictions

        valid["anomaly_score"] = scores

        valid["anomaly_status"] = np.where(
            predictions == -1,
            "Anomaly",
            "Normal"
        )

        results.append(valid)


    if not results:
        return pd.DataFrame()


    output = pd.concat(
        results,
        ignore_index=True
    )

    return output.sort_values(
        ["date", "sensor_id"]
    ).reset_index(drop=True)


with st.spinner(
    "Analysing sensor consumption patterns. "
    "The first run may take a little time; results are cached afterward."
):

    anomalies = detect_anomalies(
        df,
        tuple(FEATURES),
        CONTAMINATION,
        MIN_SENSOR_RECORDS,
        N_ESTIMATORS,
        RANDOM_STATE,
    )


if anomalies.empty:
    st.warning(
        "No eligible sensor records were available "
        "for anomaly detection."
    )
    st.stop()


# ============================================================
# 7. DETECTION OVERVIEW
# ============================================================

total_records = len(anomalies)
source_records = len(df)
excluded_records = source_records - total_records

anomaly_records = anomalies[
    anomalies["anomaly_status"] == "Anomaly"
].copy()

anomaly_count = len(anomaly_records)

sensor_count = anomalies["sensor_id"].nunique()

affected_sensors = anomaly_records[
    "sensor_id"
].nunique()

anomaly_rate = (
    anomaly_count / total_records * 100
    if total_records
    else 0
)


st.subheader("Detection Overview")

st.caption(
    "Dataset-wide results across all eligible sensors. "
    "These figures remain unchanged when the explorer is filtered."
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Analysed Records",
    f"{total_records:,}"
)

col2.metric(
    "Detected Anomalies",
    f"{anomaly_count:,}"
)

col3.metric(
    "Affected Sensors",
    f"{affected_sensors:,}"
)

col4.metric(
    "Anomaly Rate",
    f"{anomaly_rate:.2f}%"
)

st.caption(
    f"Modelled {sensor_count:,} sensors independently | "
    f"Isolation Forest contamination setting: {CONTAMINATION:.0%} per sensor | "
    f"Minimum records per sensor: {MIN_SENSOR_RECORDS}"
)

st.caption(
    f"Source records: {source_records:,} | "
    f"Modelled records: {total_records:,} | "
    f"Not modelled: {excluded_records:,}. "
    "Rows may be excluded because one or more model features are missing "
    "or a sensor has fewer than the minimum required records."
)

st.divider()


# ============================================================
# 8. ANOMALY EXPLORER
# ============================================================

st.subheader("Anomaly Explorer")

sensor_options = ["All Sensors"] + sorted(
    anomalies["sensor_id"].dropna().unique().tolist()
)

selected_sensor = st.selectbox(
    "Select Sensor",
    sensor_options,
    key="anomaly_sensor_filter"
)


sensor_filtered = anomalies.copy()

if selected_sensor != "All Sensors":
    sensor_filtered = sensor_filtered[
        sensor_filtered["sensor_id"] == selected_sensor
    ].copy()


if sensor_filtered.empty:
    st.warning("No modelled records are available for this sensor.")
    st.stop()


# ============================================================
# 9. DATE FILTER
# ============================================================

min_date = sensor_filtered["date"].min().date()
max_date = sensor_filtered["date"].max().date()

date_range = st.date_input(
    "Select Analysis Period",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
    # Keep date-picker state separate for each sensor.
    key=f"anomaly_date_filter_{selected_sensor.replace(' ', '_')}"
)


if isinstance(date_range, (tuple, list)):

    if len(date_range) == 2:
        start_date, end_date = date_range

    elif len(date_range) == 1:
        start_date = end_date = date_range[0]

    else:
        start_date, end_date = min_date, max_date

else:
    start_date = end_date = date_range


if start_date > end_date:
    st.error("The start date must be on or before the end date.")
    st.stop()


filtered = sensor_filtered[
    sensor_filtered["date"].dt.date.between(
        start_date,
        end_date
    )
].copy()


if filtered.empty:
    st.warning("No records found for the selected filters.")
    st.stop()


# ============================================================
# 10. FILTERED VIEW METRICS
# ============================================================

filtered_anomalies = filtered[
    filtered["anomaly_status"] == "Anomaly"
].copy()

filtered_count = len(filtered)

filtered_anomaly_count = len(filtered_anomalies)

filtered_sensor_count = filtered["sensor_id"].nunique()

filtered_rate = (
    filtered_anomaly_count / filtered_count * 100
    if filtered_count
    else 0
)


st.markdown("#### Selected View")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Records in View",
    f"{filtered_count:,}"
)

c2.metric(
    "Anomalies in View",
    f"{filtered_anomaly_count:,}"
)

c3.metric(
    "Sensors in View",
    f"{filtered_sensor_count:,}"
)

c4.metric(
    "Anomaly Rate in View",
    f"{filtered_rate:.2f}%"
)

# ============================================================
# 10A. SENSOR INVESTIGATION PANEL
# ============================================================

st.markdown("#### Sensor Investigation")

if selected_sensor == "All Sensors":
    st.info(
        "Select an individual sensor above to inspect its observation "
        "coverage, consumption history and anomaly details."
    )
else:
    # Use the original sensor-day dataset for coverage. Do not calculate
    # coverage from modelled rows because feature NaNs can exclude records.
    sensor_source = df[df["sensor_id"] == selected_sensor].copy()

    expected_days = (
        (df["date"].max().normalize() - df["date"].min().normalize()).days + 1
    )
    observed_days = sensor_source["date"].dt.normalize().nunique()
    coverage_pct = (
        observed_days / expected_days * 100 if expected_days > 0 else 0.0
    )

    sensor_anomalies_all = anomalies[
        (anomalies["sensor_id"] == selected_sensor)
        & (anomalies["anomaly_status"] == "Anomaly")
    ]

    sensor_modelled_rows = anomalies[
        anomalies["sensor_id"] == selected_sensor
    ]

    profile_cols = st.columns(4)
    profile_cols[0].metric("Observed days", f"{observed_days:,}")
    profile_cols[1].metric("Calendar coverage", f"{coverage_pct:.1f}%")
    profile_cols[2].metric("Modelled records", f"{len(sensor_modelled_rows):,}")
    profile_cols[3].metric("Flagged anomalies", f"{len(sensor_anomalies_all):,}")

    if coverage_pct < 25:
        st.warning(
            "Low observation coverage: interpret this sensor's anomaly "
            "results cautiously because much of the calendar period has no record."
        )
    elif coverage_pct < 60:
        st.info(
            "Moderate observation coverage: missing days may affect the "
            "historical picture. A missing day is not treated as zero consumption."
        )
    else:
        st.success(
            "Relatively stronger observation coverage across the dataset's "
            "calendar period. Missing days are still not interpreted as zero use."
        )

    if not sensor_source.empty:
        source_consumption = sensor_source["daily_consumption"].dropna()
        if not source_consumption.empty:
            st.caption(
                "Recorded consumption statistics for this sensor are shown "
                "using the available observed days only; dataset units are "
                "not asserted because the source documentation has a unit discrepancy."
            )
            stat_cols = st.columns(3)
            stat_cols[0].metric(
                "Mean recorded value", f"{source_consumption.mean():.5f}"
            )
            stat_cols[1].metric(
                "Median recorded value", f"{source_consumption.median():.5f}"
            )
            stat_cols[2].metric(
                "Maximum recorded value", f"{source_consumption.max():.5f}"
            )

st.divider()


# ============================================================
# 11. RECORDED CONSUMPTION TREND
# ============================================================

st.markdown("### Recorded Consumption Trend")

normal_data = filtered[
    filtered["anomaly_status"] == "Normal"
].copy()

anomaly_data = filtered_anomalies.copy()


# Sample normal points only in the all-sensor view.
# Every flagged anomaly remains visible.

normal_sampled = False

if (
    selected_sensor == "All Sensors"
    and len(normal_data) > MAX_NORMAL_CHART_POINTS
):

    normal_data = normal_data.sample(
        n=MAX_NORMAL_CHART_POINTS,
        random_state=RANDOM_STATE
    )

    normal_sampled = True


fig = go.Figure()


# Normal observations

fig.add_trace(
    go.Scatter(
        x=normal_data["date"],
        y=normal_data["daily_consumption"],
        mode="markers",
        name="Normal",
        marker=dict(
            color="#39B9D3",
            size=5,
            opacity=0.75
        ),
        customdata=normal_data[
            [
                "sensor_id",
                "event_count",
                "maximum_event_value"
            ]
        ].to_numpy(),
        hovertemplate=(
            "<b>Normal observation</b><br>"
            "Date: %{x|%d %b %Y}<br>"
            "Sensor: %{customdata[0]}<br>"
            "Recorded consumption: %{y:.5f}<br>"
            "Event count: %{customdata[1]}<br>"
            "Maximum event value: %{customdata[2]:.5f}"
            "<extra></extra>"
        )
    )
)


# Anomalous observations

fig.add_trace(
    go.Scatter(
        x=anomaly_data["date"],
        y=anomaly_data["daily_consumption"],
        mode="markers",
        name="Anomaly",
        marker=dict(
            color="#F07178",
            size=10,
            symbol="diamond",
            line=dict(
                color="#FFFFFF",
                width=0.6
            )
        ),
        customdata=anomaly_data[
            [
                "sensor_id",
                "event_count",
                "maximum_event_value",
                "anomaly_score"
            ]
        ].to_numpy(),
        hovertemplate=(
            "<b>Flagged anomaly</b><br>"
            "Date: %{x|%d %b %Y}<br>"
            "Sensor: %{customdata[0]}<br>"
            "Recorded consumption: %{y:.5f}<br>"
            "Event count: %{customdata[1]}<br>"
            "Maximum event value: %{customdata[2]:.5f}<br>"
            "Anomaly score: %{customdata[3]:.5f}"
            "<extra></extra>"
        )
    )
)


fig.update_layout(
    template="plotly_dark",
    paper_bgcolor="#101B2A",
    plot_bgcolor="#17283B",
    font=dict(color="#E6EDF5"),
    xaxis_title="Date",
    yaxis_title="Recorded Consumption (dataset value)",
    legend_title="Detection Result",
    height=470,
    margin=dict(
        l=20,
        r=20,
        t=35,
        b=20
    ),
    hovermode="closest"
)

fig.update_xaxes(showgrid=False)

fig.update_yaxes(
    gridcolor="rgba(210,225,240,0.18)"
)


st.plotly_chart(
    fig,
    width="stretch",
    config={"displaylogo": False}
)


if normal_sampled:
    st.caption(
        f"Chart performance: showing a reproducible sample of "
        f"{MAX_NORMAL_CHART_POINTS:,} normal observations plus every "
        "flagged anomaly. Tables and downloads retain all filtered records."
    )


# ============================================================
# 12. DETECTED ANOMALIES
# ============================================================

st.divider()

st.markdown("### Detected Anomalies")


if filtered_anomalies.empty:

    st.success(
        "No anomalies were flagged for the selected sensor and period."
    )

else:

    displayed_anomalies = filtered_anomalies.sort_values(
        "anomaly_score",
        ascending=False
    )

    table_columns = [
        "sensor_id",
        "date",
        "daily_consumption",
        "event_count",
        "maximum_event_value",
        "anomaly_score",
        "anomaly_status"
    ]

    anomaly_table = displayed_anomalies[table_columns].round(5)
    anomaly_table_height = min(420, max(100, 38 * (len(anomaly_table) + 1)))

    st.dataframe(
        anomaly_table,
        width="stretch",
        hide_index=True,
        height=anomaly_table_height
    )

    st.download_button(
        "Download filtered anomaly report (CSV)",
        data=displayed_anomalies[
            table_columns
        ].to_csv(index=False).encode("utf-8"),
        file_name="aquasentinel_filtered_anomalies.csv",
        mime="text/csv"
    )

    st.caption(
        "The anomaly score is a model decision score, not a probability. "
        "Higher scores indicate observations considered more unusual "
        "by the fitted Isolation Forest."
    )


# ============================================================
# 13. SENSOR ANOMALY SUMMARY
# ============================================================

st.divider()

st.markdown("### Sensor Anomaly Summary")

st.caption(
    "Overall summary across all eligible dates and sensors; "
    "this table is independent of the explorer filters."
)


# Coverage is calculated from the source sensor-day dataset, not from
# modelled rows. This avoids understating coverage when feature rows are
# excluded because of missing model inputs.
calendar_start = df["date"].min().normalize()
calendar_end = df["date"].max().normalize()
expected_calendar_days = (calendar_end - calendar_start).days + 1

coverage_summary = (
    df.assign(date=df["date"].dt.normalize())
    .groupby("sensor_id")
    .agg(observed_days=("date", "nunique"))
    .reset_index()
)

coverage_summary["expected_calendar_days"] = expected_calendar_days
coverage_summary["coverage_pct"] = (
    coverage_summary["observed_days"]
    / expected_calendar_days
    * 100
)

sensor_summary = (
    anomalies.assign(
        flagged_anomaly_score=lambda frame: frame["anomaly_score"].where(
            frame["anomaly_status"].eq("Anomaly")
        )
    )
    .groupby("sensor_id")
    .agg(
        modelled_records=("anomaly_status", "size"),
        anomaly_count=(
            "anomaly_status",
            lambda values: (values == "Anomaly").sum()
        ),
        average_consumption=("daily_consumption", "mean"),
        maximum_consumption=("daily_consumption", "max"),
        mean_flagged_anomaly_score=("flagged_anomaly_score", "mean"),
        maximum_flagged_anomaly_score=("flagged_anomaly_score", "max")
    )
    .reset_index()
)

sensor_summary["anomaly_rate_pct"] = (
    sensor_summary["anomaly_count"]
    / sensor_summary["modelled_records"]
    * 100
)

sensor_summary = sensor_summary.merge(
    coverage_summary,
    on="sensor_id",
    how="left",
    validate="one_to_one"
)

sensor_summary = sensor_summary[
    [
        "sensor_id",
        "observed_days",
        "expected_calendar_days",
        "coverage_pct",
        "modelled_records",
        "anomaly_count",
        "average_consumption",
        "maximum_consumption",
        "mean_flagged_anomaly_score",
        "maximum_flagged_anomaly_score",
        "anomaly_rate_pct"
    ]
].sort_values(
    ["anomaly_count", "anomaly_rate_pct"],
    ascending=[False, False]
)

st.dataframe(
    sensor_summary.round(4),
    width="stretch",
    hide_index=True,
    height=min(520, max(120, 38 * (len(sensor_summary) + 1)))
)


st.download_button(
    "Download sensor summary (CSV)",
    data=sensor_summary.to_csv(index=False).encode("utf-8"),
    file_name="aquasentinel_sensor_anomaly_summary.csv",
    mime="text/csv"
)


# ============================================================
# 14. DETECTION METHODOLOGY
# ============================================================

st.divider()

st.markdown("### Detection Methodology")

st.write(
    """
    **Isolation Forest** is an unsupervised machine-learning algorithm
    that identifies observations that are easier to isolate from the
    rest of the data.

    AquaSentinel AI fits a separate model for each eligible sensor. The model
    uses daily recorded consumption, event frequency, mean and maximum
    event values, and change from the previous observed sensor record
    (which is not necessarily the previous calendar day).
    Observation coverage is calculated separately from the source sensor-day
    records; days without records are not treated as zero consumption.
    """
)


with st.expander("How should I interpret the anomaly score?"):

    st.write(
        """
        - Each eligible sensor-day is labelled Normal or Anomaly.
        - The anomaly score is derived from the model's decision function.
        - It is not a probability or a percentage chance of a leak.
        - Higher scores indicate observations that the fitted Isolation
          Forest considers more unusual.
        - Review the score alongside the sensor's consumption history,
          event count, and data coverage.
        """
    )


st.info(
    "An anomaly is an unusual recorded consumption pattern, "
    "not proof of a physical leak or infrastructure failure. "
    "Further investigation is required before assigning a cause."
)


st.caption(
    "Dataset: HSB Living Lab Water Consumption. "
    "Recorded consumption units are not asserted here because "
    "the source documentation contains a unit discrepancy."
)
