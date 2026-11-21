import sys
from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px


# ============================================================
# 1. CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Resource Optimization | AquaSentinel AI",
    page_icon="⚖️",
    layout="wide",
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.optimization.fair_allocator import benchmark_allocations


# ============================================================
# 2. SCENARIO DATA
# ============================================================

SCENARIOS = {
    "Normal Supply": (
        pd.DataFrame({
            "neighborhood": ["North", "South", "East"],
            "population": [1000, 1500, 800],
            "demand": [100.0, 150.0, 80.0],
            "essential_demand": [60.0, 90.0, 48.0],
            "priority_weight": [1.2, 1.0, 1.5],
        }),
        200.0,
    ),
    "Essential Shortage": (
        pd.DataFrame({
            "neighborhood": ["North", "South", "East"],
            "population": [1000, 1500, 800],
            "demand": [100.0, 150.0, 80.0],
            "essential_demand": [90.0, 60.0, 48.0],
            "priority_weight": [1.2, 1.0, 1.5],
        }),
        160.0,
    ),
    "Custom Scenario": (
        pd.DataFrame({
            "neighborhood": ["North", "South", "East"],
            "population": [1000, 1500, 800],
            "demand": [100.0, 150.0, 80.0],
            "essential_demand": [60.0, 90.0, 48.0],
            "priority_weight": [1.2, 1.0, 1.5],
        }),
        200.0,
    ),
}


# ============================================================
# 3. HEADER
# ============================================================

st.markdown(
    """
    <div style="color:#54D6C4;font-size:12px;
    font-weight:700;letter-spacing:1.5px;">
    EQUITABLE RESOURCE ALLOCATION
    </div>
    """,
    unsafe_allow_html=True,
)

st.title("Resource Optimization")

st.markdown(
    "Simulate neighbourhood-level water allocation using an "
    "**essential-needs-first strategy** and compare it with "
    "conventional proportional allocation."
)

st.divider()


# ============================================================
# 4. SCENARIO SELECTION
# ============================================================

st.subheader("Allocation Scenario")

scenario = st.radio(
    "Choose a simulation scenario",
    list(SCENARIOS.keys()),
    horizontal=True,
)

default_data, default_supply = SCENARIOS[scenario]

# Use a separate versioned widget key.
# Never assign directly to a key owned by st.data_editor.

if "allocation_scenario" not in st.session_state:
    st.session_state.allocation_scenario = None

if "editor_version" not in st.session_state:
    st.session_state.editor_version = 0

# Initialize supply_input even if the scenario has not changed.
if "supply_input" not in st.session_state:
    st.session_state.supply_input = default_supply

if st.session_state.allocation_scenario != scenario:
    if st.session_state.allocation_scenario is not None:
        st.session_state.editor_version += 1

    st.session_state.allocation_scenario = scenario
    st.session_state.supply_input = default_supply

editor_key = (
    f"neighborhood_editor_{st.session_state.editor_version}"
)

st.caption(
    "Demonstration neighbourhoods and inputs are synthetic, "
    "not live municipal measurements."
)


# ============================================================
# 5. INPUTS
# ============================================================

left, right = st.columns([1.5, 1])

with left:
    st.markdown("### Neighbourhood Parameters")

    edited_data = st.data_editor(
        default_data,
        key=editor_key,
        num_rows="dynamic",
        hide_index=True,
        width="stretch",
        column_config={
            "neighborhood": st.column_config.TextColumn(
                "Neighbourhood",
                required=True,
            ),
            "population": st.column_config.NumberColumn(
                "Population",
                min_value=1,
                step=100,
            ),
            "demand": st.column_config.NumberColumn(
                "Total Demand",
                min_value=0.0,
                step=1.0,
            ),
            "essential_demand": st.column_config.NumberColumn(
                "Essential Demand",
                min_value=0.0,
                step=1.0,
            ),
            "priority_weight": st.column_config.NumberColumn(
                "Priority Weight",
                min_value=0.01,
                step=0.1,
                format="%.2f",
            ),
        },
    )

with right:
    st.markdown("### Available Water Supply")

    available_supply = st.number_input(
        "Available supply (simulation units)",
        min_value=0.0,
        max_value=100000000.0,
        value=float(st.session_state.supply_input),
        step=10.0,
        key="supply_input",
    )

    total_demand = pd.to_numeric(
        edited_data["demand"], errors="coerce"
    ).fillna(0).sum()

    total_essential = pd.to_numeric(
        edited_data["essential_demand"], errors="coerce"
    ).fillna(0).sum()

    st.metric("Total Demand", f"{total_demand:,.2f}")
    st.metric("Essential Demand", f"{total_essential:,.2f}")

    if available_supply < total_essential:
        st.warning("Supply is below total essential demand.")
    elif available_supply < total_demand:
        st.info("Essential demand can be covered, but some demand remains unmet.")
    else:
        st.success("Supply can cover total demand.")


st.divider()


# ============================================================
# 6. CALCULATE ALLOCATION
# ============================================================

st.subheader("Allocation Results")

try:
    comparison, aqua_results, baseline_results = benchmark_allocations(
        edited_data,
        available_supply,
    )

except Exception as error:
    st.error(f"Unable to calculate allocation: {error}")
    st.stop()


aqua = dict(zip(comparison["Metric"], comparison["AquaSentinel"]))
baseline = dict(
    zip(comparison["Metric"], comparison["Proportional baseline"])
)


# ============================================================
# 7. KEY METRICS
# ============================================================

c1, c2, c3, c4 = st.columns(4)

c1.metric("Water Allocated", f"{aqua['Total allocated']:,.2f}")
c2.metric("Demand Satisfaction", f"{aqua['Demand satisfaction (%)']:.2f}%")
c3.metric(
    "Essential Coverage",
    f"{aqua['Essential satisfaction (%)']:.2f}%",
    delta=f"{aqua['Essential satisfaction (%)'] - baseline['Essential satisfaction (%)']:+.2f} pp",
)
c4.metric("Unmet Demand", f"{aqua['Unmet demand']:,.2f}")


# ============================================================
# 8. STRATEGY COMPARISON
# ============================================================

st.divider()
st.markdown("### Allocation Strategy Comparison")

display_comparison = comparison.copy()

for column in ["AquaSentinel", "Proportional baseline"]:
    display_comparison[column] = display_comparison[column].round(3)

st.dataframe(
    display_comparison,
    hide_index=True,
    width="stretch",
)


# ============================================================
# 9. ALLOCATION CHART
# ============================================================

st.markdown("### Neighbourhood Allocation")

chart_data = pd.DataFrame({
    "Neighbourhood": aqua_results["neighborhood"],
    "AquaSentinel": aqua_results["allocated_water"],
    "Proportional Baseline": baseline_results["allocated_water"],
})

chart_long = chart_data.melt(
    id_vars="Neighbourhood",
    var_name="Strategy",
    value_name="Allocated Water",
)

fig = px.bar(
    chart_long,
    x="Neighbourhood",
    y="Allocated Water",
    color="Strategy",
    barmode="group",
    title="Water Allocation by Neighbourhood",
)

fig.update_layout(height=420)

st.plotly_chart(fig, use_container_width=True)


# ============================================================
# 10. ESSENTIAL COVERAGE CHART
# ============================================================

st.markdown("### Essential Demand Protection")

essential_data = pd.DataFrame({
    "Neighbourhood": aqua_results["neighborhood"],
    "AquaSentinel": aqua_results["essential_satisfaction_pct"],
    "Proportional Baseline": baseline_results["essential_satisfaction_pct"],
})

essential_long = essential_data.melt(
    id_vars="Neighbourhood",
    var_name="Strategy",
    value_name="Essential Satisfaction (%)",
)

fig2 = px.bar(
    essential_long,
    x="Neighbourhood",
    y="Essential Satisfaction (%)",
    color="Strategy",
    barmode="group",
    range_y=[0, 105],
    title="Essential Demand Satisfaction by Neighbourhood",
)

fig2.update_layout(height=420)

st.plotly_chart(fig2, use_container_width=True)


# ============================================================
# 11. DETAILED RESULTS
# ============================================================

st.divider()
st.markdown("### Detailed Allocation Results")

detail = aqua_results[
    [
        "neighborhood",
        "population",
        "demand",
        "essential_demand",
        "priority_weight",
        "allocated_water",
        "unmet_demand",
        "demand_satisfaction_pct",
        "essential_satisfaction_pct",
        "water_per_person",
    ]
].rename(columns={
    "neighborhood": "Neighbourhood",
    "population": "Population",
    "demand": "Total Demand",
    "essential_demand": "Essential Demand",
    "priority_weight": "Priority Weight",
    "allocated_water": "Allocated Water",
    "unmet_demand": "Unmet Demand",
    "demand_satisfaction_pct": "Demand Satisfaction (%)",
    "essential_satisfaction_pct": "Essential Satisfaction (%)",
    "water_per_person": "Water per Person",
})

st.dataframe(
    detail.round(3),
    hide_index=True,
    width="stretch",
)

st.download_button(
    "Download allocation results (CSV)",
    data=detail.to_csv(index=False).encode("utf-8"),
    file_name="aquasentinel_resource_allocation.csv",
    mime="text/csv",
)


# ============================================================
# 12. FAIRNESS ANALYSIS
# ============================================================

st.divider()
st.markdown("### Fairness Analysis")

essential_difference = (
    aqua["Essential satisfaction (%)"]
    - baseline["Essential satisfaction (%)"]
)

if essential_difference > 0:
    st.success(
        f"AquaSentinel improves essential-demand coverage by "
        f"{essential_difference:.2f} percentage points."
    )
elif essential_difference < 0:
    st.warning(
        "The proportional baseline has higher aggregate "
        "essential-demand coverage in this scenario."
    )
else:
    st.info(
        "Both strategies achieve equal aggregate essential-demand coverage."
    )

st.write(
    f"""
    - Minimum neighbourhood demand satisfaction:
      {aqua['Minimum neighborhood satisfaction (%)']:.2f}% (AquaSentinel)
      vs {baseline['Minimum neighborhood satisfaction (%)']:.2f}% (baseline).
    - Demand satisfaction disparity:
      {aqua['Satisfaction disparity (%)']:.2f} pp (AquaSentinel)
      vs {baseline['Satisfaction disparity (%)']:.2f} pp (baseline).
    - Jain fairness index:
      {aqua['Jain fairness index']:.4f} (AquaSentinel)
      vs {baseline['Jain fairness index']:.4f} (baseline).
    """
)

st.caption(
    "Jain's index measures equality of total-demand satisfaction rates. "
    "Essential coverage measures protection of essential requirements. "
    "Neither metric alone establishes complete social equity."
)


# ============================================================
# 13. METHODOLOGY AND LIMITATIONS
# ============================================================

with st.expander("Allocation Methodology"):
    st.markdown(
        """
        **Stage 1 — Essential demand protection**

        Essential requirements are prioritised first. If available
        supply is insufficient, it is distributed proportionally
        to essential demand.

        **Stage 2 — Weighted allocation**

        Remaining supply is distributed using priority weights,
        subject to each neighbourhood's remaining demand.

        **Baseline — Proportional allocation**

        Available supply is distributed in proportion to total demand.

        **Priority weights**

        These are explicit policy inputs, not automatically inferred
        from population, income, or vulnerability.
        """
    )

st.info(
    "This is a synthetic resource-allocation simulation. The HSB Living "
    "Lab dataset contains household/fixture-level consumption records, "
    "not live city-wide reservoir or pipeline telemetry. This prototype "
    "does not control real water infrastructure."
)
