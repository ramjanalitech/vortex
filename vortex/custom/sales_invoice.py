import frappe
import requests
import json
from frappe.utils import nowdate, get_url, get_site_path
from frappe.utils.file_manager import save_file
from frappe.utils.pdf import get_pdf
from frappe.utils.background_jobs import enqueue
import base64


# Function to schedule sending WhatsApp messages at 9 PM every night
def schedule_sales_invoices_whatsapp():
    """Schedule the function to run at 9 PM daily."""
    enqueue(send_sales_invoices_in_batches, queue='long', timeout=6000, job_name="Send Sales Invoices via WhatsApp")

# Main function to send Sales Invoices via WhatsApp in batches
@frappe.whitelist()
def send_sales_invoices_in_batches(batch_size=50):
    sales_invoices = frappe.get_all('Sales Invoice', filters={
        'posting_date': nowdate(),
        'status': 'Unpaid'
    }, fields=['name', 'customer', 'contact_mobile', 'grand_total'])

    if not sales_invoices:
        frappe.msgprint("No Sales Invoices to send via WhatsApp today.")
        return

    for i in range(0, len(sales_invoices), batch_size):
        batch = sales_invoices[i:i + batch_size]
        enqueue(send_sales_invoice_batch, invoices=batch)

# Function to process a batch of Sales Invoices
def send_sales_invoice_batch(invoices):
    try:
        whatsapp_settings = get_whatsapp_settings()
    except frappe.ValidationError as e:
        frappe.log_error(str(e), "WhatsApp Settings Error")
        return

    for invoice in invoices:
        if not invoice.get('contact_mobile'):
            frappe.msgprint(f"Skipping Sales Invoice {invoice['name']} due to missing contact mobile.")
            continue
        send_invoice_whatsapp(invoice, whatsapp_settings['api_key'], whatsapp_settings['url'])

# Function to send a specific Sales Invoice via WhatsApp (manual or automatic)
@frappe.whitelist()
def whatsapp_get_doc(doc, method=None):
    doc = json.loads(doc)
    sales_invoice_name = doc['name']
    destination = doc['contact_mobile']
    customer_name = doc['customer']

    try:
        whatsapp_settings = get_whatsapp_settings()
    except frappe.ValidationError as e:
        frappe.throw(str(e))

    send_invoice_whatsapp({
        'name': sales_invoice_name,
        'customer': customer_name,
        'contact_mobile': destination
    }, whatsapp_settings['api_key'], whatsapp_settings['url'])

# Helper function to fetch WhatsApp settings
def get_whatsapp_settings():
    try:
        whatsapp_settings = frappe.get_doc("Whatsapp Setting")
        if not whatsapp_settings.url or not whatsapp_settings.api_key:
            frappe.throw("WhatsApp settings are incomplete. Please configure URL and API Key.")
        return {"url": whatsapp_settings.url, "api_key": whatsapp_settings.api_key}
    except frappe.DoesNotExistError:
        frappe.throw("WhatsApp settings not found. Please configure 'Whatsapp Setting'.")

# Function to send a Sales Invoice through WhatsApp
def send_invoice_whatsapp(invoice, api_key, url):
    try:
        pdf_link = get_sales_invoice_pdf_link(invoice['name'])
        file_url = pdfurl_generate(pdf_link, "Sales Invoice", invoice['name'])

        headers = {"Content-Type": "application/json"}
        data = {
            "apiKey": api_key,
            "campaignName": get_campaign_name("Sales Invoice"),
            "destination": invoice['contact_mobile'],
            "userName": invoice['customer'],
            "source": "Sales Invoice",
            "media": {
                "url": file_url,
                "filename": f"{invoice['name']}.pdf"
            },
            "templateParams": [],
            "tags": ["Sales Invoice"]
        }

        response = requests.post(url, data=json.dumps(data), headers=headers)
        status = "Sent" if response.status_code == 200 else "Not Sent"

        log_whatsapp_status(invoice['name'], file_url, response.text, status, invoice['customer'])

        if status == "Sent":
            frappe.msgprint(f"WhatsApp SMS sent successfully for {invoice['name']}")
        else:
            frappe.msgprint(f"Failed to send WhatsApp SMS for {invoice['name']}")

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), f"Error sending WhatsApp message for {invoice['name']}")

# Function to get campaign name for the Sales Invoice
def get_campaign_name(doctype):
    try:
        whatsapp_campaign = frappe.get_doc("Whatsapp Setting")
        for campaign in whatsapp_campaign.whatsapp_campaign:
            if campaign.campaign_doctype == doctype:
                return campaign.campaign_name
    except frappe.DoesNotExistError:
        frappe.throw("No WhatsApp campaign settings found.")

    frappe.throw(f"No WhatsApp campaign found for {doctype}")

# Function to get the public link of Sales Invoice PDF
# def get_sales_invoice_pdf_link(docname):
#     doc = frappe.get_doc("Sales Invoice", docname)
#     key = doc.get_document_share_key(expires_on=None, no_expiry=True)
#     print_format = frappe.db.get_value("Property Setter", {
#         "doc_type": "Sales Invoice", "property": "default_print_format"}, "value") or "Standard"
#     return f"{get_url()}/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Invoice&name={docname}&format={print_format}&key={key}"

# Function to get the public link of Sales Invoice PDF
def get_sales_invoice_pdf_link(docname):
    try:
        doc = frappe.get_doc("Sales Invoice", docname)
        key = doc.get_document_share_key(expires_on=None, no_expiry=True)
        print_format = (
            frappe.db.get_value(
                "Property Setter", 
                {"doc_type": "Sales Invoice", "property": "default_print_format"}, 
                "value"
            ) or "Standard"
        )
        return (
            f"{frappe.utils.get_url()}/api/method/frappe.utils.print_format.download_pdf"
            f"?doctype=Sales%20Invoice&name={docname}&format={print_format}&key={key}"
        )
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Error in PDF Generation URL")
        frappe.throw("Failed to generate PDF link.")

# Function to generate PDF URL and save the file in ERPNext
def pdfurl_generate(pdf_link, doctype, docname):
    response = requests.get(pdf_link)
    file_name = f"{frappe.generate_hash('', 5)}.pdf"
    file_path = f"/public/files/{file_name}"

    with open(get_site_path() + file_path, "wb") as file:
        file.write(response.content)

    saved_file = save_file(fname=file_name, content=base64.b64encode(response.content),
                           dt=doctype, dn=docname, decode=True, is_private=0)
    return get_url() + saved_file.file_url

# Function to log the status of the WhatsApp message
def log_whatsapp_status(docname, file_url, response, status, customer):
    """Log the WhatsApp message status with customer name."""
    new_log = frappe.new_doc("Whatsapp Log")
    new_log.doctype_name = "Sales Invoice"
    new_log.document_name = docname
    new_log.customer = customer
    new_log.url = file_url
    new_log.response = response
    new_log.status = status
    new_log.save()
