frappe.query_reports['whatsapp report'] = {
    onload: function(report) {
		frappe.query_report.page.add_inner_button(__("Get Selected"), function() {
			return frappe.call({
				method: "erpnext.api.test_button",
				callback: function(r) {
				frappe.msgprint("Approved sucessfully");
				}

				});
		});
	}
};