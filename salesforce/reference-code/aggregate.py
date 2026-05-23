"""Per-rep metric aggregation. Takes the raw query DataFrames and produces a
dict per rep, ready for HTML templating."""
from __future__ import annotations

import calendar
import datetime as dt

import pandas as pd

import queries

MONTH_LABELS = ["Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan"]


def _fy_month_sequence(fy_start_year: int) -> list[tuple[int, int, str]]:
    """FY months in order: (year, month, label). Feb..Jan."""
    seq = []
    for offset, label in enumerate(MONTH_LABELS):
        month = ((1 + offset) % 12) + 1  # Feb=2 ... Jan=1
        year = fy_start_year if month >= 2 else fy_start_year + 1
        seq.append((year, month, label))
    return seq


def build_rep_metrics(
    reps: pd.DataFrame,
    yoy: pd.DataFrame,
    ratio: pd.DataFrame,
    rr: pd.DataFrame,
    cases: pd.DataFrame,
    balances: pd.DataFrame,
    report_month_end: dt.date,
) -> list[dict]:
    """Produce a list of per-rep dicts shaped for the HTML template."""
    fy_start = queries.fiscal_year_start(report_month_end)
    fy_curr = fy_start.year
    fy_prior = fy_curr - 1
    months = _fy_month_sequence(fy_curr)
    rep_metrics = []

    yoy_indexed = yoy.set_index(["OwnerId", "year", "month"])["total"] if not yoy.empty else pd.Series(dtype=float)
    ratio_indexed = ratio.set_index("OwnerId") if not ratio.empty else pd.DataFrame()
    rr_indexed = rr.set_index(["OwnerId", "category"])["total"] if not rr.empty else pd.Series(dtype=float)
    cases_indexed = cases.set_index(["OwnerId", "type"])["cnt"] if not cases.empty else pd.Series(dtype=int)
    balances_indexed = balances.set_index("OwnerId") if not balances.empty else pd.DataFrame()

    for _, row in reps.iterrows():
        owner_id = row["Id"]
        rep_name = row["Name"]

        # KPI 1: YOY monthly
        yoy_rows = []
        curr_total = 0.0
        prior_total = 0.0
        for (year, month, label) in months:
            curr_val = float(yoy_indexed.get((owner_id, year, month), 0.0)) if len(yoy_indexed) else 0.0
            prior_year_for_month = year - 1
            prior_val = float(yoy_indexed.get((owner_id, prior_year_for_month, month), 0.0)) if len(yoy_indexed) else 0.0
            yoy_rows.append(
                {
                    "month_label": label,
                    "current": curr_val,
                    "prior": prior_val,
                    "delta": curr_val - prior_val,
                }
            )
            curr_total += curr_val
            prior_total += prior_val

        # KPI 2: Close Ratio
        if owner_id in ratio_indexed.index:
            r = ratio_indexed.loc[owner_id]
            close_won = int(r["won"])
            close_total = int(r["total"])
            close_ratio_val = float(r["ratio"])
        else:
            close_won = close_total = 0
            close_ratio_val = 0.0

        # KPI 3: Repeat / Referral / Other
        rr_repeat = float(rr_indexed.get((owner_id, "Repeat"), 0.0)) if len(rr_indexed) else 0.0
        rr_referral = float(rr_indexed.get((owner_id, "Referral"), 0.0)) if len(rr_indexed) else 0.0
        rr_other = float(rr_indexed.get((owner_id, "Other"), 0.0)) if len(rr_indexed) else 0.0
        rr_grand = rr_repeat + rr_referral + rr_other

        # KPI 4: Open Cases by Type
        case_rows = []
        case_total = 0
        for t in queries.CASE_TYPE_WHITELIST:
            cnt = int(cases_indexed.get((owner_id, t), 0)) if len(cases_indexed) else 0
            case_rows.append({"type": t, "cnt": cnt})
            case_total += cnt

        # KPI 5: Balances Owed
        if owner_id in balances_indexed.index:
            b = balances_indexed.loc[owner_id]
            bal_total = float(b["total_owed"])
            bal_aging = float(b["avg_aging_days"])
            bal_count = int(b["wo_count"])
        else:
            bal_total = bal_aging = 0.0
            bal_count = 0

        rep_metrics.append(
            {
                "owner_id": owner_id,
                "rep_name": rep_name,
                "report_month_label": calendar.month_name[report_month_end.month] + f" {report_month_end.year}",
                "fy_curr": f"FY{fy_curr % 100:02d}",
                "fy_prior": f"FY{fy_prior % 100:02d}",
                "yoy_rows": yoy_rows,
                "yoy_curr_total": curr_total,
                "yoy_prior_total": prior_total,
                "close_won": close_won,
                "close_total": close_total,
                "close_ratio": close_ratio_val,
                "rr_repeat": rr_repeat,
                "rr_referral": rr_referral,
                "rr_other": rr_other,
                "rr_grand": rr_grand,
                "case_rows": case_rows,
                "case_total": case_total,
                "bal_total": bal_total,
                "bal_aging_days": bal_aging,
                "bal_count": bal_count,
            }
        )

    return rep_metrics
