# ..............imports to EFRIS.................
import frappe
from frappe import _
from frappe.utils import now_datetime
from six import string_types
import json
import requests
from ura_efris.api.utils import (
    get_ura_efris_settings,
    create_global_info,
    b64encode,
    create_data,
)


@frappe.whitelist()
def send_request_to_api(docname, modified):
    doc = frappe.get_doc("Sales Invoice", docname)
    credit_note_query(doc, "on_submit")

import base64
@frappe.whitelist()
def credit_note_query(doc, method):
    if doc.is_return:
        tin, deviceNo, url = get_ura_efris_settings(doc)
        dataitem = {
            # "oriInvoiceId": doc.original_invoiceid,
            "oriInvoiceNo": doc.original_invoiceno,
            "buyerTin": doc.tax_id,
            "buyerLegalName": doc.customer,
            "invoiceType": "1",
            # "buyerNinBrn": "201905081705",
            "invoiceKind": "1",
            "pageNo": "1",
            "pageSize": "10",
            }
        payload = {}
        payload.update(dataitem)
        # Encode as base64
        temp = json.dumps(payload)
        base64_message = b64encode(temp)
        data = {
            "returnStateInfo": {"returnCode": "", "returnMessage": ""},
        }
        data["data"] = create_data(base64_message)
        data["globalInfo"] = create_global_info("T107", deviceNo, tin)
        response = requests.post(url, json=data)
        
        response_json = response.json()
        test1 = response_json["data"]
        country = test1["content"]
        py_string = country
        byte_msg = py_string.encode("ascii")
        base64_val = base64.b64decode(byte_msg)
        main_content_return = base64_val.decode("ascii")
           
        doc.db_set("custom_return_main_content", main_content_return)
        frappe.msgprint(
                _("Thank you! A return has been requested for this invoice to EFRIS." + str(main_content_return))
        )
