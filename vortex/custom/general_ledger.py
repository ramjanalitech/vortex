import frappe
import requests
import json
from frappe.utils import get_bench_path, get_site_path, get_url
from frappe.utils.file_manager import save_file
from frappe.utils.pdf import get_pdf
import base64
from frappe import _
from erpnext.accounts.report.general_ledger.general_ledger import execute
import random
import string

@frappe.whitelist()
def whatsapp_get_doc(doc, file_url, method=None):
    doc = json.loads(doc)
    whatsapp_settings = frappe.get_doc("Whatsapp Setting")

    report_name = "General Ledger"
    url = whatsapp_settings.url
    api_key = whatsapp_settings.api_key

    # Fetch mobile number based on party
    party_type = doc.get('party_type')
    party_name = doc.get('party_name')
    destination = get_mobile_number(party_type, party_name)
    frappe.msgprint(f"Mobile Number: {destination}")
    
    if not destination:
        frappe.msgprint(f"No mobile number found for {party_type} {party_name}")
        return
    
    user_name = doc.get('user_name', frappe.session.user)
    if not user_name:
        frappe.msgprint("userName is required")
        return

    headers = {"Content-Type": "application/json"}
    data = {
        "apiKey": api_key,
        "campaignName": get_campaign_name(report_name),
        "destination": destination,
        "userName": "party_name",  # Use user_name directly
        "source": "General Ledger",
        "media": {
            
        },
        "templateParams": [
            file_url
        ],
        "tags": ["string"]
    }

    req = requests.post(url, data=json.dumps(data), headers=headers)
    log_whatsapp_response(req, report_name, file_url)

def get_campaign_name(report_name):
    whatsapp_campaign_report = frappe.get_doc('Whatsapp Setting')
    for camp_name in whatsapp_campaign_report.whatsapp_campaign_report:
        if camp_name.campaign_report == report_name:
            frappe.msgprint(f"Campaign Name: {camp_name.campaign_name}")
            return camp_name.campaign_name
    return None

def generate_random_string(length):
    letters = string.digits  # includes digits 0-9
    result_str = ''.join(random.choice(letters) for _ in range(length))
    return result_str

@frappe.whitelist()
def create_statement_account(doc):
    doc = json.loads(doc)
    soa = frappe.new_doc("Process Statement Of Accounts")
    soa.name = generate_random_string(5)
    soa.company = doc.get("company")
    soa.from_date = doc.get("from_date")
    soa.to_date = doc.get("to_date")
    soa.finance_book = doc.get("finance_book")
    soa.append("customers", {
        "customer": doc.get("party_name")
    })
    soa.save(ignore_permissions=True)

    return soa.name

def get_mobile_number(party_type, party_name):
    contact_fields = {
        "Customer": ("Customer", "mobile_no"),
        "Supplier": ("Contact", "mobile_no"),
        "Employee": ("Employee", "cell_number as mobile_no")
    }
    if party_type in contact_fields:
        doctype, field = contact_fields[party_type]
        contact = frappe.get_value(doctype, {"name": party_name}, field, as_dict=True)
        return contact.mobile_no if contact else None
    return None

def log_whatsapp_response(req, report_name, file_url):
    status = "Sent" if req.status_code == 200 else "Not Sent"
    new_doc = frappe.new_doc("Whatsapp Log")
    new_doc.doctype_name = report_name
    new_doc.url = str(file_url)
    new_doc.response = req.text
    new_doc.document_name = report_name
    new_doc.status = status
    new_doc.save()
    
    frappe.msgprint(f"Whatsapp SMS {status}")

def make_access_log(file_type, method, page):
    # Assuming this function exists to log access
    frappe.get_doc({
        "doctype": "Access Log",
        "file_type": file_type,
        "method": method,
        "page": page
    }).insert()
