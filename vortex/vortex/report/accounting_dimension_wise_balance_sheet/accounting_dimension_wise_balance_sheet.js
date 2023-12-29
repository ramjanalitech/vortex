// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.provide("erpnext.utils")

frappe.query_reports["Accounting Dimension Wise Balance Sheet"] = {
	
	"filters" :[
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1
		},
		{
			"fieldname":"finance_book",
			"label": __("Finance Book"),
			"fieldtype": "Link",
			"options": "Finance Book"
		},
		{
			"fieldname":"filter_based_on",
			"label": __("Filter Based On"),
			"fieldtype": "Select",
			"options": ["Fiscal Year", "Date Range"],
			"default": ["Fiscal Year"],
			"reqd": 1,
			on_change: function() {
				let filter_based_on = frappe.query_report.get_filter_value('filter_based_on');
				frappe.query_report.toggle_filter_display('from_fiscal_year', filter_based_on === 'Date Range');
				frappe.query_report.toggle_filter_display('to_fiscal_year', filter_based_on === 'Date Range');
				frappe.query_report.toggle_filter_display('period_start_date', filter_based_on === 'Fiscal Year');
				frappe.query_report.toggle_filter_display('period_end_date', filter_based_on === 'Fiscal Year');

				frappe.query_report.refresh();
			}
		},
		{
			"fieldname":"period_start_date",
			"label": __("Start Date"),
			"fieldtype": "Date",
			// "reqd": 1,
			"depends_on": "eval:doc.filter_based_on == 'Date Range'"
		},
		{
			"fieldname":"period_end_date",
			"label": __("End Date"),
			"fieldtype": "Date",
			// "reqd": 1,
			"depends_on": "eval:doc.filter_based_on == 'Date Range'"
		},
		{
			"fieldname":"from_fiscal_year",
			"label": __("Start Year"),
			"fieldtype": "Link",
			"options": "Fiscal Year",
			"default": frappe.defaults.get_user_default("fiscal_year"),
			"reqd": 1,
			"depends_on": "eval:doc.filter_based_on == 'Fiscal Year'"
		},
		{
			"fieldname":"to_fiscal_year",
			"label": __("End Year"),
			"fieldtype": "Link",
			"options": "Fiscal Year",
			"default": frappe.defaults.get_user_default("fiscal_year"),
			"reqd": 1,
			"depends_on": "eval:doc.filter_based_on == 'Fiscal Year'"
		},
		{
			"fieldname": "periodicity",
			"label": __("Periodicity"),
			"fieldtype": "Select",
			"reqd": 1,
			"options": [
				{ "value": "Monthly", "label": __("Monthly") },
				{ "value": "Quarterly", "label": __("Quarterly") },
				{ "value": "Half-Yearly", "label": __("Half-Yearly") },
				{ "value": "Yearly", "label": __("Yearly") }
			]
		},
		// Note:
		// If you are modifying this array such that the presentation_currency object
		// is no longer the last object, please make adjustments in cash_flow.js
		// accordingly.
		{
			"fieldname": "presentation_currency",
			"label": __("Currency"),
			"fieldtype": "Select",
			"options": erpnext.get_presentation_currency_list()
		},
		{
			"fieldname": "cost_center",
			"label": __("Cost Center"),
			"fieldtype": "MultiSelectList",
			get_data: function(txt) {
				return frappe.db.get_link_options('Cost Center', txt, {
					company: frappe.query_report.get_filter_value("company")
				});
			}
		},
		{
			"fieldname": "accumulated_values",
			"label": __("Accumulated Values"),
			"fieldtype": "Check",
			"default": 1
		},
		{
			"fieldname": "include_default_book_entries",
			"label": __("Include Default Book Entries"),
			"fieldtype": "Check",
			"default": 1
		}
	],
	"formatter": function(value, row, column, data, default_formatter) {
		if (data && column.fieldname=="account") {
			value = data.account_name || value;

			column.link_onclick =
			"open_general_ledger(" + JSON.stringify(data) + ")";
			column.is_tree = true;
		}

		value = default_formatter(value, row, column, data);

		if (data && !data.parent_account) {
			value = $(`<span>${value}</span>`);

			var $value = $(value).css("font-weight", "bold");
			if (data.warn_if_negative && data[column.fieldname] < 0) {
				$value.addClass("text-danger");
			}

			value = $value.wrap("<p></p>").parent().html();
		}

		return value;
	},

	"tree": true,
	"name_field": "account",
	"parent_field": "parent_account",
	"initial_depth": 3,
	onload: function(report) {
		// dropdown for links to other financial statements
		// erpnext.financial_statements.filters = get_filters()

		frappe.call({
			method: "vortex.vortex.report.accounting_dimension_wise_balance_sheet.accounting_dimension_wise_balance_sheet._get_accounting_dimensions",
			callback: function(r) {
				var periodicity = frappe.query_report.get_filter('periodicity');
				periodicity.df.options.push(...r.message);
				periodicity.refresh();
			}
		});

		let fiscal_year = frappe.defaults.get_user_default("fiscal_year")

		frappe.model.with_doc("Fiscal Year", fiscal_year, function(r) {
			var fy = frappe.model.get_doc("Fiscal Year", fiscal_year);
			frappe.query_report.set_filter_value({
				period_start_date: fy.year_start_date,
				period_end_date: fy.year_end_date
			});
		});
		
		frappe.query_report.set_filter_value({
			periodicity: "Yearly"
		});

		const views_menu = report.page.add_custom_button_group(__('Financial Statements'));

		report.page.add_custom_menu_item(views_menu, __("Balance Sheet"), function() {
			var filters = report.get_values();
			frappe.set_route('query-report', 'Accounting Dimension Wise Balance Sheet', {company: filters.company});
		});

		report.page.add_custom_menu_item(views_menu, __("Profit and Loss"), function() {
			var filters = report.get_values();
			frappe.set_route('query-report', 'Accounting Dimension Wise Profit and Loss Statement', {company: filters.company});
		});

		report.page.add_custom_menu_item(views_menu, __("Cash Flow Statement"), function() {
			var filters = report.get_values();
			frappe.set_route('query-report', 'Cash Flow', {company: filters.company});
		});
	}
}

function open_general_ledger(data) {
	if (!data.account) return;
	var project = $.grep(frappe.query_report.filters, function(e){ return e.df.fieldname == 'project'; })

	frappe.route_options = {
		"account": data.account,
		"company": frappe.query_report.get_filter_value('company'),
		"from_date": data.from_date || data.year_start_date,
		"to_date": data.to_date || data.year_end_date,
		"project": (project && project.length > 0) ? project[0].$input.val() : ""
	};
	frappe.set_route("query-report", "General Ledger");
}
erpnext.utils.add_dimensions = function(report_name, index) {
	let filters = frappe.query_reports[report_name].filters;
	
	frappe.call({
		method: "erpnext.accounts.doctype.accounting_dimension.accounting_dimension.get_dimensions",
		callback: function(r) {
			let accounting_dimensions = r.message[0];
			accounting_dimensions.forEach((dimension) => {
				let found = filters.some(el => el.fieldname === dimension['fieldname']);
				
				if (!found) {
					filters.splice(index, 0, {
						"fieldname": dimension["fieldname"],
						"label": __(dimension["label"]),
						"fieldtype": "MultiSelectList",
						get_data: function(txt) {
							return frappe.db.get_link_options(dimension["document_type"], txt);
						},
					});
				}
			});
		}
	});
};
erpnext.utils.add_dimensions('Accounting Dimension Wise Balance Sheet', 10);