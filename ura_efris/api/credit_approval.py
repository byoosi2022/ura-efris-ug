# ..............imports to EFRIS.................
import frappe
from frappe import _
import json
import requests
from ura_efris.api.utils import (
    get_ura_efris_settings,
    create_global_info,
    b64encode,
    get_main_content_from_reponse,
    create_data,
)


@frappe.whitelist()
def credit_note_approval(docname, oriinvoiceid, original_invoiceno, modified):
    doc = frappe.get_doc("Sales Invoice", docname)
    tin, deviceNo, url = get_ura_efris_settings(doc)
    doc.oriinvoiceid = oriinvoiceid
    doc.original_invoiceno = original_invoiceno

    dataitem = {
        "referenceNo": doc.efris_return_id,
        "queryType": "1",
        "pageNo": "1",
        "pageSize": "10",
    }
    temp = json.dumps(dataitem)
    base64_message = b64encode(temp)
    data = {
        "returnStateInfo": {"returnCode": "", "returnMessage": ""},
    }
    data["data"] = create_data(base64_message)
    data["globalInfo"] = create_global_info("T111", deviceNo, tin)

    response = requests.post(url, json=data)
    main_content = get_main_content_from_reponse(response)
    data = json.loads(main_content)

    # Access the 'id' and 'approveStatus' values from the first record in the 'records' list
    record = data["records"][0] if data["records"] else {"message": {"id": "Failed"}}
    if not data["records"]:
        frappe.msgprint(
            _(
                f"The ID has NOT been returned from Efris. Please try again later.<BR><BR>{data}"
            ),
        )
        doc.efris_return_id = ""
    else:
        frappe.msgprint(
            _(
                f"Thank you! A return has been requested for this invoice to Efris.<BR><BR>"
            ),
        )
        doc.efris_return_id = record["id"]
        doc.save()
        frappe.db.commit()
    return record
