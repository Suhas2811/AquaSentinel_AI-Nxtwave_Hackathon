
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px


st.set_page_config(
    page_title="Crisis Simulator | AquaSentinel AI",
    page_icon="🚨",
    layout="wide",
)

# ------------------------------------------------------------
# HEADER
# ------------------------------------------------------------

st.markdown(
    """
    <div style="color:#54D6C4;font-size:12px;
    font-weight:700;letter-spacing:1.5px;">
    URBAN WATER INTELLIGENCE PLATFORM
    </div>
    """,
    unsafe_allow_html=True,
)

st.title("Water Crisis Simulator")

st.markdown(
    """
    Simulate urban water shortages, assess neighbourhood-level
    impacts and explore supply recovery strategies.
    """
)

st.divider()

# ------------------------------------------------------------
# SYNTHETIC NEIGHBOURHOOD DATA
# ------------------------------------------------------------

base = pd.DataFrame({
    "Neighbourhood": ["North", "South", "East"],
    "Population": [1000, 1500, 800],
    "Daily Demand": [100.0, 150.0, 80.0],
    "Essential Demand": [60.0, 90.0, 48.0],
    "Priority Weight": [1.2, 1.0, 1.5],
})

TOTAL_DEMAND = float(base["Daily Demand"].sum())
TOTAL_ESSENTIAL = float(base["Essential Demand"].sum())

# ------------------------------------------------------------
# CRISIS CONTROLS
# ------------------------------------------------------------

st.subheader("Crisis Configuration")

left, right = st.columns(2)

with left:
    crisis_type = st.selectbox(
        "Crisis scenario",
        [
            "Moderate Shortage",
            "Severe Drought",
            "Reservoir Failure",
            "Custom Crisis",
        ],
    )

    presets = {
        "Moderate Shortage": 75,
        "Severe Drought": 50,
        "Reservoir Failure": 30,
        "Custom Crisis": 60,
    }

    default_supply = presets[crisis_type]

    supply_percent = st.slider(
        "Available water supply (% of normal demand)",
        min_value=10,
        max_value=100,
        value=default_supply,
        step=5,
    )

with right:
    recovery_rate = st.slider(
        "Daily supply recovery rate (% points)",
        min_value=0,
        max_value=20,
        value=8,
        step=1,
    )

    simulation_days = st.slider(
        "Recovery simulation period (days)",
        min_value=3,
        max_value=14,
        value=7,
    )

    st.caption(
        "Recovery rate represents an assumed daily increase in "
        "supply availability, not a measured reservoir forecast."
    )

st.caption(
    "All neighbourhood, demand, supply and recovery inputs in "
    "this demonstration are synthetic."
)

# ------------------------------------------------------------
# ALLOCATION ENGINE
# ------------------------------------------------------------

def allocate_essential_first(data, supply):
    demand = data["Daily Demand"].to_numpy(dtype=float)
    essential = data["Essential Demand"].to_numpy(dtype=float)
    weights = data["Priority Weight"].to_numpy(dtype=float)

    allocation = np.zeros(len(data), dtype=float)

    essential_total = essential.sum()

    if supply <= essential_total:
        if essential_total > 0:
            allocation = supply * essential / essential_total
    else:
        allocation = essential.copy()
        remaining = supply - essential_total

        while remaining > 1e-9:
            unmet = np.maximum(demand - allocation, 0)
            active = unmet > 1e-9

            if not active.any():
                break

            shares = remaining * weights[active] / weights[active].sum()
            actual = np.minimum(shares, unmet[active])

            distributed = actual.sum()

            if distributed <= 1e-9:
                break

            allocation[active] += actual
            remaining -= distributed

    return allocation


def build_results(data, supply):
    result = data.copy()

    allocation = allocate_essential_first(data, supply)

    result["Allocated Water"] = allocation
    result["Unmet Demand"] = np.maximum(
        result["Daily Demand"].to_numpy() - allocation, 0
    )

    result["Demand Satisfaction (%)"] = np.where(
        result["Daily Demand"] > 0,
        allocation / result["Daily Demand"] * 100,
        100,
    )

    essential_delivered = np.minimum(
        allocation,
        result["Essential Demand"].to_numpy(),
    )

    result["Essential Coverage (%)"] = np.where(
        result["Essential Demand"] > 0,
        essential_delivered / result["Essential Demand"] * 100,
        100,
    )

    return result


# ------------------------------------------------------------
# SIMULATE CRISIS
# ------------------------------------------------------------

available_supply = TOTAL_DEMAND * supply_percent / 100

results = build_results(base, available_supply)

total_allocated = results["Allocated Water"].sum()
total_unmet = results["Unmet Demand"].sum()

overall_satisfaction = (
    total_allocated / TOTAL_DEMAND * 100
)

essential_delivered = np.minimum(
    results["Allocated Water"],
    results["Essential Demand"],
).sum()

essential_coverage = (
    essential_delivered / TOTAL_ESSENTIAL * 100
)

# ------------------------------------------------------------
# CRISIS STATUS
# ------------------------------------------------------------

st.divider()
st.subheader("Crisis Impact Assessment")

if supply_percent >= 90:
    st.success("Normal operating conditions")
elif supply_percent >= 70:
    st.warning("Moderate water shortage")
elif supply_percent >= 45:
    st.error("Severe water shortage")
else:
    st.error("Critical water emergency")

m1, m2, m3, m4 = st.columns(4)

m1.metric(
    "Available Supply",
    f"{available_supply:.1f}",
    f"{supply_percent}% of normal",
)

m2.metric(
    "Unmet Demand",
    f"{total_unmet:.1f}",
)

m3.metric(
    "Demand Satisfaction",
    f"{overall_satisfaction:.1f}%",
)

m4.metric(
    "Essential Coverage",
    f"{essential_coverage:.1f}%",
)

# ------------------------------------------------------------
# NEIGHBOURHOOD IMPACT
# ------------------------------------------------------------

st.divider()
st.subheader("Neighbourhood-wise Crisis Impact")

fig = px.bar(
    results,
    x="Neighbourhood",
    y=["Allocated Water", "Unmet Demand"],
    barmode="group",
    title="Daily Water Allocation and Unmet Demand",
)

fig.update_layout(height=420)

st.plotly_chart(fig, use_container_width=True)

st.markdown("### Neighbourhood Impact Table")

st.dataframe(
    results[
        [
            "Neighbourhood",
            "Population",
            "Daily Demand",
            "Essential Demand",
            "Allocated Water",
            "Unmet Demand",
            "Demand Satisfaction (%)",
            "Essential Coverage (%)",
        ]
    ].round(2),
    hide_index=True,
    use_container_width=True,
)

# ------------------------------------------------------------
# RECOVERY SIMULATION
# ------------------------------------------------------------

st.divider()
st.subheader("Seven-Day Supply Recovery Simulation")

recovery_data = []

for day in range(simulation_days + 1):
    projected_percent = min(
        supply_percent + day * recovery_rate,
        100,
    )

    projected_supply = TOTAL_DEMAND * projected_percent / 100

    projected_results = build_results(
        base,
        projected_supply,
    )

    projected_allocated = projected_results[
        "Allocated Water"
    ].sum()

    projected_essential = np.minimum(
        projected_results["Allocated Water"],
        projected_results["Essential Demand"],
    ).sum()

    recovery_data.append({
        "Day": day,
        "Supply Availability (%)": projected_percent,
        "Available Supply": projected_supply,
        "Unmet Demand": (
            TOTAL_DEMAND - projected_allocated
        ),
        "Essential Coverage (%)": (
            projected_essential / TOTAL_ESSENTIAL * 100
        ),
    })

recovery_df = pd.DataFrame(recovery_data)

fig_recovery = px.line(
    recovery_df,
    x="Day",
    y=[
        "Supply Availability (%)",
        "Essential Coverage (%)",
    ],
    markers=True,
    title="Supply Recovery and Essential Coverage",
)

fig_recovery.update_layout(height=420)

st.plotly_chart(
    fig_recovery,
    use_container_width=True,
)

st.dataframe(
    recovery_df.round(2),
    hide_index=True,
    use_container_width=True,
)

# ------------------------------------------------------------
# CRISIS RECOMMENDATIONS
# ------------------------------------------------------------

st.divider()
st.subheader("Recommended Crisis Response")

if essential_coverage < 60:
    st.error(
        "Critical recommendation: Activate emergency water "
        "distribution, protect essential services and arrange "
        "additional supply."
    )

elif essential_coverage < 100:
    st.warning(
        "Prioritise essential water requirements, deploy "
        "supplementary supply and monitor vulnerable neighbourhoods."
    )

elif total_unmet > 0:
    st.info(
        "Essential requirements are covered. Continue controlled "
        "allocation and monitor non-essential demand."
    )

else:
    st.success(
        "Available supply covers all modelled demand. "
        "Maintain monitoring and reserve capacity."
    )

st.markdown(
    """
    **Suggested response actions**

    - Prioritise drinking water and essential household needs.
    - Monitor neighbourhood-level supply and unmet demand.
    - Coordinate supplementary tanker or reservoir supply.
    - Track recovery before returning to normal allocation.
    """
)

st.caption(
    "Simulation disclaimer: This is a decision-support prototype "
    "using synthetic scenarios. It does not predict actual droughts, "
    "measure live reservoirs or operate municipal infrastructure."
)

st.download_button(
    "Download crisis simulation results",
    data=recovery_df.to_csv(index=False).encode("utf-8"),
    file_name="aquasentinel_crisis_simulation.csv",
    mime="text/csv",
)
