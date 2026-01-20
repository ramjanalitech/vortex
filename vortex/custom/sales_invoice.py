
# New Code 

import frappe
import json
import requests
from frappe.utils.pdf import get_pdf
from frappe.utils import get_url
from frappe import _
from frappe.utils import cint
from frappe.utils import flt
from frappe.utils import fmt_money

# --------------------------------------------------
# 1️⃣ ON SUBMIT EVENT
# --------------------------------------------------

@frappe.whitelist()
def generate_pdf_and_send_whatsapp_on_submit(doc, method=None):
    """
    Triggered on Sales Invoice submit
    """
    result = send_whatsapp_message(doc.name, doc.doctype)

    if result.get("status") == "Sent":
        frappe.msgprint(
            _("WhatsApp message sent successfully to {0}")
            .format(result.get("mobile"))
        )
    elif result.get("status") == "Skipped":
        frappe.msgprint(_("WhatsApp already sent for this document"))
    else:
        frappe.msgprint(
            _("Failed to send WhatsApp message. Reason: {0}")
            .format(result.get("message"))
        )

# --------------------------------------------------
# 2️⃣ BUTTON ACTION
# --------------------------------------------------

@frappe.whitelist()
def send_whatsapp_button(docname, doctype):
    result = send_whatsapp_message(docname, doctype)

    if result.get("status") == "Sent":
        frappe.msgprint(
            _("WhatsApp message sent successfully to {0}")
            .format(result.get("mobile"))
        )
    elif result.get("status") == "Skipped":
        frappe.msgprint(_("WhatsApp already sent for this document"))
    else:
        frappe.msgprint(
            _("Failed to send WhatsApp message. Reason: {0}")
            .format(result.get("message"))
        )

    return result


# --------------------------------------------------
# 3️⃣ SCHEDULER FUNCTION
# --------------------------------------------------

def schedule_sales_invoices_whatsapp():
    """
    Send WhatsApp only for today's submitted Sales Invoices
    """
    today = frappe.utils.today()

    invoices = frappe.get_all(
        "Sales Invoice",
        filters={
            "docstatus": 1,
            "posting_date": today,          # 👈 ONLY TODAY
            "contact_mobile": ["!=", ""]
        },
        fields=["name"]
    )

    for inv in invoices:
        try:
            send_whatsapp_message(inv.name, "Sales Invoice")
        except Exception:
            frappe.log_error(
                frappe.get_traceback(),
                f"WhatsApp Scheduler Failed for {inv.name}"
            )


# --------------------------------------------------
# 4️⃣ CORE SENDER
# --------------------------------------------------

def send_whatsapp_message(docname, doctype):
    doc = frappe.get_doc(doctype, docname)

    # 🚫 Return / Replacement rules
    if doctype == "Sales Invoice":

        # Replacement → always block
        if cint(getattr(doc, "is_replacemnet", 0)) == 1:
            return {
                "status": "Skipped",
                "message": "Replacement Sales Invoice – WhatsApp not allowed",
                "mobile": None
            }

        # Sales Return → block ONLY if total = 0
        if cint(getattr(doc, "is_return", 0)) == 1 and doc.grand_total == 0:
            return {
                "status": "Skipped",
                "message": "Sales Return with zero amount – WhatsApp not allowed",
                "mobile": None
            }


    # Skip if mobile missing
    if not getattr(doc, "contact_mobile", None):
        return {
            "status": "Skipped",
            "message": "Customer mobile number is missing",
            "mobile": None
        }

    # Prevent duplicate WhatsApp
    if frappe.db.exists(
        "Whatsapp Log",
        {
            "doctype_name": doctype,
            "document_name": docname,
            "status": "Sent"
        }
    ):
        return {
            "status": "Skipped",
            "message": "WhatsApp already sent for this document",
            "mobile": doc.contact_mobile
        }

    customer_name = getattr(doc, "customer_name", None) or getattr(doc, "customer", None)

    invoice_data = {
        "name": docname,
        "doctype": doctype,
        "customer": customer_name,
        "contact_mobile": doc.contact_mobile
    }

    whatsapp_settings = get_whatsapp_settings()

    return send_whatsapp_with_pdf(
        invoice_data,
        whatsapp_settings["api_key"],
        whatsapp_settings["url"]
    )

# --------------------------------------------------
# 5️⃣ WHATSAPP SETTINGS
# --------------------------------------------------

def get_whatsapp_settings():
    whatsapp_settings = frappe.get_doc("Whatsapp Setting")

    if not whatsapp_settings.url or not whatsapp_settings.api_key:
        frappe.throw(_("WhatsApp settings are incomplete."))

    return {
        "url": whatsapp_settings.url,
        "api_key": whatsapp_settings.api_key
    }


def get_campaign_name(doctype):
    whatsapp_campaign = frappe.get_doc("Whatsapp Setting")

    for campaign in whatsapp_campaign.whatsapp_campaign:
        if campaign.campaign_doctype == doctype:
            return campaign.campaign_name

    frappe.throw(_("No WhatsApp campaign found for {0}").format(doctype))


# --------------------------------------------------
# 6️⃣ SEND WHATSAPP WITH PDF
# --------------------------------------------------

def send_whatsapp_with_pdf(invoice, api_key, url):
    try:
        file_url = generate_public_pdf(invoice["name"], invoice["doctype"])

        headers = {"Content-Type": "application/json"}

        # Template params per doctype
        if invoice["doctype"] == "Delivery Note":
            dn = frappe.get_doc("Delivery Note", invoice["name"])
            template_params = [dn.sales_invoice or ""]
        else:
            template_params = []

        data = {
            "apiKey": api_key,
            "campaignName": get_campaign_name(invoice["doctype"]),
            "destination": invoice["contact_mobile"],
            "userName": invoice["customer"],
            "source": invoice["doctype"],
            "media": {
                "url": file_url,
                "filename": f"{invoice['name']}.pdf"
            },
            "templateParams": template_params,
            "tags": [invoice["doctype"]]
        }

        frappe.logger().info(f"Sending WhatsApp: {json.dumps(data)}")

        response = requests.post(
            url,
            data=json.dumps(data),
            headers=headers,
            timeout=10
        )

        status = "Sent" if response.status_code == 200 else "Not Sent"

        log_whatsapp_status(
            invoice["name"],
            invoice["doctype"],
            invoice["customer"],
            invoice["contact_mobile"],
            file_url,
            response.text,
            status
        )

        return {
            "status": status,
            "message": response.text,
            "mobile": invoice["contact_mobile"]
        }

    except Exception as e:
        frappe.log_error(
            frappe.get_traceback(),
            f"Error sending WhatsApp for {invoice['name']}"
        )
        return {
            "status": "Failed",
            "message": str(e),
            "mobile": invoice["contact_mobile"]
        }


# --------------------------------------------------
# 7️⃣ PDF GENERATION
# --------------------------------------------------

def generate_public_pdf(docname, doctype):
    print_format = frappe.db.get_value(
        "Property Setter",
        {"doc_type": doctype, "property": "default_print_format"},
        "value"
    ) or "Standard"

    html = frappe.get_print(doctype, docname, print_format=print_format)
    pdf_content = get_pdf(html)

    file_name = f"{frappe.generate_hash('', 5)}.pdf"

    file_doc = frappe.get_doc({
        "doctype": "File",
        "file_name": file_name,
        "attached_to_doctype": doctype,
        "attached_to_name": docname,
        "is_private": 0,
        "content": pdf_content
    })

    file_doc.save(ignore_permissions=True)
    frappe.db.commit()

    return get_url() + file_doc.file_url


# --------------------------------------------------
# 8️⃣ WHATSAPP LOG
# --------------------------------------------------

def log_whatsapp_status(docname, doctype, customer, mobile_no, file_url, response_text, status):
    try:
        frappe.get_doc({
            "doctype": "Whatsapp Log",
            "doctype_name": doctype,
            "document_name": docname,
            "customer": customer,
            "mobile_no": mobile_no,
            "url": file_url,
            "status": status,
            "response": response_text
        }).insert(ignore_permissions=True)
    except Exception:
        frappe.log_error(
            frappe.get_traceback(),
            f"Failed to log WhatsApp for {docname}"
        )


# OverDue Code

def schedule_overdue_sales_invoice_whatsapp():
    today = frappe.utils.today()

    invoices = frappe.get_all(
        "Sales Invoice",
        filters={
            "docstatus": 1,
            "outstanding_amount": [">", 0],
            "due_date": ["<", today],
            "custom_overdue_whatsapp_sent": 0,
            "contact_mobile": ["!=", ""]
        },
        pluck="name"
    )

    for invoice_name in invoices:
        try:
            result = send_overdue_whatsapp(invoice_name)

            if result.get("status") == "Sent":
                frappe.db.set_value(
                    "Sales Invoice",
                    invoice_name,
                    "custom_overdue_whatsapp_sent",
                    1
                )

        except Exception:
            frappe.log_error(
                frappe.get_traceback(),
                f"Overdue WhatsApp Failed for {invoice_name}"
            )

def send_overdue_whatsapp(invoice_name):
    doc = frappe.get_doc("Sales Invoice", invoice_name)

    if doc.is_return or getattr(doc, "custom_is_replacement", 0):
        return {"status": "Skipped"}

    if not doc.contact_mobile:
        return {"status": "Skipped"}

    invoice_data = {
        "name": doc.name,
        "doctype": "Sales Invoice",
        "customer": doc.customer_name or doc.customer,
        "contact_mobile": doc.contact_mobile,
        "is_overdue": 1
    }

    whatsapp_settings = get_whatsapp_settings()

    return send_whatsapp_with_pdf_overdue(
        invoice_data,
        whatsapp_settings["api_key"],
        whatsapp_settings["url"]
    )

def send_whatsapp_with_pdf_overdue(invoice, api_key, url):
    file_url = generate_public_pdf(invoice["name"], invoice["doctype"])

    # ✅ Fetch outstanding amount
    outstanding_amount = frappe.db.get_value(
        "Sales Invoice",
        invoice["name"],
        "outstanding_amount"
    )

    data = {
        "apiKey": api_key,
        "campaignName": "invoice_overdue_reminder",
        "destination": invoice["contact_mobile"],
        "userName": invoice["customer"],
        "source": invoice["doctype"],
        "media": {
            "url": file_url,
            "filename": f"{invoice['name']}.pdf"
        },
        "templateParams": [
            invoice["customer"],                # {{1}} Customer Name
            invoice["name"],                    # {{2}} Invoice Number
            f"{outstanding_amount:.2f}"         # {{3}} Amount
        ],
        "tags": ["Sales Invoice", "Overdue"]
    }

    response = requests.post(url, json=data, timeout=10)

    status = "Sent" if response.status_code == 200 else "Not Sent"

    log_whatsapp_status(
        invoice["name"],
        invoice["doctype"],
        invoice["customer"],
        invoice["contact_mobile"],
        file_url,
        response.text,
        status
    )

    return {"status": status}

