import frappe


def notify_sales_persons(doc, method=None):
    """Email all salespersons assigned to the Sales Invoice customer."""

    if doc.doctype != "Sales Invoice" or doc.docstatus != 1:
        return

    if not doc.customer:
        return

    # Read the salesperson assignments from Customer Master
    customer = frappe.get_doc("Customer", doc.customer)
    recipients = set()

    for row in customer.get("sales_persons") or []:
        salesperson_name = row.get("sales_person")

        if not salesperson_name:
            continue

        # Get email directly from Sales Person, if configured
        salesperson = frappe.get_doc("Sales Person", salesperson_name)
        email = None

        for fieldname in ("email_id", "email"):
            if salesperson.meta.has_field(fieldname):
                email = salesperson.get(fieldname)
                if email:
                    break

        # If email is stored against the linked Employee, use it
        if not email and salesperson.meta.has_field("employee"):
            employee_name = salesperson.get("employee")

            if employee_name:
                employee = frappe.get_doc("Employee", employee_name)

                for fieldname in (
                    "company_email",
                    "prefered_email",
                    "user_id",
                ):
                    if employee.meta.has_field(fieldname):
                        email = employee.get(fieldname)
                        if email:
                            break

        if email and "@" in email:
            recipients.add(email.strip())

    if not recipients:
        return

    subject = f"Sales Invoice Submitted: {doc.name}"

    message = f"""
        <p>Dear Sales Person,</p>
        <p>A Sales Invoice has been submitted.</p>
        <p>
            <b>Invoice:</b> {frappe.utils.escape_html(doc.name)}<br>
            <b>Customer:</b> {frappe.utils.escape_html(doc.customer)}<br>
            <b>Posting Date:</b> {frappe.utils.escape_html(str(doc.posting_date))}<br>
            <b>Grand Total:</b> {frappe.utils.fmt_money(
                doc.grand_total,
                currency=doc.currency
            )}
        </p>
        <p>Please review the invoice in ERPNext.</p>
    """

    frappe.sendmail(
        recipients=sorted(recipients),
        subject=subject,
        message=message,
        reference_doctype="Sales Invoice",
        reference_name=doc.name,
        delayed=True,
    )