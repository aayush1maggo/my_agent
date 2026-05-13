"""GA4 Visualization Tools for SEO Agent.

These tools build on top of the core GA4 data tools and generate
Seaborn/Matplotlib charts that can be referenced in reports.

They are designed for use by the analytics_agent (DataInsight) to
quickly visualize key event performance and the pages driving those
events, including year-over-year comparisons.
"""
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from .ga4_tools import get_ga4_metrics


DEFAULT_CHART_DIR = Path("ga4_charts")


def _ensure_output_path(filename: Optional[str]) -> Path:
    """Ensure the output directory exists and return a full path."""
    DEFAULT_CHART_DIR.mkdir(parents=True, exist_ok=True)

    if filename:
        return DEFAULT_CHART_DIR / filename

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return DEFAULT_CHART_DIR / f"ga4_chart_{timestamp}.png"


def plot_ga4_event_yoy_bar(
    property_id: str,
    current_start_date: str,
    current_end_date: str,
    previous_start_date: str,
    previous_end_date: str,
    metric: str = "conversions",
    top_n: int = 20,
    output_filename: Optional[str] = None,
) -> Dict:
    """Plot year-over-year performance for key events as a bar chart.

    This tool fetches GA4 data for two periods and generates a side-by-side
    bar chart comparing the chosen metric for each eventName.

    Args:
        property_id: GA4 property ID ('123456789' or 'properties/123456789').
        current_start_date: Start of the current period (YYYY-MM-DD or NdaysAgo).
        current_end_date: End of the current period.
        previous_start_date: Start of the comparison period.
        previous_end_date: End of the comparison period.
        metric: Metric to plot (e.g. 'conversions', 'eventCount').
        top_n: Number of top events (by current period metric) to show.
        output_filename: Optional filename for the chart (saved under ga4_charts/).

    Returns:
        Dict with chart_path and summary statistics.
    """
    # Fetch current period data
    current = get_ga4_metrics(
        property_id=property_id,
        start_date=current_start_date,
        end_date=current_end_date,
        metrics=[metric],
        dimensions=["eventName"],
    )

    # Fetch previous period data
    previous = get_ga4_metrics(
        property_id=property_id,
        start_date=previous_start_date,
        end_date=previous_end_date,
        metrics=[metric],
        dimensions=["eventName"],
    )

    current_df = pd.DataFrame(current.get("rows", []))
    previous_df = pd.DataFrame(previous.get("rows", []))

    if current_df.empty and previous_df.empty:
        return {"error": "No GA4 data available for the selected periods."}

    # Ensure metric is numeric
    for df in (current_df, previous_df):
        if not df.empty and metric in df.columns:
            df[metric] = pd.to_numeric(df[metric], errors="coerce").fillna(0)

    # Aggregate by eventName
    current_agg = (
        current_df.groupby("eventName", as_index=False)[metric].sum()
        if not current_df.empty
        else pd.DataFrame(columns=["eventName", metric])
    )
    previous_agg = (
        previous_df.groupby("eventName", as_index=False)[metric].sum()
        if not previous_df.empty
        else pd.DataFrame(columns=["eventName", metric])
    )

    current_agg.rename(columns={metric: "current"}, inplace=True)
    previous_agg.rename(columns={metric: "previous"}, inplace=True)

    merged = pd.merge(current_agg, previous_agg, on="eventName", how="outer").fillna(0)

    if merged.empty:
        return {"error": "No GA4 event data after aggregation."}

    # Limit to top N events by current metric
    merged["current"] = pd.to_numeric(merged["current"], errors="coerce").fillna(0)
    merged["previous"] = pd.to_numeric(merged["previous"], errors="coerce").fillna(0)
    merged.sort_values("current", ascending=False, inplace=True)
    top_events = merged.head(top_n)

    # Melt for plotting
    plot_df = top_events.melt(
        id_vars="eventName",
        value_vars=["current", "previous"],
        var_name="period",
        value_name="value",
    )

    # Create chart
    sns.set(style="whitegrid")
    plt.figure(figsize=(12, 6))
    ax = sns.barplot(
        data=plot_df,
        x="eventName",
        y="value",
        hue="period",
    )
    ax.set_xlabel("Event name")
    ax.set_ylabel(metric)
    ax.set_title(f"GA4 {metric} by event – current vs previous period")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    output_path = _ensure_output_path(output_filename)
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()

    return {
        "chart_path": str(output_path),
        "metric": metric,
        "top_events": top_events.to_dict(orient="records"),
        "metadata": {
            "property_id": current.get("metadata", {}).get("property_id", property_id),
            "current_range": current.get("metadata", {}).get("date_range"),
            "previous_range": previous.get("metadata", {}).get("date_range"),
        },
    }


def plot_ga4_event_page_conversions(
    property_id: str,
    event_name: str,
    start_date: str,
    end_date: str,
    metric: str = "eventCount",
    top_n: int = 20,
    output_filename: Optional[str] = None,
) -> Dict:
    """Plot top pages driving a specific key event.

    This tool fetches GA4 data grouped by eventName and pagePathPlusQueryString
    and generates a bar chart of the top pages contributing to a given event.

    Args:
        property_id: GA4 property ID ('123456789' or 'properties/123456789').
        event_name: The key event to analyze (e.g. 'generate_lead', 'purchase').
        start_date: Start of the period (YYYY-MM-DD or NdaysAgo).
        end_date: End of the period.
        metric: Metric to plot (e.g. 'eventCount', 'conversions').
        top_n: Number of top pages to show.
        output_filename: Optional filename for the chart (saved under ga4_charts/).

    Returns:
        Dict with chart_path and page breakdown.
    """
    data = get_ga4_metrics(
        property_id=property_id,
        start_date=start_date,
        end_date=end_date,
        metrics=[metric],
        dimensions=["eventName", "pagePathPlusQueryString"],
    )

    df = pd.DataFrame(data.get("rows", []))
    if df.empty:
        return {"error": "No GA4 data available for the selected period."}

    # Filter to the requested event
    df = df[df["eventName"] == event_name]
    if df.empty:
        return {
            "error": f"No GA4 data found for event '{event_name}' in the selected period."
        }

    # Ensure numeric metric
    df[metric] = pd.to_numeric(df[metric], errors="coerce").fillna(0)

    # Aggregate by page
    agg = (
        df.groupby("pagePathPlusQueryString", as_index=False)[metric]
        .sum()
        .sort_values(metric, ascending=False)
    )
    top_pages = agg.head(top_n)

    # Shorten long paths for labeling but keep full path in data
    plot_df = top_pages.copy()
    plot_df["label"] = plot_df["pagePathPlusQueryString"].apply(
        lambda p: p if len(p) <= 60 else p[:57] + "..."
    )

    # Create chart
    sns.set(style="whitegrid")
    plt.figure(figsize=(12, 6))
    ax = sns.barplot(
        data=plot_df,
        x="label",
        y=metric,
        color="steelblue",
    )
    ax.set_xlabel("Page path")
    ax.set_ylabel(metric)
    ax.set_title(f"Top pages driving event: {event_name}")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    output_path = _ensure_output_path(output_filename)
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()

    return {
        "chart_path": str(output_path),
        "event_name": event_name,
        "metric": metric,
        "pages": top_pages.to_dict(orient="records"),
        "metadata": {
            "property_id": data.get("metadata", {}).get("property_id", property_id),
            "date_range": data.get("metadata", {}).get("date_range"),
        },
    }

