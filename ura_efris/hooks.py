# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version
import json
import requests
import frappe
from ura_efris.api.items_stock import send_request_to_api
from ura_efris.api.items_efris import send_request_to_api_item

app_name = "ura_efris"
app_title = "Ura Efris"
app_publisher = "mututa paul"
app_description = "intergration with ura"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "mututapaul01@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/ura_efris/css/ura_efris.css"
# app_include_js = "/assets/ura_efris/js/ura_efris.js"


# include js, css files in header of web template
# web_include_css = "/assets/ura_efris/css/ura_efris.css"
# web_include_js = "/assets/ura_efris/js/ura_efris.js"

# include js in page
# page_js = {"page" : "public/js/file.js"}/home/frappe/frappe-bench/apps/ura_efris/public

# include js in doctype views"Sales Invoice": "public/js/custom_button.js",
doctype_js = {
    "Sales Invoice": "/public/js/custom_button.js",
    "Purchase Receipt": "/public/js/custom_button.js",
    "Stock Entry": "/public/js/custom_button_stock.js",
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Website user home page (by function)
# get_website_user_home_page = "ura_efris.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "ura_efris.install.before_install"
# after_install = "ura_efris.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "ura_efris.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# TODO Enqueue these requests if possible
doc_events = {
    "Purchase Invoice": {
        "on_submit": "ura_efris.api.items_stock.send_request_to_api",
        # "on_submit": "ura_efris.api.efrist_stock_ledger.on_submit"
    },
    "Purchase Receipt": {
        "on_submit": "ura_efris.api.purchase_receipt.send_request_to_api_hook",
        # "on_submit": "ura_efris.api.efrist_stock_ledger.on_submit"
    },
    "Item": {
        "before_save": [
            "ura_efris.api.items_efris.before_save",
            "ura_efris.api.items_efris.send_request_to_api_item",
        ]
    },
    "Sales Invoice": {
        "before_insert": [
            "ura_efris.api.credit_note_application.before_insert",
            ],
        "on_submit": [
            "ura_efris.api.sales_efris.send_request_to_post_sales",
        ],
    },
    "Customer": {
        "on_update": "ura_efris.api.ura_verification_custom.ura_verification_custom",
    },
}

# Scheduled Tasks
# ---------------

scheduler_events = {
    "cron": {
        "*/5 * * * *": [
            "ura_efris.api.sales_efris.send_to_api_bulk",
        ]
    },
    # 	"all": [
    # 		"ura_efris.tasks.all"
    # 	],
    # 	"daily": [
    # 		"ura_efris.tasks.daily"
    # 	],
    # "hourly": ["ura_efris.api.sales_efris.send_to_api_bulk"],
    # 	"weekly": [
    # 		"ura_efris.tasks.weekly"
    # 	]
    # 	"monthly": [
    # 		"ura_efris.tasks.monthly"
    # 	]
}

# Testing
# -------

# before_tests = "ura_efris.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "ura_efris.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
fixtures = ["Client Script"]
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "ura_efris.task.get_dashboard_data"
# }
