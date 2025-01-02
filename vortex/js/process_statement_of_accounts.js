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
    // Mobile number 
    customer_collection: function (frm) {
        frm.set_value("collection_name", "");
        if (frm.doc.customer_collection) {
            frm.get_field("collection_name").set_label(frm.doc.customer_collection);
        }
    },
    
    fetch_customer_for_whatsapp_send: function (frm) {
        if (frm.doc.collection_name) {
            frappe.call({
                method: "vortex.custom.process_statement_of_accounts.fetch_customers_whatsapp",
                args: {
                    customer_collection: frm.doc.customer_collection,
                    collection_name: frm.doc.collection_name,
                    primary_mandatory: frm.doc.primary_mandatory,
                },
                callback: function (r) {
                    if (!r.exc) {
                        if (r.message.length) {
                            frm.clear_table("customers");
                            for (const customer of r.message) {
                                var row = frm.add_child("customers");
                                row.customer = customer.name;
                                row.mobile_no = customer.primary_mobile;  // Replaced email with mobile
                            }
                            frm.refresh_field("customers");
                        } else {
                            frappe.throw(__("No Customers found with selected options."));
                        }
                    }
                },
            });
        } else {
            frappe.throw("Enter " + frm.doc.customer_collection + " name.");
        }
    },  
});
