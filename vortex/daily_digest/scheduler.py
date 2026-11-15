
import frappe

from frappe.utils import add_days, nowdate, getdate

from vortex.daily_digest.report import (
    execute_standard_report,
    apply_selected_columns,
)

from vortex.daily_digest.sales_invoice import (
    get_daily_sales_invoice_list,
)

from vortex.daily_digest.payment_collection import (
    get_payment_collection,
)


CUSTOM_REPORTS = {
    "Payment Collection",
    "Daily Sales Invoice List",
}


def get_digest_setting():
    if not frappe.db.exists("DocType", "Daily Digest Setting"):
        return None

    setting = frappe.get_doc("Daily Digest Setting")

    if not setting.enabled:
        return None

    return setting


def get_recipients(setting):
    recipients = []

    for row in (setting.get("recipients") or []):
        if row.enabled and row.email_address:
            recipients.append(row.email_address.strip())

    return list(dict.fromkeys(recipients))


def get_enabled_reports(setting):
    reports = []

    for row in (setting.get("reports") or []):
        if not row.enabled or not row.report_name:
            continue

        reports.append({
            "report_name": row.report_name,
            "selected_columns": row.get("selected_columns"),
            "display_order": row.get("display_order") or 0,
        })

    return sorted(
        reports,
        key=lambda item: item["display_order"]
    )


def build_digest(company, from_date, to_date, report_rows):
    sections = []
    errors = []

    for report_config in report_rows:

        report_name = report_config["report_name"]

        try:
            if report_name in CUSTOM_REPORTS:
                if report_name == "Payment Collection":
                    report_data = get_payment_collection(
                        company,
                        from_date,
                        to_date
                    )

                elif report_name == "Daily Sales Invoice List":
                    report_data = get_daily_sales_invoice_list(
                        company,
                        from_date,
                        to_date
                    )
            else:
                if not frappe.db.exists("Report", report_name):
                    frappe.throw(
                        f"Report '{report_name}' does not exist."
                    )

                report_data = execute_standard_report(
                    report_name,
                    company,
                    from_date,
                    to_date
                )

            report_data = apply_selected_columns(
                report_data,
                report_config.get("selected_columns")
            )

            sections.append(report_data)

        except Exception:
            error_message = frappe.get_traceback()

            frappe.log_error(
                title=f"Daily Digest Report Error: {report_name}",
                message=error_message
            )

            errors.append({
                "report_name": report_name,
                "message": str(frappe.get_traceback().splitlines()[-1]),
            })

    return sections, errors


def render_digest_html(context):
    return frappe.render_template(
        "templates/emails/daily_digest.html",
        context
    )


def generate_digest_pdf(html):
    """Generate one consolidated PDF for all report sections."""

    from frappe.utils.pdf import get_pdf

    return get_pdf(
        html,
        options={
            "orientation": "Landscape",
            "page-size": "A4",
            "margin-top": "12mm",
            "margin-bottom": "12mm",
            "margin-left": "8mm",
            "margin-right": "8mm",
            "encoding": "UTF-8",
        }
    )


def send_daily_digest():
    setting = get_digest_setting()

    if not setting:
        frappe.logger("daily_digest").info(
            "Daily Digest is disabled."
        )
        return

    recipients = get_recipients(setting)

    if not recipients:
        frappe.log_error(
            title="Daily Digest",
            message="No active email recipients configured."
        )
        return

    if not setting.company:
        frappe.log_error(
            title="Daily Digest",
            message="Company is not configured."
        )
        return

    to_date = getdate(nowdate())
    from_date = getdate(add_days(to_date, -1))

    report_rows = get_enabled_reports(setting)

    if not report_rows:
        frappe.log_error(
            title="Daily Digest",
            message="No enabled reports configured."
        )
        return

    sections, errors = build_digest(
        setting.company,
        from_date,
        to_date,
        report_rows
    )

    if not sections:
        frappe.log_error(
            title="Daily Digest",
            message="No reports could be generated."
        )
        return

    context = {
        "company": setting.company,
        "from_date": from_date,
        "to_date": to_date,
        "sections": sections,
        "errors": errors,
        "is_pdf": True,
    }

    # Generate one consolidated PDF.
    pdf_html = render_digest_html(context)
    pdf_content = generate_digest_pdf(pdf_html)

    pdf_filename = (
        f"Daily_Digest_{from_date.strftime('%Y%m%d')}.pdf"
    )

    # Render email HTML separately.
    context["is_pdf"] = False
    email_html = render_digest_html(context)

    subject = (
        f"Daily ERPNext Business Digest - {from_date}"
    )

    frappe.sendmail(
        recipients=recipients,
        subject=subject,
        message=email_html,
        attachments=[
            {
                "fname": pdf_filename,
                "fcontent": pdf_content,
            }
        ],
        delayed=False,
    )

    frappe.logger("daily_digest").info(
        f"Daily Digest email submitted to {', '.join(recipients)}"
    )

    return {
        "status": "Email submitted",
        "recipients": recipients,
        "report_count": len(sections),
        "errors": errors,
        "pdf_filename": pdf_filename,
    }
