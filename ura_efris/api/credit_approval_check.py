# ..............imports to EFRIS.................
import frappe
from frappe import _
from frappe.utils import now_datetime
from ura_efris.api.utils import (
    get_ura_efris_settings,
    create_global_info,
    b64encode,
    get_main_content_from_reponse,
    create_data,
)
import json
import requests


# # ..............imports to EFRIS.................
@frappe.whitelist()
def credit_note_approval(docname, efris_return_id, modified):
    doc = frappe.get_doc("Sales Invoice", docname)
    tin, deviceNo, url = get_ura_efris_settings(doc)
    doc.efris_return_id = efris_return_id
    doc.modified = now_datetime().strftime("%Y-%m-%d %H:%M:%S")
    application_details = {"id": doc.efris_return_id, "queryType": "1"}
    temp = json.dumps(application_details)
    base64_message = b64encode(temp)
    data_two = {
        "returnStateInfo": {"returnCode": "", "returnMessage": ""},
    }
    data_two["data"] = create_data(base64_message)
    data_two["globalInfo"] = create_global_info("T112", deviceNo, tin)
    response = requests.post(url, json=data_two)
    main_content = get_main_content_from_reponse(response)
    data = json.loads(main_content)
    refund_invoice_no = data["refundInvoiceNo"]

    application_details = {"invoiceNo": refund_invoice_no}
    temp = json.dumps(application_details)
    base64_messages = b64encode(temp)
    data_two = {
        "data": {
            "content": base64_messages,
            "signature": "",
            "dataDescription": {"codeType": "0", "encryptCode": "1", "zipCode": "0"},
        },
        "returnStateInfo": {"returnCode": "", "returnMessage": ""},
    }
    data_two["global_info"] = create_global_info("T108", deviceNo, tin)
    response = requests.post(url, json=data_two)
    main_content = get_main_content_from_reponse(response)
    data2 = json.loads(main_content)
    return data2
    # frappe.msgprint(_("Thank you! A return has been requested for this invoice to Efris." + str(data2)))
