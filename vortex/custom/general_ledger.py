import frappe
import requests
import json
from frappe.utils import get_bench_path, get_site_path, get_url
from frappe.utils.file_manager import save_file
from frappe.utils.pdf import get_pdf
import base64
from frappe import _
from erpnext.accounts.report.general_ledger.general_ledger import execute

@frappe.whitelist()
def whatsapp_get_doc(doc, method=None):
    doc = json.loads(doc)
    whatsapp_settings = frappe.get_doc("Whatsapp Setting")

    report_name = "General Ledger"
    url = whatsapp_settings.url
    api_key = whatsapp_settings.api_key

    # Fetch mobile number based on party
    # party_type = doc.get('party_type')
    # party_name = doc.get('party_name')
    # destination = get_mobile_number(party_type, party_name)
    # frappe.msgprint(f"Mobile Number: {destination}")
    

    pdf_link = get_general_ledger_pdf_link(doc)
    
    # Check if 'custom_params' exists, if not provide an empty list
    template_params = doc.get('custom_params', [])

    file_url = generate_pdf_url(pdf_link, "Report", "General Ledger")

    headers = {"Content-Type": "application/json"}
    data = {
        "apiKey": api_key,
        "campaignName": "monthly_ledger_new",
        "destination": "7698737440",
        "userName": "party_name", # doc.get('user_name', ''),  # Default to empty string if 'user_name' is missing
        "source": "General Ledger",
        "media": {
            "url": file_url,
            "filename": report_name
        },
        "templateParams": [
					
		],
        "tags": ["string"]
    }

    req = requests.post(url, data=json.dumps(data), headers=headers)
    log_whatsapp_response(req, report_name, file_url)

# This Is Working Data 
def get_general_ledger_pdf_link(doc):
    filters = {
        "company": doc.get("company"),
        "from_date": doc.get("from_date"),
        "to_date": doc.get("to_date"),
        "finance_book": doc.get("finance_book"),
        "project": doc.get("project"),
        "cost_center": doc.get("cost_center")
    }

    try:
        frappe.msgprint(f"Attempting to fetch report: General Ledger with filters: {filters}")

        # Fetch report HTML using filters
        # report_html = frappe.get_print("Report", "General Ledger", filters, doc.get("format") or "Standard")

        report_filters = frappe.parse_json(filters) if filters else {}
        columns, data = execute(report_filters)

        base_template_path = "frappe/www/printview.html"
        template_path = (
            "erpnext/accounts/doctype/process_statement_of_accounts/process_statement_of_accounts.html"
            if doc.report == "General Ledger"
            else "erpnext/accounts/doctype/process_statement_of_accounts/process_statement_of_accounts_accounts_receivable.html"
        )
        report_html = frappe.render_template(
		template_path,
		{
			"filters": filters,
			"data": res,
			"report": {"report_name": doc.report, "columns": col},
			"ageing": ageing[0] if (doc.include_ageing and ageing) else None,
			"letter_head": letter_head if doc.letter_head else None
			if doc.terms_and_conditions
			else None,
		},
        )

        frappe.msgprint(f"Fetched report HTML successfully: {report_html} characters")

        # Convert HTML to PDF
        pdf_data = get_pdf(report_html)
        frappe.msgprint(f"Converted HTML to PDF successfully, PDF size: {len(pdf_data)} bytes")

        # Save PDF file
        file_name = "General_Ledger.pdf"
        file_doc = save_file(file_name, pdf_data, "Report", "General Ledger", is_private=0)
        frappe.msgprint(f"Saved PDF file successfully: {file_doc.file_url}")
        
        # Construct the full URL for the file
        file_url = get_url(file_doc.file_url)
        frappe.msgprint(f"Generated file URL: {file_url}")
        return file_url
    except Exception as e:
        frappe.log_error(f"Error generating PDF for General Ledger: {str(e)}")
        frappe.msgprint(f"Error generating PDF: {str(e)}")
        return None

@frappe.whitelist()
def report_to_pdf(html, orientation="Landscape"):
	make_access_log(file_type="PDF", method="PDF", page=html)
	frappe.local.response.filename = "report.pdf"
	frappe.local.response.filecontent = get_pdf(html, {"orientation": orientation})
	frappe.local.response.type = "pdf"
    
def generate_pdf_url(pdf_link, doctype, docname):
    base_path = frappe.db.get_single_value('Whatsapp Setting', 'base_path')
    bench_path = get_bench_path()
    site_path = get_site_path().replace(".", "/sites", 1)
    base_path_ = bench_path + site_path
    file_name = frappe.generate_hash("", 5) + ".pdf"
    cert_file_name = "cert_" + file_name

    headers = {'Content-Type': 'application/json'}
    cert_url = pdf_link
    certificate_response = requests.get(cert_url, headers=headers)
    
    cert_file_path = "/public/files/" + cert_file_name
    with open(base_path_ + cert_file_path, "wb") as cert_file:
        cert_file.write(certificate_response.content)
    
    pdf_file = save_file(fname=cert_file_name, content=base64.b64encode(certificate_response.content), dt=doctype, dn=docname, decode=True, is_private=0)
    
    # Construct the full URL for the file
    file_url = get_url(pdf_file.file_url)
    return file_url


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

