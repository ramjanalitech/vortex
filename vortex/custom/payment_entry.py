import frappe
import json
import requests
from frappe.utils.pdf import get_pdf
from frappe.utils import get_url
from frappe import _

# ---------------- PAYMENT ENTRY ---------------- #

@frappe.whitelist()
def generate_pdf_and_send_whatsapp_on_submit_payment(doc, method=None):
    result = send_whatsapp_message_payment(doc.name, "Payment Entry")
    if result.get("status") == "Sent":
        frappe.msgprint(_("WhatsApp message sent successfully to {0}").format(result.get("mobile")))
    else:
        frappe.msgprint(_("Failed to send WhatsApp message. Reason: {0}").format(result.get("message")))


# ---------------- COMMON BUTTON ---------------- #

@frappe.whitelist()
def send_whatsapp_button(docname, doctype):
    if doctype == "Payment Entry":
        result = send_whatsapp_message_payment(docname, doctype)
    else:
        result = send_whatsapp_message(docname, doctype)

    if result.get("status") == "Sent":
        frappe.msgprint(_("WhatsApp message sent successfully to {0}").format(result.get("mobile")))
    else:
        frappe.msgprint(_("Failed to send WhatsApp message. Reason: {0}").format(result.get("message")))
    return result


# ---------------- PAYMENT ENTRY MESSAGE ---------------- #

def send_whatsapp_message_payment(docname, doctype):
    doc = frappe.get_doc(doctype, docname)

    mobile = getattr(doc, "contact_mobile", None)

    # If mobile not on Payment Entry, fetch from linked Customer/Supplier
    if not mobile and doc.party_type and doc.party:
        if doc.party_type == "Customer":
            mobile = frappe.db.get_value("Customer", doc.party, "mobile_no")
        elif doc.party_type == "Supplier":
            mobile = frappe.db.get_value("Supplier", doc.party, "mobile_no")

    if not mobile:
        frappe.throw(_("Contact number is missing. Please update the Party's mobile number."))

    party_name = getattr(doc, "party_name", None) or getattr(doc, "party", None)

    payment_data = {
        "name": docname,
        "doctype": doctype,
        "customer": party_name,   # reusing "customer" key to keep send_whatsapp_with_pdf compatible
        "contact_mobile": mobile
    }

    whatsapp_settings = get_whatsapp_settings()

    return send_whatsapp_with_pdf(payment_data, whatsapp_settings["api_key"], whatsapp_settings["url"])


# ---------------- SETTINGS ---------------- #

def get_whatsapp_settings():
    try:
        whatsapp_settings = frappe.get_doc("Whatsapp Setting")
        if not whatsapp_settings.url or not whatsapp_settings.api_key:
            frappe.throw(_("WhatsApp settings are incomplete. Please configure URL and API Key."))
        return {"url": whatsapp_settings.url, "api_key": whatsapp_settings.api_key}
    except frappe.DoesNotExistError:
        frappe.throw(_("WhatsApp settings not found. Please configure 'Whatsapp Setting'."))

def get_campaign_name(doctype):
    try:
        whatsapp_campaign = frappe.get_doc("Whatsapp Setting")
        for campaign in whatsapp_campaign.whatsapp_campaign:
            if campaign.campaign_doctype == doctype:
                return campaign.campaign_name
    except frappe.DoesNotExistError:
        frappe.throw(_("No WhatsApp campaign settings found."))

    frappe.throw(_("No WhatsApp campaign found for {0}").format(doctype))


# ---------------- SEND MESSAGE ---------------- #

def send_whatsapp_with_pdf(invoice, api_key, url):
    try:
        # Generate public URL to PDF
        file_url = generate_public_pdf(invoice["name"], invoice["doctype"])
        
        headers = {"Content-Type": "application/json"}
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
            # 👇 Always pass paid amount as template param
            "templateParams": [str(frappe.db.get_value(invoice["doctype"], invoice["name"], "paid_amount"))],
            "tags": [invoice["doctype"]]
        }

        frappe.logger().debug(f"Sending WhatsApp: {json.dumps(data)}")

        response = requests.post(url, data=json.dumps(data), headers=headers, timeout=10)
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
        frappe.log_error(frappe.get_traceback(), f"Error sending WhatsApp message for {invoice['name']}")
        return {
            "status": "Failed",
            "message": str(e),
            "mobile": invoice["contact_mobile"]
        }


# ---------------- PDF GENERATION ---------------- #

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


# ---------------- LOGGING ---------------- #

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
        frappe.log_error(frappe.get_traceback(), f"Failed to log WhatsApp for {docname}")
