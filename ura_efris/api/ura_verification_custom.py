# ..............imports to EFRIS.................
import frappe
from frappe import _
from ura_efris.api.utils import (
    get_ura_efris_settings,
    create_global_info,
    b64encode,
    get_main_content_from_reponse,
    create_data,
)
import json
import requests


@frappe.whitelist()
def ura_verification_custom(doc, method):
    if doc.tax_id:
        tin, deviceNo, url = get_ura_efris_settings(doc)
        dataitem = {"tin": doc.tax_id, "ninBrn": doc.tax_id_non_business}
        temp = json.dumps(dataitem)
        base64_message = b64encode(temp)
        data = {
            "returnStateInfo": {"returnCode": "", "returnMessage": ""},
        }
        data["data"] = create_data(base64_message)
        data["globalInfo"] = create_global_info("T119", deviceNo, tin)
        response = requests.post(url, json=data)
        main_content = get_main_content_from_reponse(response)
        data = json.loads(main_content)
        tax_payer = data["taxpayer"]
        record = tax_payer["legalName"]
        doc.customer_name = record
        frappe.msgprint("Customer name updated successfully")
