# # import frappe 
# # import requests
# # import json
# # from frappe.utils import get_url
# # from frappe.utils import get_url_to_form, now_datetime, get_fullname, get_bench_path, get_site_path, get_request_site_address
# # from frappe.utils.pdf import get_pdf
# # from frappe.utils.file_manager import save_file
# # import base64
# # import os

# # @frappe.whitelist()
# # def whatsapp_get_doc(doc,method=None):
# # 	doc= json.loads(doc)
# # 	document=frappe.get_doc("Whatsapp Setting")
# # 	sales_invoice_name = doc['name']
# # 	url=document.url
# # 	api_key = document.api_key
# # 	whatsapp_camapaign = frappe.get_doc('Whatsapp Setting')
# # 	for camp_name in whatsapp_camapaign.whatsapp_campaign:
# # 		if camp_name.campaign_doctype == "Sales Invoice":
# # 			payment_campaign = camp_name.campaign_name
# # 	campaign_name = payment_campaign
# # 	destination = doc['contact_mobile']
# # 	pdf_link = get_sales_invoice_pdf_link(sales_invoice_name)
# # 	# template_params = doc['sales_order']
# # 	fileurl = pdfurl_generate(pdf_link,"Sales Invoice",sales_invoice_name)
# # 	headers = {"Content-Type": "application/json"}
# # 	data = {
# # 				"apiKey": api_key,
# # 				"campaignName": campaign_name,
# # 				"destination": destination,
# # 				"userName": doc['customer'],
# # 				"source": "Sales Invoice",
# # 				"media": {
# # 				"url": fileurl,
# # 				"filename": doc['customer']
# # 				},
# # 				"templateParams": [

# # 				],
# # 				"tags": [
# # 				"string"
# # 				]
# # 				}
# # 	req = requests.post(url, data=json.dumps(data), headers=headers)	
# # 	if req.status_code == 200:
# # 		new_doc = frappe.new_doc("Whatsapp Log")
# # 		new_doc.doctype_name = "Sales Invoice"
# # 		new_doc.url = str(fileurl)
# # 		new_doc.response = req
# # 		new_doc.document_name = sales_invoice_name
# # 		new_doc.status = "Sent"
# # 		new_doc.save()
# # 		frappe.msgprint("Whatsapp SMS Sent ")
# # 	else:
# # 		new_doc = frappe.new_doc("Whatsapp Log")
# # 		new_doc.doctype_name = "Sales Invoice"
# # 		new_doc.url = str(fileurl)
# # 		new_doc.response = req
# # 		new_doc.document_name = sales_invoice_name
# # 		new_doc.status = "Not Sent"
# # 		new_doc.save()
# # 		frappe.msgprint("Whatsapp SMS Not Sent ")
	
# # def get_sales_invoice_pdf_link(doc):
# # 	docname = frappe.get_doc("Sales Invoice",doc)
# # 	key = docname.get_document_share_key( expires_on=None,no_expiry=True)
# # 	print_format = "Standard"
# # 	doctype = frappe.get_doc("DocType", docname)
# # 	if doctype.custom:
# # 		if doctype.default_print_format:
# # 			print_format = doctype.default_print_format
# # 	else:
# # 		default_print_format = frappe.db.get_value("Property Setter",filters={"doc_type": "Sales Invoice","property": "default_print_format"},fieldname="value")
# # 		print_format = default_print_format if default_print_format else print_format

# # 	link = get_pdf_link("Sales Invoice",docname.name,print_format=print_format)
# # 	filename = f'{docname}.pdf'
# # 	url = f'{frappe.utils.get_url()}{link}&key={key}'
# # 	return url

# # def pdfurl_generate(pdf_link,doctype,docname): 
# # 	base_path = frappe.db.get_single_value('Whatsapp Setting','base_path')
# # 	bench_path = get_bench_path()
# # 	site_path = get_site_path().replace(".", "/sites",1)
# # 	base_path_ = bench_path + site_path
# # 	file_name = frappe.generate_hash("",5) + ".pdf"
# # 	cert_file_name = "cert_" + file_name
# # 	headers = {'Content-Type': 'application/json'}
# # 	cert_url = pdf_link
# # 	certificate_response = requests.get(cert_url,headers=headers)
# # 	cert_file_path = "/public/files/" + cert_file_name
# # 	cert_file = open(base_path_ + cert_file_path, "wb")
# # 	cert_file.write(certificate_response.content)
# # 	cert_file.close()
# # 	pdf_file = save_file(fname=cert_file_name, content=base64.b64encode(certificate_response.content),dt=doctype, dn=docname, decode=True, is_private=0)

# # 	file_url = base_path + pdf_file.file_url 	
# # 	return file_url

# # def get_pdf_link(doctype, docname, print_format="Standard", no_letterhead=0):
# # 	return "/api/method/frappe.utils.print_format.download_pdf?doctype={doctype}&name={docname}&format={print_format}&no_letterhead={no_letterhead}".format(
# # 		doctype=doctype, docname=docname, print_format=print_format, no_letterhead=no_letterhead)

# # import frappe
# # import requests
# # import json
# # from frappe.utils import nowdate
# # from frappe.utils.file_manager import save_file
# # from frappe.utils.pdf import get_pdf
# # import base64

# # def send_sales_invoices_whatsapp():
# #     # Fetch Sales Invoices with today's posting date
# #     sales_invoices = frappe.get_all('Sales Invoice', filters={
# #         'posting_date': nowdate(),
# #         'status': 'Unpaid'  # Example: Only unpaid invoices
# #     }, fields=['name', 'customer', 'contact_mobile', 'grand_total'])

# #     if not sales_invoices:
# #         frappe.msgprint("No Sales Invoices to send via WhatsApp today.")
# #         return

# #     # Get WhatsApp settings
# #     whatsapp_settings = frappe.get_doc("Whatsapp Setting")
# #     url = whatsapp_settings.url
# #     api_key = whatsapp_settings.api_key

# #     for invoice in sales_invoices:
# #         try:
# #             # Get PDF link for the Sales Invoice
# #             pdf_link = get_sales_invoice_pdf_link(invoice.name)
# #             file_url = pdfurl_generate(pdf_link, "Sales Invoice", invoice.name)

# #             # Prepare WhatsApp message data
# #             headers = {"Content-Type": "application/json"}
# #             data = {
# #                 "apiKey": api_key,
# #                 "campaignName": get_campaign_name("Sales Invoice"),
# #                 "destination": invoice.contact_mobile,
# #                 "userName": invoice.customer,
# #                 "source": "Sales Invoice",
# #                 "media": {
# #                     "url": file_url,
# #                     "filename": invoice.customer
# #                 },
# #                 "templateParams": [],
# #                 "tags": ["Sales Invoice"]
# #             }

# #             # Send the request to WhatsApp API
# #             response = requests.post(url, data=json.dumps(data), headers=headers)

# #             # Check response and log status
# #             status = "Sent" if response.status_code == 200 else "Not Sent"
# #             log_whatsapp_status(invoice.name, file_url, response.text, status)

# #         except Exception as e:
# #             frappe.log_error(frappe.get_traceback(), f"Error sending WhatsApp message for {invoice.name}")

# # def get_campaign_name(doctype):
# #     """Fetch the campaign name for the specified doctype from Whatsapp Setting."""
# #     whatsapp_campaign = frappe.get_doc("Whatsapp Setting")
# #     for campaign in whatsapp_campaign.whatsapp_campaign:
# #         if campaign.campaign_doctype == doctype:
# #             return campaign.campaign_name
# #     frappe.throw(f"No WhatsApp campaign found for {doctype}")

# # def get_sales_invoice_pdf_link(docname):
# #     """Get a public link to download the Sales Invoice PDF."""
# #     doc = frappe.get_doc("Sales Invoice", docname)
# #     key = doc.get_document_share_key(expires_on=None, no_expiry=True)
# #     print_format = frappe.db.get_value("Property Setter", {
# #         "doc_type": "Sales Invoice", "property": "default_print_format"}, "value") or "Standard"
# #     return f"{frappe.utils.get_url()}/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Invoice&name={docname}&format={print_format}&key={key}"

# # def pdfurl_generate(pdf_link, doctype, docname):
# #     """Generate a PDF file and save it, returning the file's public URL."""
# #     response = requests.get(pdf_link)
# #     file_name = f"{frappe.generate_hash('', 5)}.pdf"
# #     file_path = f"/public/files/{file_name}"

# #     # Save PDF to file system
# #     with open(frappe.get_site_path() + file_path, "wb") as file:
# #         file.write(response.content)

# #     # Save the file in ERPNext
# #     saved_file = save_file(fname=file_name, content=base64.b64encode(response.content),
# #                            dt=doctype, dn=docname, decode=True, is_private=0)
# #     return frappe.utils.get_url() + saved_file.file_url

# # def log_whatsapp_status(docname, file_url, response, status):
# #     """Log the WhatsApp message status."""
# #     new_log = frappe.new_doc("Whatsapp Log")
# #     new_log.doctype_name = "Sales Invoice"
# #     new_log.url = file_url
# #     new_log.response = response
# #     new_log.document_name = docname
# #     new_log.status = status
# #     new_log.save()

# import frappe
# import requests
# import json
# from frappe.utils import nowdate, get_bench_path, get_site_path, get_url
# from frappe.utils.file_manager import save_file
# from frappe.utils.pdf import get_pdf
# import base64
# from frappe.utils.background_jobs import enqueue

# # Function to schedule sending WhatsApp messages at 9 PM every night
# def schedule_sales_invoices_whatsapp():
#     # Schedule the function to run at 9 PM daily
#     enqueue(send_sales_invoices_whatsapp, queue='long', timeout=6000, job_name="Send Sales Invoices via WhatsApp")

# # Function to send Sales Invoices for today via WhatsApp
# @frappe.whitelist()
# def send_sales_invoices_whatsapp():
#     # Fetch Sales Invoices with today's posting date
#     sales_invoices = frappe.get_all('Sales Invoice', filters={
#         'posting_date': nowdate(),
#         'status': 'Unpaid'  # Example: Only unpaid invoices
#     }, fields=['name', 'customer', 'contact_mobile', 'grand_total'])

#     if not sales_invoices:
#         frappe.msgprint("No Sales Invoices to send via WhatsApp today.")
#         return

#     # Get WhatsApp settings
#     whatsapp_settings = frappe.get_doc("Whatsapp Setting")
#     url = whatsapp_settings.url
#     api_key = whatsapp_settings.api_key

#     for invoice in sales_invoices:
#         send_invoice_whatsapp(invoice, api_key, url)

# # Function to send a specific Sales Invoice via WhatsApp (manual or automatic)
# @frappe.whitelist()
# def whatsapp_get_doc(doc, method=None):
#     doc = json.loads(doc)
#     sales_invoice_name = doc['name']
#     destination = doc['contact_mobile']
#     customer_name = doc['customer']

#     # Get WhatsApp settings
#     whatsapp_settings = frappe.get_doc("Whatsapp Setting")
#     url = whatsapp_settings.url
#     api_key = whatsapp_settings.api_key

#     # Send the single invoice
#     send_invoice_whatsapp({
#         'name': sales_invoice_name,
#         'customer': customer_name,
#         'contact_mobile': destination
#     }, api_key, url)

# # Function to send a Sales Invoice through WhatsApp
# def send_invoice_whatsapp(invoice, api_key, url):
#     try:
#         # Get PDF link for the Sales Invoice
#         pdf_link = get_sales_invoice_pdf_link(invoice['name'])
#         file_url = pdfurl_generate(pdf_link, "Sales Invoice", invoice['name'])

#         # Prepare WhatsApp message data
#         headers = {"Content-Type": "application/json"}
#         data = {
#             "apiKey": api_key,
#             "campaignName": get_campaign_name("Sales Invoice"),
#             "destination": invoice['contact_mobile'],
#             "userName": invoice['customer'],
#             "source": "Sales Invoice",
#             "media": {
#                 "url": file_url,
#                 "filename": invoice['customer']
#             },
#             "templateParams": [],
#             "tags": ["Sales Invoice"]
#         }

#         # Send the request to WhatsApp API
#         response = requests.post(url, data=json.dumps(data), headers=headers)

#         # Check response and log status
#         status = "Sent" if response.status_code == 200 else "Not Sent"
#         log_whatsapp_status(invoice['name'], file_url, response.text, status)
#         # Notify user if successfully sent
#         if status == "Sent":
#             frappe.msgprint("WhatsApp SMS Sent")
#         else:
#             frappe.msgprint(f"Failed to send WhatsApp SMS for {invoice['name']}")

#     except Exception as e:
#         frappe.log_error(frappe.get_traceback(), f"Error sending WhatsApp message for {invoice['name']}")

# # Function to get campaign name for the Sales Invoice
# def get_campaign_name(doctype):
#     """Fetch the campaign name for the specified doctype from Whatsapp Setting."""
#     whatsapp_campaign = frappe.get_doc("Whatsapp Setting")
#     for campaign in whatsapp_campaign.whatsapp_campaign:
#         if campaign.campaign_doctype == doctype:
#             return campaign.campaign_name
#     frappe.throw(f"No WhatsApp campaign found for {doctype}")

# # Function to get the public link of Sales Invoice PDF
# def get_sales_invoice_pdf_link(docname):
#     """Get a public link to download the Sales Invoice PDF."""
#     doc = frappe.get_doc("Sales Invoice", docname)
#     key = doc.get_document_share_key(expires_on=None, no_expiry=True)
#     print_format = frappe.db.get_value("Property Setter", {
#         "doc_type": "Sales Invoice", "property": "default_print_format"}, "value") or "Standard"
#     return f"{frappe.utils.get_url()}/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Invoice&name={docname}&format={print_format}&key={key}"

# # Function to generate PDF URL and save the file in ERPNext
# def pdfurl_generate(pdf_link, doctype, docname):
#     """Generate a PDF file and save it, returning the file's public URL."""
#     response = requests.get(pdf_link)
#     file_name = f"{frappe.generate_hash('', 5)}.pdf"
#     file_path = f"/public/files/{file_name}"

#     # Save PDF to file system
#     with open(frappe.get_site_path() + file_path, "wb") as file:
#         file.write(response.content)

#     # Save the file in ERPNext
#     saved_file = save_file(fname=file_name, content=base64.b64encode(response.content),
#                            dt=doctype, dn=docname, decode=True, is_private=0)
#     return frappe.utils.get_url() + saved_file.file_url

# # Function to log the status of the WhatsApp message
# def log_whatsapp_status(docname, file_url, response, status):
#     """Log the WhatsApp message status."""
#     new_log = frappe.new_doc("Whatsapp Log")
#     new_log.doctype_name = "Sales Invoice"
#     new_log.url = file_url
#     new_log.response = response
#     new_log.document_name = docname
#     new_log.status = status
#     new_log.save()

import frappe
import requests
import json
from frappe.utils import nowdate, get_bench_path, get_site_path, get_url
from frappe.utils.file_manager import save_file
from frappe.utils.pdf import get_pdf
import base64
from frappe.utils.background_jobs import enqueue

# Function to schedule sending WhatsApp messages at 9 PM every night
def schedule_sales_invoices_whatsapp():
    # Schedule the function to run at 9 PM daily
    enqueue(send_sales_invoices_whatsapp, queue='long', timeout=6000, job_name="Send Sales Invoices via WhatsApp")

# Function to send Sales Invoices for today via WhatsApp
@frappe.whitelist()
def send_sales_invoices_whatsapp():
    sales_invoices = frappe.get_all('Sales Invoice', filters={
        'posting_date': nowdate(),
        'status': 'Unpaid'  # Example: Only unpaid invoices
    }, fields=['name', 'customer', 'contact_mobile', 'grand_total'])

    if not sales_invoices:
        frappe.msgprint("No Sales Invoices to send via WhatsApp today.")
        return

    try:
        whatsapp_settings = frappe.get_doc("Whatsapp Setting")
        url = whatsapp_settings.url
        api_key = whatsapp_settings.api_key
    except frappe.DoesNotExistError:
        frappe.msgprint("WhatsApp settings not found.")
        return

    for invoice in sales_invoices:
        send_invoice_whatsapp(invoice, api_key, url)

# Function to send a specific Sales Invoice via WhatsApp (manual or automatic)
@frappe.whitelist()
def whatsapp_get_doc(doc, method=None):
    doc = json.loads(doc)
    sales_invoice_name = doc['name']
    destination = doc['contact_mobile']
    customer_name = doc['customer']

    try:
        whatsapp_settings = frappe.get_doc("Whatsapp Setting")
        url = whatsapp_settings.url
        api_key = whatsapp_settings.api_key
    except frappe.DoesNotExistError:
        frappe.msgprint("WhatsApp settings not found.")
        return

    send_invoice_whatsapp({
        'name': sales_invoice_name,
        'customer': customer_name,
        'contact_mobile': destination
    }, api_key, url)

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
                "filename": invoice['customer']
            },
            "templateParams": [],
            "tags": ["Sales Invoice"]
        }

        response = requests.post(url, data=json.dumps(data), headers=headers)
        status = "Sent" if response.status_code == 200 else "Not Sent"
        log_whatsapp_status(invoice['name'], file_url, response.text, status)

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
def get_sales_invoice_pdf_link(docname):
    doc = frappe.get_doc("Sales Invoice", docname)
    key = doc.get_document_share_key(expires_on=None, no_expiry=True)
    print_format = frappe.db.get_value("Property Setter", {
        "doc_type": "Sales Invoice", "property": "default_print_format"}, "value") or "Standard"
    return f"{frappe.utils.get_url()}/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Invoice&name={docname}&format={print_format}&key={key}"

# Function to generate PDF URL and save the file in ERPNext
def pdfurl_generate(pdf_link, doctype, docname):
    response = requests.get(pdf_link)
    file_name = f"{frappe.generate_hash('', 5)}.pdf"
    file_path = f"/public/files/{file_name}"

    with open(frappe.get_site_path() + file_path, "wb") as file:
        file.write(response.content)

    saved_file = save_file(fname=file_name, content=base64.b64encode(response.content),
                           dt=doctype, dn=docname, decode=True, is_private=0)
    return frappe.utils.get_url() + saved_file.file_url

# Function to log the status of the WhatsApp message
def log_whatsapp_status(docname, file_url, response, status):
    new_log = frappe.new_doc("Whatsapp Log")
    new_log.doctype_name = "Sales Invoice"
    new_log.url = file_url
    new_log.response = response
    new_log.document_name = docname
    new_log.status = status
    new_log.save()
