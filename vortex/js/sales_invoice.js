frappe.ui.form.on('Sales Invoice', {
    refresh(frm) {
            frm.add_custom_button(__('Send WhatsApp'), function () {
                frappe.call({
                    method: "vortex.custom.sales_invoice.send_whatsapp_button",
                    args: {
                        docname: frm.doc.name,
                        doctype: frm.doc.doctype
                    }
                });
            });
        
    }
});

