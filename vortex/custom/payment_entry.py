import frappe 
import requests
import json
from frappe.utils import get_url
from frappe.utils import get_url_to_form, now_datetime, get_fullname, get_bench_path, get_site_path, get_request_site_address
from frappe.utils.pdf import get_pdf
from frappe.utils.file_manager import save_file
import base64
import os


def payment_receipt(doc,method=None):
	document=frappe.get_doc("Whatsapp Setting")
	payment_entry_name = doc.name
	url=document.url
	api_key = document.api_key
	campaign_name =document.campaign_name
	phone_no = frappe.get_doc("Contact",doc.contact_person)
	destination = phone_no.mobile_no
	pdf_link = attach_paymententry_pdf(doc)
	headers = {"Content-Type": "application/json"}
	data = {
				"apiKey": api_key,
				"campaignName": campaign_name,
				"destination": destination,
				"userName": doc.company,
				"source": "Payment Entry",
				"media": {
				"url": pdf_link,
				"filename": doc.company
				},
				"templateParams": [
				],
				"tags": [
				"string"
				]
				}
	req = requests.post(url, data=json.dumps(data), headers=headers)	
	print("pdffffffffffffffffffffffffff",pdf_link)
	if req.status_code == 200:
		new_doc = frappe.new_doc("Whatsapp Log")
		new_doc.doctype_name = "Payment Entry"
		new_doc.url = pdf_link
		new_doc.response = req
		new_doc.document_name = payment_entry_name
		new_doc.status = "Sent"
		new_doc.save()
		# delete_file(doc,doc.name)
		frappe.msgprint("Whatsapp SMS Sent ")
	else:
		new_doc = frappe.new_doc("Whatsapp Log")
		new_doc.doctype_name = "Payment Entry"
		new_doc.url = pdf_link
		new_doc.response = req
		new_doc.document_name = payment_entry_name
		new_doc.status = "Not Sent"
		new_doc.save()
		frappe.msgprint("Whatsapp SMS Not Sent ")

		


def get_payment_entry_pdf_link(doc):
	docname = frappe.get_doc("Payment Entry",doc)	
	key = docname.get_document_share_key( expires_on=None,no_expiry=True)
	print_format = "Standard"
	doctype = frappe.get_doc("DocType", docname)
	if doctype.custom:
		if doctype.default_print_format:
			print_format = doctype.default_print_format
	else:
		default_print_format = frappe.db.get_value("Property Setter",filters={"doc_type": "Payment Entry","property": "default_print_format"},fieldname="value")
		print_format = default_print_format if default_print_format else print_format

	link = get_pdf_link("Payment Entry",docname.name,print_format=print_format)
	filename = f'{docname}.pdf'
	url = f'{frappe.utils.get_url()}{link}&key={key}'
	return url


def attach_paymententry_pdf(doc, log=None):
	filename = doc.name
	pdf_content = frappe.get_print("Payment Entry",doc.name,doc=doc,no_letterhead=True,as_pdf=True)
	pdf_file =  save_file(filename, pdf_content, "Payment Entry", doc.name, is_private=0)
	base_path = frappe.db.get_single_value('Whatsapp Setting','base_path')
	file_url = base_path + pdf_file.file_url
	return file_url

def delete_file(doc, filename):
    filename, extn = os.path.splitext(filename)

    for file in frappe.get_all(
        "File",
        filters=[
            ["attached_to_doctype", "=", doc.doctype],
            ["attached_to_name", "=", doc.name],
            ["file_name", "like", f"{filename}%"],
            ["file_name", "like", f"%{extn}"],
        ],
        pluck="name",
    ):
        frappe.delete_doc("File", file, force=True, ignore_permissions=True)

def get_pdf_link(doctype, docname, print_format="Standard", no_letterhead=0):
	return "/api/method/frappe.utils.print_format.download_pdf?doctype={doctype}&name={docname}&format={print_format}&no_letterhead={no_letterhead}".format(
		doctype=doctype, docname=docname, print_format=print_format, no_letterhead=no_letterhead)
 