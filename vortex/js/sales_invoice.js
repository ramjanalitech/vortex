// frappe.ui.form.on('Sales Invoice', {
//     refresh(frm) {
//             frm.add_custom_button(__('Send WhatsApp'), function () {
//                 frappe.call({
//                     method: "vortex.custom.sales_invoice.generate_pdf_and_send_whatsapp_on_submit",
//                     args: {
//                         docname: frm.doc.name,
//                         doctype: frm.doc.doctype
//                     }
//                 });
//             });
        
//     }
// });

frappe.ui.form.on('Sales Invoice', {
    refresh(frm) {
        if (!frm.is_new() && frm.doc.docstatus === 1) {
            frm.add_custom_button(__('Send WhatsApp'), function () {
                frappe.call({
                    method: "vortex.custom.sales_invoice.send_whatsapp_button",
                    args: {
                        docname: frm.doc.name,
                        doctype: frm.doc.doctype
                    },
                    freeze: true,
                    freeze_message: __('Sending WhatsApp...')
                });
            });
        }
    }
});

