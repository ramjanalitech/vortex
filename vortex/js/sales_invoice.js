// custom_script_sales_invoice.js

frappe.ui.form.on('Sales Invoice', {
    refresh: function(frm) {
        frm.add_custom_button(__('Whatsapp SMS'), function() {
            frappe.call({
                    method: "vortex.custom.sales_invoice.whatsapp_get_doc",
                    args: {
                        doc: frm.doc,
                    },
                    callback: function(r) {
                        if(r.message) {
                            
                        }
                    }
                });
        });
    }
});
