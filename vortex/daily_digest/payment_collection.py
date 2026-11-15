
import frappe

from vortex.daily_digest.report import normalize_report_data


def get_payment_collection(company, from_date, to_date):
    """Get customer collections allocated against Sales Invoices."""

    columns = [
        {
            "label": "Posting Date",
            "fieldname": "posting_date",
            "fieldtype": "Date",
        },
        {
            "label": "Payment Entry",
            "fieldname": "payment_entry",
            "fieldtype": "Link",
        },
        {
            "label": "Customer",
            "fieldname": "customer",
            "fieldtype": "Link",
        },
        {
            "label": "Currency",
            "fieldname": "currency",
            "fieldtype": "Data",
        },
        {
            "label": "Collected Amount",
            "fieldname": "collected_amount",
            "fieldtype": "Currency",
        },
    ]

    rows = frappe.db.sql(
        """
        SELECT
            pe.posting_date,
            pe.name AS payment_entry,
            pe.party AS customer,
            si.currency,
            SUM(per.allocated_amount) AS collected_amount

        FROM `tabPayment Entry` pe

        INNER JOIN `tabPayment Entry Reference` per
            ON per.parent = pe.name

        LEFT JOIN `tabSales Invoice` si
            ON si.name = per.reference_name

        WHERE
            pe.docstatus = 1
            AND pe.payment_type = 'Receive'
            AND pe.party_type = 'Customer'
            AND pe.company = %(company)s
            AND pe.posting_date BETWEEN %(from_date)s
                AND %(to_date)s
            AND per.reference_doctype = 'Sales Invoice'

        GROUP BY
            pe.posting_date,
            pe.name,
            pe.party,
            si.currency

        ORDER BY
            pe.posting_date,
            pe.name
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
        "title": "Payment Collection",
        "columns": normalized_columns,
        "rows": normalized_rows,
        "total_rows": len(normalized_rows),
        "filters": {
            "company": company,
            "from_date": from_date,
            "to_date": to_date,
        },
    }
