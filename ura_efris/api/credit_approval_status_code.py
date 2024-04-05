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


# # ..............imports to EFRIS.................
@frappe.whitelist()
def credit_note_approval(docname, efris_return_id, modified):
    doc = frappe.get_doc("Sales Invoice", docname)

    tin, deviceNo, url = get_ura_efris_settings(doc)
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
    approve_status_code = data["approveStatusCode"]

    return approve_status_code
