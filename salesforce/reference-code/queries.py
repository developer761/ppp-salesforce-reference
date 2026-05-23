"""SOQL pulls for the monthly Field performance report card.

Each function takes a list of rep User Ids plus the reporting period (month-end
date) and returns a pandas DataFrame. Queries hit `my-production` via the `sf`
CLI and parse the JSON output.
"""
from __future__ import annotations

import datetime as dt
import json
import shutil
import subprocess
from pathlib import Path

import pandas as pd

# Profile Id for the "*Standard.Field" rep profile — look up in your own org:
#   sf data query -q "SELECT Id FROM Profile WHERE Name = '*Standard.Field'"
FIELD_MEMBER_PROFILE_ID = "<FIELD_MEMBER_PROFILE_ID>"  # org-specific; do not hardcode in a public repo
CASE_TYPE_WHITELIST = (
    "Estimator No Show",
    "Waiting for Estimate",
    "Dissatisfied Customer",
    "Balance Owed",
    "Service Call",
    "Other",
)
TARGET_ORG = "my-production"

_SF = shutil.which("sf") or "sf"


def _soql(query: str) -> list[dict]:
    proc = subprocess.run(
        [_SF, "data", "query", "--query", query, "--target-org", TARGET_ORG, "--json"],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"SOQL failed: {proc.stderr or proc.stdout}\nQuery: {query}")
    payload = json.loads(proc.stdout)
    return payload["result"]["records"]


def _ids_csv(rep_ids: list[str]) -> str:
    return ",".join(f"'{rid}'" for rid in rep_ids)


def fiscal_year_start(report_month_end: dt.date) -> dt.date:
    """FY starts Feb 1; FY name = start year. April 2026 -> FY26 -> 2026-02-01."""
    fy_year = report_month_end.year if report_month_end.month >= 2 else report_month_end.year - 1
    return dt.date(fy_year, 2, 1)


def fiscal_year_end(report_month_end: dt.date) -> dt.date:
    fy_start = fiscal_year_start(report_month_end)
    return dt.date(fy_start.year + 1, 1, 31)


def field_member_reps() -> pd.DataFrame:
    """Returns active reps with profile *Standard.Field, columns: Id, Name."""
    rows = _soql(
        f"SELECT Id, Name FROM User "
        f"WHERE ProfileId = '{FIELD_MEMBER_PROFILE_ID}' AND IsActive = true "
        f"ORDER BY Name"
    )
    return pd.DataFrame([{"Id": r["Id"], "Name": r["Name"]} for r in rows])


def yoy_sales_monthly(rep_ids: list[str], report_month_end: dt.date) -> pd.DataFrame:
    """Won-opp sales by rep × calendar year × calendar month, current FY + prior FY.

    Window: prior FY start through current FY end (24 months of close dates).
    Filtered to IsWon=true so only realized sales count.
    """
    fy_curr_end = fiscal_year_end(report_month_end)
    fy_prior_start = dt.date(fiscal_year_start(report_month_end).year - 1, 2, 1)
    rows = _soql(
        f"SELECT OwnerId, CALENDAR_YEAR(CloseDate) yr, CALENDAR_MONTH(CloseDate) mo, "
        f"SUM(QuotedSubtotalWithChangeOrder__c) total "
        f"FROM Opportunity "
        f"WHERE OwnerId IN ({_ids_csv(rep_ids)}) "
        f"AND CloseDate >= {fy_prior_start.isoformat()} "
        f"AND CloseDate <= {fy_curr_end.isoformat()} "
        f"AND IsWon = true "
        f"GROUP BY OwnerId, CALENDAR_YEAR(CloseDate), CALENDAR_MONTH(CloseDate)"
    )
    return pd.DataFrame(
        [
            {
                "OwnerId": r["OwnerId"],
                "year": int(r["yr"]),
                "month": int(r["mo"]),
                "total": float(r["total"] or 0),
            }
            for r in rows
        ]
    )


def close_ratio(rep_ids: list[str], report_month_end: dt.date) -> pd.DataFrame:
    """Won vs total opps created in the current fiscal year, by rep.

    Returns one row per rep with `won`, `total`, `ratio`. Reps with zero opps in
    the FY are not in the result — caller should default them to 0/0.
    """
    fy_start = fiscal_year_start(report_month_end)
    fy_end_dt = dt.datetime.combine(
        dt.date(fy_start.year + 1, 2, 1), dt.time.min
    )  # exclusive upper bound
    rows = _soql(
        f"SELECT OwnerId, IsWon, COUNT(Id) cnt "
        f"FROM Opportunity "
        f"WHERE OwnerId IN ({_ids_csv(rep_ids)}) "
        f"AND CreatedDate >= {fy_start.isoformat()}T00:00:00Z "
        f"AND CreatedDate < {fy_end_dt.isoformat()}Z "
        f"GROUP BY OwnerId, IsWon"
    )
    df = pd.DataFrame([{"OwnerId": r["OwnerId"], "IsWon": r["IsWon"], "cnt": int(r["cnt"])} for r in rows])
    if df.empty:
        return pd.DataFrame(columns=["OwnerId", "won", "total", "ratio"])
    pivot = df.pivot_table(index="OwnerId", columns="IsWon", values="cnt", fill_value=0).reset_index()
    pivot.columns.name = None
    pivot = pivot.rename(columns={True: "won", False: "not_won"})
    if "won" not in pivot.columns:
        pivot["won"] = 0
    if "not_won" not in pivot.columns:
        pivot["not_won"] = 0
    pivot["total"] = pivot["won"] + pivot["not_won"]
    pivot["ratio"] = pivot.apply(lambda r: r["won"] / r["total"] if r["total"] else 0.0, axis=1)
    return pivot[["OwnerId", "won", "total", "ratio"]]


def repeat_referral_split(rep_ids: list[str], report_month_end: dt.date) -> pd.DataFrame:
    """FY-to-date won sales split by Repeat / Referral / Other (NULL).

    Returns rows with columns OwnerId, category, total. Caller should expect
    only the categories actually present per rep — missing buckets default to 0.
    """
    fy_start = fiscal_year_start(report_month_end)
    rows = _soql(
        f"SELECT OwnerId, Repeat_Referral__c cat, "
        f"SUM(QuotedSubtotalWithChangeOrder__c) total "
        f"FROM Opportunity "
        f"WHERE OwnerId IN ({_ids_csv(rep_ids)}) "
        f"AND CloseDate >= {fy_start.isoformat()} "
        f"AND CloseDate <= {report_month_end.isoformat()} "
        f"AND IsWon = true "
        f"GROUP BY OwnerId, Repeat_Referral__c"
    )
    out = []
    for r in rows:
        cat = r.get("cat") or "Other"
        out.append({"OwnerId": r["OwnerId"], "category": cat, "total": float(r["total"] or 0)})
    return pd.DataFrame(out)


def open_cases_by_type(rep_ids: list[str]) -> pd.DataFrame:
    """Point-in-time count of open Cases by rep × Case.Type (whitelist only)."""
    types_csv = ",".join(f"'{t}'" for t in CASE_TYPE_WHITELIST)
    rows = _soql(
        f"SELECT OwnerId, Type, COUNT(Id) cnt "
        f"FROM Case "
        f"WHERE OwnerId IN ({_ids_csv(rep_ids)}) "
        f"AND IsClosed = false "
        f"AND Type IN ({types_csv}) "
        f"GROUP BY OwnerId, Type"
    )
    return pd.DataFrame(
        [
            {"OwnerId": r["OwnerId"], "type": r["Type"], "cnt": int(r["cnt"])}
            for r in rows
        ]
    )


def balances_owed(rep_ids: list[str]) -> pd.DataFrame:
    """Point-in-time sum of BalanceOwed__c and avg Final_Balance_Aging__c for
    Work Orders in 'Complete Balance Owed' status, by rep."""
    rows = _soql(
        f"SELECT OwnerId, SUM(BalanceOwed__c) total, "
        f"AVG(Final_Balance_Aging__c) avg_aging, COUNT(Id) cnt "
        f"FROM WorkOrder "
        f"WHERE OwnerId IN ({_ids_csv(rep_ids)}) "
        f"AND Status = 'Complete Balance Owed' "
        f"GROUP BY OwnerId"
    )
    return pd.DataFrame(
        [
            {
                "OwnerId": r["OwnerId"],
                "total_owed": float(r["total"] or 0),
                "avg_aging_days": float(r["avg_aging"] or 0),
                "wo_count": int(r["cnt"]),
            }
            for r in rows
        ]
    )
