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
	pdf_link = get_payment_entry_pdf_link(payment_entry_name)
	fileurl = pdfurl_generate(pdf_link,"Payment Entry",payment_entry_name)
	headers = {"Content-Type": "application/json"}
	data = {
				"apiKey": api_key,
				"campaignName": campaign_name,
				"destination": destination,
				"userName": doc.company,
				"source": "Payment Entry",
				"media": {
				"url": fileurl,
				"filename": doc.company
				},
				"templateParams": [
				],
				"tags": [
				"string"
				]
				}
	req = requests.post(url, data=json.dumps(data), headers=headers)	
	if req.status_code == 200:
		new_doc = frappe.new_doc("Whatsapp Log")
		new_doc.doctype_name = "Payment Entry"
		new_doc.url = str(fileurl)
		new_doc.response = req
		new_doc.document_name = payment_entry_name
		new_doc.status = "Sent"
		new_doc.save()
		frappe.msgprint("Whatsapp SMS Sent ")
	else:
		new_doc = frappe.new_doc("Whatsapp Log")
		new_doc.doctype_name = "Payment Entry"
		new_doc.url = str(fileurl)
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

def pdfurl_generate(pdf_link,doctype,docname): 
	base_path = frappe.db.get_single_value('Whatsapp Setting','base_path')
	bench_path = get_bench_path()
	site_path = get_site_path().replace(".", "/sites",1)
	base_path_ = bench_path + site_path
	file_name = frappe.generate_hash("",5) + ".pdf"
	cert_file_name = "cert_" + file_name
	headers = {'Content-Type': 'application/json'}
	cert_url = pdf_link
	certificate_response = requests.get(cert_url,headers=headers)
	cert_file_path = "/public/files/" + cert_file_name
	cert_file = open(base_path_ + cert_file_path, "wb")
	cert_file.write(certificate_response.content)
	cert_file.close()
	pdf_file = save_file(fname=cert_file_name, content=base64.b64encode(certificate_response.content),dt=doctype, dn=docname, decode=True, is_private=0)

	file_url = base_path + pdf_file.file_url 	
	return file_url

def get_pdf_link(doctype, docname, print_format="Standard", no_letterhead=0):
	return "/api/method/frappe.utils.print_format.download_pdf?doctype={doctype}&name={docname}&format={print_format}&no_letterhead={no_letterhead}".format(
		doctype=doctype, docname=docname, print_format=print_format, no_letterhead=no_letterhead)
 