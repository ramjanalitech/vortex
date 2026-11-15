
import json
import re

import frappe
from frappe.utils import cint


DATE_FILTER_FIELDS = {
    "from_date",
    "to_date",
    "report_date",
    "age_as_on",
    "posting_date",
    "start_date",
    "end_date",
}


def get_report_filters(report_name, company, from_date, to_date):
    """Build report filters using configured Report filters."""

    report = frappe.get_doc("Report", report_name)

    filters = {}

    report_filters = report.get("filters") or []

    if isinstance(report_filters, str):
        report_filters = json.loads(report_filters)

    for field in report_filters:
        fieldname = field.get("fieldname")

        if not fieldname:
            continue

        if fieldname == "company":
            filters[fieldname] = company

        elif fieldname == "from_date":
            filters[fieldname] = str(from_date)

        elif fieldname == "to_date":
            filters[fieldname] = str(to_date)

        elif fieldname in DATE_FILTER_FIELDS:
            filters[fieldname] = str(from_date if fieldname in {
                "report_date", "age_as_on", "posting_date", "start_date"
            } else to_date)

        elif field.get("default"):
            filters[fieldname] = field.get("default")

    # Company is required for company-specific reports such as
    # Item-wise Sales History.
    filters["company"] = company

    return filters


def normalize_report_data(columns, rows):
    """Convert Frappe report output into a consistent structure."""

    normalized_columns = []

    for column in columns or []:

        if isinstance(column, dict):
            fieldname = column.get("fieldname") or ""
            label = column.get("label") or fieldname
            fieldtype = column.get("fieldtype") or "Data"
            width = cint(column.get("width") or 0)

        else:
            parts = str(column).split(":")
            label = parts[0].strip()
            fieldname = frappe.scrub(label)
            fieldtype = "Data"
            width = 0

            if len(parts) > 1:
                fieldtype = parts[1].split("/")[0] or "Data"

            if len(parts) > 2:
                try:
                    width = cint(parts[2])
                except (ValueError, TypeError):
                    width = 0

        normalized_columns.append({
            "label": label,
            "fieldname": fieldname,
            "fieldtype": fieldtype,
            "width": width,
        })

    normalized_rows = []

    for row in rows or []:

        if isinstance(row, dict):
            normalized_rows.append([
                row.get(column["fieldname"])
                for column in normalized_columns
            ])

        else:
            normalized_rows.append(list(row))

    return normalized_columns, normalized_rows


def apply_selected_columns(report_data, selected_columns):
    """Filter and reorder report columns according to configuration."""

    if not selected_columns:
        return report_data

    requested = [
        value.strip()
        for value in str(selected_columns).split(",")
        if value.strip()
    ]

    if not requested:
        return report_data

    columns = report_data.get("columns") or []
    rows = report_data.get("rows") or []

    column_lookup = {}

    for index, column in enumerate(columns):
        column_lookup[column["fieldname"].lower()] = index
        column_lookup[column["label"].lower()] = index

    selected_indexes = []

    for requested_column in requested:
        key = requested_column.lower()

        if key not in column_lookup:
            available = ", ".join(
                column["fieldname"] for column in columns
            )

            frappe.throw(
                f"Column '{requested_column}' was not found in "
                f"report '{report_data.get('title')}'. "
                f"Available columns: {available}"
            )

        index = column_lookup[key]

        if index not in selected_indexes:
            selected_indexes.append(index)

    report_data["columns"] = [
        columns[index] for index in selected_indexes
    ]

    report_data["rows"] = [
        [
            row[index] if index < len(row) else None
            for index in selected_indexes
        ]
        for row in rows
    ]

    return report_data


def execute_standard_report(
    report_name,
    company,
    from_date,
    to_date
):
    """Execute a standard ERPNext Query or Script Report."""

    from frappe.desk.query_report import run

    filters = get_report_filters(
        report_name,
        company,
        from_date,
        to_date
    )

    result = run(
        report_name=report_name,
        filters=filters
    )

    columns, rows = normalize_report_data(
        result.get("columns") or [],
        result.get("result") or []
    )

    return {
        "title": report_name,
        "columns": columns,
        "rows": rows,
        "total_rows": len(rows),
        "filters": filters,
    }
