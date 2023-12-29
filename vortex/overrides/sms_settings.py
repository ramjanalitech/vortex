import frappe
from frappe.core.doctype.sms_settings.sms_settings import SMSSettings,validate_receiver_nos,get_headers,send_request,create_sms_log
from frappe import _, msgprint, throw
from frappe.model.document import Document
from frappe.utils import nowdate,cstr
from erpnext.selling.doctype.sms_center.sms_center import SMSCenter
from frappe.email.doctype.notification.notification import Notification


@frappe.whitelist()
def send_custom_sms(receiver_list, msg, sender_name="", success_msg=True):
	import json

	if isinstance(receiver_list, str):
		receiver_list = json.loads(receiver_list)
		if not isinstance(receiver_list, list):
			receiver_list = [receiver_list]

	receiver_list = validate_receiver_nos(receiver_list)

	arg = {
		"receiver_list": receiver_list,
		"message": frappe.safe_decode(msg).encode("utf-8"),
		"success_msg": success_msg,
	}

	if frappe.db.get_single_value("SMS Settings", "sms_gateway_url"):
		send_via_gateway(arg)
	else:
		msgprint(_("Please Update SMS Settings"))


def send_via_gateway(arg):
	ss = frappe.get_doc("SMS Settings", "SMS Settings")
	headers = get_headers(ss)
	use_json = headers.get("Content-Type") == "application/json"
	message = frappe.safe_decode(arg.get("message"))
	args = {ss.message_parameter: message}
	for d in ss.get("parameters"):
		if not d.header:
			args[d.parameter] = d.value

	success_list = []

	for d in arg.get("receiver_list"):
		args[ss.receiver_parameter] = d
		params = {}
		list_parms=[]
		dict_args = {}
		params.update({"sender":args['sender']})
		dict_args.update({"number":args['number'],"text":args['message'],"dlttempid":args['dlttempid']})
		list_parms.append(dict_args)
		params.update({"message":list_parms})
		params.update({"messagetype": args['messagetype']})
		args=params
		status = send_request(ss.sms_gateway_url, args, headers, ss.use_post, use_json)


		if 200 <= status < 300:
			success_list.append(d)

	if len(success_list) > 0:
		args.update(arg)
		create_sms_log(args, success_list)
		if arg.get("success_msg"):
			frappe.msgprint(_("SMS sent to following numbers: {0}").format("\n" + "\n".join(success_list)))

class custom_SMSCenter(SMSCenter):
	@frappe.whitelist()
	def send_sms(self):
		receiver_list = []
		if not self.message:
			msgprint(_("Please enter message before sending"))
		else:
			receiver_list = self.get_receiver_nos()
		if receiver_list:
			send_custom_sms(receiver_list, cstr(self.message))

class CustomNotification(Notification):
	def send_sms(self, doc, context):
		send_custom_sms(
			receiver_list=self.get_receiver_list(doc, context),
			msg=frappe.render_template(self.message, context),
		)


