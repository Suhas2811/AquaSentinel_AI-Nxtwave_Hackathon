
import numpy as np
import pandas as pd


REQUIRED_COLUMNS = [
    "neighborhood",
    "population",
    "demand",
    "essential_demand",
    "priority_weight",
]

EPSILON = 1e-10


def _validate_inputs(neighborhoods, available_supply):
    if not isinstance(neighborhoods, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame.")

    if neighborhoods.empty:
        raise ValueError("At least one neighborhood is required.")

    missing = set(REQUIRED_COLUMNS) - set(neighborhoods.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    available_supply = float(available_supply)

    if not np.isfinite(available_supply) or available_supply < 0:
        raise ValueError("Available supply must be finite and non-negative.")

    df = neighborhoods[REQUIRED_COLUMNS].copy().reset_index(drop=True)

    if df["neighborhood"].isna().any():
        raise ValueError("Neighborhood names cannot be missing.")

    if df["neighborhood"].duplicated().any():
        raise ValueError("Neighborhood names must be unique.")

    numeric_columns = [
        "population",
        "demand",
        "essential_demand",
        "priority_weight",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="raise")

    values = df[numeric_columns].to_numpy(dtype=float)

    if not np.isfinite(values).all():
        raise ValueError("All numeric inputs must be finite.")

    if (df[numeric_columns] < 0).any().any():
        raise ValueError("Numeric inputs cannot be negative.")

    if (df["population"] <= 0).any():
        raise ValueError("Population must be greater than zero.")

    if (df["priority_weight"] <= 0).any():
        raise ValueError("Priority weights must be positive.")

    if (df["essential_demand"] > df["demand"]).any():
        raise ValueError("Essential demand cannot exceed total demand.")

    return df, available_supply


def _build_result(df, allocation):
    result = df.copy()

    demand = result["demand"].to_numpy(dtype=float)
    essential = result["essential_demand"].to_numpy(dtype=float)
    population = result["population"].to_numpy(dtype=float)

    allocation = np.asarray(allocation, dtype=float)

    result["allocated_water"] = allocation
    result["unmet_demand"] = np.maximum(demand - allocation, 0)

    result["demand_satisfaction_pct"] = np.where(
        demand > EPSILON,
        allocation / np.maximum(demand, EPSILON) * 100,
        100.0,
    )

    essential_delivered = np.minimum(allocation, essential)

    result["essential_satisfaction_pct"] = np.where(
        essential > EPSILON,
        essential_delivered / np.maximum(essential, EPSILON) * 100,
        100.0,
    )

    result["water_per_person"] = allocation / population

    return result


def _calculate_metrics(result, available_supply):
    satisfaction = (
        result["demand_satisfaction_pct"].to_numpy(dtype=float) / 100
    )

    demand = result["demand"].to_numpy(dtype=float)
    essential = result["essential_demand"].to_numpy(dtype=float)
    allocation = result["allocated_water"].to_numpy(dtype=float)

    total_demand = float(demand.sum())
    total_allocated = float(allocation.sum())
    total_essential = float(essential.sum())

    essential_delivered = float(np.minimum(allocation, essential).sum())

    # Jain's index: 1.0 represents equal satisfaction rates.
    # This is calculated across neighbourhoods, not people.
    squared_sum = float(np.square(satisfaction).sum())

    jain_index = (
        float(satisfaction.sum() ** 2 / (len(satisfaction) * squared_sum))
        if squared_sum > EPSILON
        else 1.0
    )

    metrics = {
        "available_supply": available_supply,
        "total_demand": total_demand,
        "total_allocated": total_allocated,
        "total_unmet_demand": float(result["unmet_demand"].sum()),
        "supply_utilization_pct": (
            total_allocated / available_supply * 100
            if available_supply > EPSILON else 0.0
        ),
        "overall_demand_satisfaction_pct": (
            total_allocated / total_demand * 100
            if total_demand > EPSILON else 100.0
        ),
        "essential_satisfaction_pct": (
            essential_delivered / total_essential * 100
            if total_essential > EPSILON else 100.0
        ),
        "minimum_neighborhood_satisfaction_pct": float(
            result["demand_satisfaction_pct"].min()
        ),
        "maximum_neighborhood_satisfaction_pct": float(
            result["demand_satisfaction_pct"].max()
        ),
        "satisfaction_disparity_pct": float(
            result["demand_satisfaction_pct"].max()
            - result["demand_satisfaction_pct"].min()
        ),
        "jain_fairness_index": jain_index,
        "minimum_water_per_person": float(
            result["water_per_person"].min()
        ),
        "maximum_water_per_person": float(
            result["water_per_person"].max()
        ),
    }

    return metrics


def allocate_water(neighborhoods, available_supply):
    """
    Essential-needs-first, weighted allocation.

    Priority weights influence distribution of remaining supply.
    Population is used for per-capita reporting, not as an automatic
    vulnerability score. Set priority weights using documented,
    transparent criteria.
    """

    df, supply = _validate_inputs(neighborhoods, available_supply)

    demand = df["demand"].to_numpy(dtype=float)
    essential = df["essential_demand"].to_numpy(dtype=float)
    weights = df["priority_weight"].to_numpy(dtype=float)

    allocation = np.zeros(len(df), dtype=float)

    essential_total = float(essential.sum())

    # Stage 1: Essential requirements.
    if supply <= essential_total:
        if essential_total > EPSILON:
            allocation = supply * essential / essential_total
        remaining_supply = 0.0
    else:
        allocation = essential.copy()
        remaining_supply = supply - essential_total

    # Stage 2: Weighted redistribution of remaining supply.
    remaining_demand = np.maximum(demand - allocation, 0.0)

    while remaining_supply > EPSILON:
        active = remaining_demand > EPSILON

        if not active.any():
            break

        active_weights = weights[active]
        proposed = (
            remaining_supply * active_weights / active_weights.sum()
        )

        actual = np.minimum(proposed, remaining_demand[active])
        distributed = float(actual.sum())

        if distributed <= EPSILON:
            break

        allocation[active] += actual
        remaining_demand[active] -= actual
        remaining_supply = max(remaining_supply - distributed, 0.0)

    result = _build_result(df, allocation)
    metrics = _calculate_metrics(result, supply)

    if metrics["total_allocated"] > supply + 1e-7:
        raise RuntimeError("Allocation exceeded available supply.")

    if (result["allocated_water"] > result["demand"] + 1e-7).any():
        raise RuntimeError("Allocation exceeded neighborhood demand.")

    return result, metrics


def proportional_allocation(neighborhoods, available_supply):
    """
    Baseline: allocate supply in proportion to total demand.
    This baseline does not protect essential demand separately.
    """

    df, supply = _validate_inputs(neighborhoods, available_supply)

    demand = df["demand"].to_numpy(dtype=float)
    total_demand = float(demand.sum())

    if total_demand <= EPSILON:
        allocation = np.zeros(len(df), dtype=float)
    else:
        allocation = (
            min(supply, total_demand) * demand / total_demand
        )

    result = _build_result(df, allocation)
    metrics = _calculate_metrics(result, supply)

    return result, metrics


def benchmark_allocations(neighborhoods, available_supply):
    """
    Compare AquaSentinel's allocation with proportional allocation.

    Returns:
        comparison_table, aqua_results, baseline_results
    """

    aqua_results, aqua_metrics = allocate_water(
        neighborhoods, available_supply
    )

    baseline_results, baseline_metrics = proportional_allocation(
        neighborhoods, available_supply
    )

    comparison = pd.DataFrame({
        "Metric": [
            "Total allocated",
            "Unmet demand",
            "Demand satisfaction (%)",
            "Essential satisfaction (%)",
            "Minimum neighborhood satisfaction (%)",
            "Satisfaction disparity (%)",
            "Jain fairness index",
        ],
        "AquaSentinel": [
            aqua_metrics["total_allocated"],
            aqua_metrics["total_unmet_demand"],
            aqua_metrics["overall_demand_satisfaction_pct"],
            aqua_metrics["essential_satisfaction_pct"],
            aqua_metrics["minimum_neighborhood_satisfaction_pct"],
            aqua_metrics["satisfaction_disparity_pct"],
            aqua_metrics["jain_fairness_index"],
        ],
        "Proportional baseline": [
            baseline_metrics["total_allocated"],
            baseline_metrics["total_unmet_demand"],
            baseline_metrics["overall_demand_satisfaction_pct"],
            baseline_metrics["essential_satisfaction_pct"],
            baseline_metrics["minimum_neighborhood_satisfaction_pct"],
            baseline_metrics["satisfaction_disparity_pct"],
            baseline_metrics["jain_fairness_index"],
        ],
    })

    return comparison, aqua_results, baseline_results
