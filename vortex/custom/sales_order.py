import frappe 
import requests
import json
from frappe.utils import get_url
from frappe.utils import get_url_to_form, now_datetime, get_fullname, get_bench_path, get_site_path, get_request_site_address
from frappe.utils.pdf import get_pdf
from frappe.utils.file_manager import save_file
import base64
import os

@frappe.whitelist()
def sales_order(doc,method=None):
	document=frappe.get_doc("Whatsapp Setting")
	payment_entry_name = doc.name
	url=document.url
	api_key = document.api_key
	whatsapp_camapaign = frappe.get_doc('Whatsapp Setting')
	for camp_name in whatsapp_camapaign.whatsapp_campaign:
		if camp_name.campaign_doctype == "Sales Order":
			payment_campaign = camp_name.campaign_name
	campaign_name = payment_campaign
	phone_no = doc.contact_mobile
	destination = phone_no
	template_params = str(doc.total)
	headers = {"Content-Type": "application/json"}
	data = {
				"apiKey": api_key,
				"campaignName": campaign_name,
				"destination": destination,
				"userName": doc.customer,
				"source": "Sales Order",
				"media": {
				"url": "",
				"filename": doc.customer
				},
				"templateParams": [
					template_params
				],
				"tags": [
				"string"
				]
				}
	req = requests.post(url, data=json.dumps(data), headers=headers)	
	if req.status_code == 200:
		new_doc = frappe.new_doc("Whatsapp Log")
		new_doc.doctype_name = "Payment Entry"
		new_doc.url = ""
		new_doc.response = req
		new_doc.document_name = payment_entry_name
		new_doc.status = "Sent"
		new_doc.save()
		frappe.msgprint("Whatsapp SMS Sent ")
	else:
		new_doc = frappe.new_doc("Whatsapp Log")
		new_doc.doctype_name = "Payment Entry"
		new_doc.response = req
		new_doc.document_name = payment_entry_name
		new_doc.status = "Not Sent"
		new_doc.save()
		frappe.msgprint("Whatsapp SMS Not Sent ")
