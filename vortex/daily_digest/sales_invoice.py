
import frappe

from vortex.daily_digest.report import normalize_report_data


def get_daily_sales_invoice_list(company, from_date, to_date):

    columns = [
        {
            "label": "Sales Invoice",
            "fieldname": "sales_invoice",
            "fieldtype": "Link",
        },
        {
            "label": "Posting Date",
            "fieldname": "posting_date",
            "fieldtype": "Date",
        },
        {
            "label": "Customer",
            "fieldname": "customer",
            "fieldtype": "Link",
        },
        {
            "label": "Customer Name",
            "fieldname": "customer_name",
            "fieldtype": "Data",
        },
        {
            "label": "Currency",
            "fieldname": "currency",
            "fieldtype": "Data",
        },
        {
            "label": "Grand Total",
            "fieldname": "grand_total",
            "fieldtype": "Currency",
        },
        {
            "label": "Outstanding Amount",
            "fieldname": "outstanding_amount",
            "fieldtype": "Currency",
        },
        {
            "label": "Status",
            "fieldname": "status",
            "fieldtype": "Data",
        },
    ]

    rows = frappe.db.sql(
        """
        SELECT
            name AS sales_invoice,
            posting_date,
            customer,
            customer_name,
            currency,
            grand_total,
            outstanding_amount,
            status
        FROM `tabSales Invoice`
        WHERE
            docstatus = 1
            AND is_return = 0
            AND company = %(company)s
            AND posting_date BETWEEN %(from_date)s AND %(to_date)s
        ORDER BY posting_date, name
        """,
        {
            "company": company,
            "from_date": from_date,
            "to_date": to_date,
        },
        as_list=True,
    )

    normalized_columns, normalized_rows = normalize_report_data(
        columns,
        rows
    )

    return {
        "title": "Daily Sales Invoice List",
        "columns": normalized_columns,
        "rows": normalized_rows,
        "total_rows": len(normalized_rows),
        "filters": {
            "company": company,
            "from_date": from_date,
            "to_date": to_date,
        },
    }
