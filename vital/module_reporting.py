"""
module_reporting.py

Lightweight reporting helpers for exporting VITAL LCOE and optimization
results to stakeholder-readable Markdown and machine-readable CSV files.
"""

from pathlib import Path
import pandas as pd
import numpy as np


def _is_finite_number(value):
    """Return True if value can be safely treated as a finite number."""
    try:
        return np.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _format_money(value):
    """Format a numeric value as USD."""
    if value is None or not _is_finite_number(value):
        return "N/A"
    return f"${float(value):,.2f}"


def _format_float(value, digits=4):
    """Format a numeric value safely."""
    if value is None or not _is_finite_number(value):
        return "N/A"
    return f"{float(value):.{digits}f}"


def summarize_lcoe(calculator):
    """
    Create a flat summary dictionary from an LCOECalculator.

    Args:
        calculator: An initialized vital.module_lcoe.LCOECalculator object.

    Returns:
        dict: Summary values suitable for CSV, Markdown, or display.
    """
    adjusted_capex = calculator.calculate_total_capex()
    annual_opex = calculator.calculate_total_opex(adjusted_capex)
    annual_energy = calculator.calculate_annual_energy()
    capacity_factor = calculator.calculate_capacity_factor()
    lcoe = calculator.calculate_lcoe()

    capex_summary = calculator.get_capex_summary()

    summary = {
        "customer": calculator.data.customer,
        "application": calculator.data.application,
        "lcoe_usd_per_kwh": lcoe,
        "annual_energy_kwh": annual_energy,
        "capacity_factor": capacity_factor,
        "component_capex_usd": capex_summary["component_capex"],
        "capex_adjustment_factor": capex_summary["adjustment_factor"],
        "adjusted_capex_usd": capex_summary["adjusted_capex"],
        "annual_opex_usd": annual_opex,
        "lifetime_years": calculator.data.lifetime,
        "discount_rate": calculator.data.discount_rate,
        "turbulence_intensity": calculator.data.turbulence_intensity,
        "turbine_radius_m": calculator.data.turbine_radius,
        "turbine_rated_power_w": calculator.data.turbine_rated_power,
        "number_of_turbines": calculator.data.number_of_turbines,
        "hub_depth_m": calculator.data.hub_depth,
        "cable_length_m": calculator.data.dCable,
        "mooring_depth_m": calculator.data.dMoor,
        "battery_capacity_kwh": calculator.data.Battery,
    }

    for name, value in capex_summary["capex_items"].items():
        summary[f"capex_{name}_usd"] = value

    return summary


def lcoe_summary_to_markdown(summary):
    """
    Convert an LCOE summary dictionary to Markdown.

    Args:
        summary (dict): Output from summarize_lcoe.

    Returns:
        str: Markdown report text.
    """
    lines = []
    lines.append("# VITAL LCOE Summary")
    lines.append("")
    lines.append("## Project Configuration")
    lines.append("")
    lines.append(f"- Customer: `{summary.get('customer')}`")
    lines.append(f"- Application: `{summary.get('application')}`")
    lines.append(f"- Lifetime: {summary.get('lifetime_years')} years")
    lines.append(f"- Discount rate: {_format_float(summary.get('discount_rate'), 3)}")
    lines.append(f"- Turbulence intensity: {_format_float(summary.get('turbulence_intensity'), 3)}")
    lines.append("")

    lines.append("## Key Results")
    lines.append("")
    lines.append(f"- LCOE: **${summary['lcoe_usd_per_kwh']:.4f}/kWh**")
    lines.append(f"- Annual energy: **{summary['annual_energy_kwh']:,.2f} kWh/year**")
    lines.append(f"- Capacity factor: **{summary['capacity_factor']:.4f}**")
    lines.append(f"- Adjusted CAPEX: **{_format_money(summary['adjusted_capex_usd'])}**")
    lines.append(f"- Annual OPEX: **{_format_money(summary['annual_opex_usd'])}**")
    lines.append("")

    lines.append("## Turbine and Site Inputs")
    lines.append("")
    lines.append(f"- Turbine radius: {summary.get('turbine_radius_m')} m")
    lines.append(f"- Rated power: {summary.get('turbine_rated_power_w')} W")
    lines.append(f"- Number of turbines: {summary.get('number_of_turbines')}")
    lines.append(f"- Hub depth: {summary.get('hub_depth_m')} m")
    lines.append(f"- Cable length: {summary.get('cable_length_m')} m")
    lines.append(f"- Mooring depth: {summary.get('mooring_depth_m')} m")
    lines.append(f"- Battery capacity: {summary.get('battery_capacity_kwh')} kWh")
    lines.append("")

    lines.append("## CAPEX Breakdown")
    lines.append("")
    lines.append("| Component | Cost |")
    lines.append("|---|---:|")

    capex_items = {
        key.replace("capex_", "").replace("_usd", ""): value
        for key, value in summary.items()
        if key.startswith("capex_") and key.endswith("_usd")
    }

    for name, value in capex_items.items():
        lines.append(f"| {name} | {_format_money(value)} |")

    lines.append(f"| **Component CAPEX total** | **{_format_money(summary['component_capex_usd'])}** |")
    lines.append(f"| **Adjustment factor** | **{summary['capex_adjustment_factor']:.3f}** |")
    lines.append(f"| **Adjusted CAPEX** | **{_format_money(summary['adjusted_capex_usd'])}** |")
    lines.append("")

    lines.append("## Notes")
    lines.append("")
    lines.append(
        "This report is intended for screening-level comparison and stakeholder "
        "communication. It should not be interpreted as a final engineering, "
        "permitting, or deployment recommendation."
    )
    lines.append("")

    return "\n".join(lines)


def export_lcoe_report(calculator, output_prefix="vital_lcoe_summary"):
    """
    Export an LCOE summary to Markdown and CSV.

    Args:
        calculator: vital.module_lcoe.LCOECalculator object.
        output_prefix (str): Output path without extension.

    Returns:
        dict: Paths to generated files.
    """
    output_prefix = Path(output_prefix)
    output_prefix.parent.mkdir(parents=True, exist_ok=True)

    summary = summarize_lcoe(calculator)

    csv_path = output_prefix.with_suffix(".csv")
    md_path = output_prefix.with_suffix(".md")

    pd.DataFrame([summary]).to_csv(csv_path, index=False)

    markdown = lcoe_summary_to_markdown(summary)
    md_path.write_text(markdown, encoding="utf-8")

    return {
        "summary": summary,
        "csv": str(csv_path),
        "markdown": str(md_path),
    }


def summarize_optimization_result(opt_result):
    """
    Create a compact summary from an LCOEOptimizer result dictionary.

    Args:
        opt_result (dict): Output from LCOEOptimizer.optimize.

    Returns:
        dict: Summary suitable for CSV, Markdown, or display.
    """
    results_table = opt_result["results_table"]
    feasible_table = opt_result["feasible_table"]

    summary = {
        "optimal_lcoe_usd_per_kwh": opt_result["optimal_lcoe"],
        "total_designs": len(results_table),
        "feasible_designs": len(feasible_table),
        "infeasible_designs": len(results_table) - len(feasible_table),
        "feasible_fraction": len(feasible_table) / len(results_table) if len(results_table) > 0 else np.nan,
    }

    for name, value in opt_result["optimal_params"].items():
        summary[f"optimal_{name}"] = value

    for name, value in opt_result.get("fixed_params", {}).items():
        summary[f"fixed_{name}"] = value

    for name, value in opt_result.get("site_params", {}).items():
        if np.isscalar(value):
            summary[f"site_{name}"] = value

    return summary


def optimization_summary_to_markdown(summary):
    """
    Convert an optimization summary dictionary to Markdown.

    Args:
        summary (dict): Output from summarize_optimization_result.

    Returns:
        str: Markdown report text.
    """
    lines = []
    lines.append("# VITAL Optimization Summary")
    lines.append("")

    lines.append("## Key Results")
    lines.append("")
    lines.append(f"- Optimal LCOE: **${summary['optimal_lcoe_usd_per_kwh']:.4f}/kWh**")
    lines.append(f"- Feasible designs: **{summary['feasible_designs']} of {summary['total_designs']}**")
    lines.append(f"- Feasible fraction: **{summary['feasible_fraction']:.3f}**")
    lines.append("")

    lines.append("## Optimal Design Variables")
    lines.append("")
    lines.append("| Variable | Value |")
    lines.append("|---|---:|")

    for key, value in summary.items():
        if key.startswith("optimal_") and key != "optimal_lcoe_usd_per_kwh":
            variable = key.replace("optimal_", "")
            lines.append(f"| {variable} | {value} |")

    lines.append("")

    lines.append("## Notes")
    lines.append("")
    lines.append(
        "Infeasible designs are excluded from the feasible-design count. "
        "This optimization summary is intended for screening-level design "
        "comparison and should be reviewed alongside constraint results and "
        "model assumptions."
    )
    lines.append("")

    return "\n".join(lines)


def export_optimization_report(opt_result, output_prefix="vital_optimization_summary"):
    """
    Export an optimization summary and optimization tables.

    Args:
        opt_result (dict): Output from LCOEOptimizer.optimize.
        output_prefix (str): Output path without extension.

    Returns:
        dict: Paths to generated files.
    """
    output_prefix = Path(output_prefix)
    output_prefix.parent.mkdir(parents=True, exist_ok=True)

    summary = summarize_optimization_result(opt_result)

    summary_csv_path = output_prefix.with_suffix(".csv")
    md_path = output_prefix.with_suffix(".md")

    full_results_path = output_prefix.with_name(output_prefix.name + "_all_designs").with_suffix(".csv")
    feasible_results_path = output_prefix.with_name(output_prefix.name + "_feasible_designs").with_suffix(".csv")

    pd.DataFrame([summary]).to_csv(summary_csv_path, index=False)
    opt_result["results_table"].to_csv(full_results_path, index=False)
    opt_result["feasible_table"].to_csv(feasible_results_path, index=False)

    markdown = optimization_summary_to_markdown(summary)
    md_path.write_text(markdown, encoding="utf-8")

    return {
        "summary": summary,
        "summary_csv": str(summary_csv_path),
        "markdown": str(md_path),
        "all_designs_csv": str(full_results_path),
        "feasible_designs_csv": str(feasible_results_path),
    }