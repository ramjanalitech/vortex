from . import __version__ as app_version

app_name = "vortex"
app_title = "Vortex"
app_publisher = "8848digital"
app_description = "Whatsapp message"
app_email = "prateek@8848digital.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/vortex/css/vortex.css"
# app_include_js = "/assets/vortex/js/vortex.js"

doctype_js = {
    "Sales Invoice": "js/sales_invoice.js"
}

doc_events = {
    "Payment Entry": {
    "on_submit": "vortex.custom.payment_entry.payment_receipt"
    },
    "Payment Request": {
    "on_submit": "vortex.custom.payment_request.payment_request"
    },
     "Delivery Note": {
    "on_submit": "vortex.custom.delivery_note.delivery_note"
    },
     "Sales Order": {
    "on_submit": "vortex.custom.sales_order.sales_order"
    }
    }

# include js, css files in header of web template
# web_include_css = "/assets/vortex/css/vortex.css"
# web_include_js = "/assets/vortex/js/vortex.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "vortex/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "vortex.utils.jinja_methods",
#	"filters": "vortex.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "vortex.install.before_install"
# after_install = "vortex.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "vortex.uninstall.before_uninstall"
# after_uninstall = "vortex.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "vortex.utils.before_app_install"
# after_app_install = "vortex.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "vortex.utils.before_app_uninstall"
# after_app_uninstall = "vortex.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "vortex.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

override_doctype_class = {
	"SMS Center": "vortex.overrides.sms_settings.custom_SMSCenter",
    "Notification": "vortex.overrides.sms_settings.CustomNotification"
}

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
#	"*": {
#		"on_update": "method",
#		"on_cancel": "method",
#		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"vortex.tasks.all"
#	],
#	"daily": [
#		"vortex.tasks.daily"
#	],
#	"hourly": [
#		"vortex.tasks.hourly"
#	],
#	"weekly": [
#		"vortex.tasks.weekly"
#	],
#	"monthly": [
#		"vortex.tasks.monthly"
#	],
# }

# Testing
# -------

# before_tests = "vortex.install.before_tests"

# Overriding Methods
# ------------------------------
#
override_whitelisted_methods = {
	"erpnext.accounts.doctype.payment_entry.payment_entry.get_payment_entry": "vortex.overrides.payment_entry.get_payment_entry"
}
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "vortex.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["vortex.utils.before_request"]
# after_request = ["vortex.utils.after_request"]

# Job Events
# ----------
# before_job = ["vortex.utils.before_job"]
# after_job = ["vortex.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"vortex.auth.validate"
# ]
