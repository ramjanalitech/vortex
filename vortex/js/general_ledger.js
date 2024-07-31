// Copyright (c) 2018, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.query_reports["General Ledger"] = {
    onload: function(report) {
        report.page.add_inner_button(__('Whatsapp Send'), function() {
            //Code to execute when button is clicked
            let filters = report.get_values();
            console.log(filters)
            frappe.call({
                method: "vortex.custom.general_ledger.whatsapp_get_doc",
                args: {
                    doc: filters
                },
                callback: function(r) {
                    if(r.message) {
                        console.log(url);
                    }
                }
            });
            
        });
    },
}
