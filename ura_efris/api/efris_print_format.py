# ..............imports to EFRIS.................
from frappe.model.document import Document
import frappe
from frappe import _, throw, msgprint
from frappe.utils import nowdate

import six
from six import string_types
import json
import base64

import requests

# # ..............imports to EFRIS.................
@frappe.whitelist()
def send_request_to_post_sales(docname, main_content):
    doc = frappe.get_doc("Sales Invoice", docname)
    doc.main_content = main_content
    message_dict = json.loads(doc.main_content)
    tax_rate = (
        message_dict.get("doc.main_content", {})
        .get("basicInformation", {})
        .get("antifakeCode")
    )
    return message_dict


@frappe.whitelist()
def print_efris_sales(docname, main_content):
    doc = frappe.get_doc("Sales Invoice", docname)
    # doc.main_content = main_content
    # message_dict = json.loads(doc.main_content)
    # tax_rate = message_dict.get('doc.main_content', {}).get('basicInformation', {}).get('antifakeCode')
    # return message_dict
    frappe.msgprint(_("Thanks your Data has  been sent to Efris"))
