// Copyright (c) 2020, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on('Process Statement Of Accounts', {
    refresh: function(frm) {
        // Check if the form is not a new document
        if (!frm.doc.__islocal) {
            // Add custom button for sending WhatsApp messages
            frm.add_custom_button(__('WhatsApp Send'), function() {
                // Make server-side call to send WhatsApp message
                frappe.call({
                    method: "vortex.custom.process_statement_of_accounts.whatsapp",
                    args: {
                        "document_name": frm.doc.name,
                    },
                    callback: function(r) {
                        // Handle the response from the server
                        if (r && r.message) {
                            // Show success alert if messages are queued
                            frappe.show_alert({ message: __('Emails Queued'), indicator: 'blue' });
                        } else {
                            // Show message if no records are found
                            frappe.msgprint(__('No Records for these settings.'));
                        }
                    }
                });
            });
        }
    },
});
