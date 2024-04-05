# ..............imports to EFRIS.................
import frappe
from frappe import _
from ura_efris.api.utils import (
    get_ura_efris_settings,
    create_global_info,
    b64encode,
    get_return_code_and_message,
    create_data,
)
import json
import requests


@frappe.whitelist()
def send_request_to_api(docname, modified):
    doc = frappe.get_doc("Stock Entry", docname)
    stock_entry(doc, "from_front_end")


@frappe.whitelist()
def stock_entry(doc, method):
    if (
        doc.adjusttype_to_efris
        and doc.stock_entry_type == "Material Transfer"
        and doc.efris_return_code != "00"
        and doc.docstatus == 1
    ):
        tin, deviceNo, url = get_ura_efris_settings(doc)
        goodsStockInItem = []
        for activity in doc.items:
            measureunit = frappe.get_value("UOM", activity.stock_uom, "measureunit")
            goodsStockInItem.append(
                {
                    "commodityGoodsId": "",
                    "goodsCode": activity.item_code,
                    "measureUnit": measureunit,
                    "quantity": activity.qty * activity.conversion_factor,
                    "unitPrice": activity.basic_rate,
                    "remarks": "remarks",
                    "fuelTankId": "",
                    "lossQuantity": "",
                    "originalQuantity": "",
                }
            )
        dataitem = {
            "item_code": doc.name,
            "goodsStockIn": {
                "operationType": doc.operationtype,
                "supplierTin": "",
                "supplierName": "",
                "adjustType": doc.code,
                "remarks": "",
                "stockInDate": "",
                "stockInType": "",
                "productionBatchNo": "",
                "productionDate": "",
                "branchId": "",
                "invoiceNo": "",
                "isCheckBatchNo": "",
                "rollBackIfError": "",
                "goodsTypeCode": "101",
            },
            "goodsStockInItem": goodsStockInItem,
        }
        temp = json.dumps(dataitem)
        base64_message = b64encode(temp)
        data = {
            "returnStateInfo": {"returnCode": "", "returnMessage": ""},
        }
        data["data"] = create_data(base64_message)
        data["globalInfo"] = create_global_info("T131", deviceNo, tin)
        response = requests.post(url, json=data)
        returnCode, returnMessage = get_return_code_and_message(response)
        if returnCode == "00":
            frappe.msgprint(_(f"Thank you, Stock Transfer has been sent to EFRIS"))
            doc.efris_return_code = returnCode
            if method != "on_submit":
                doc.save()
                frappe.db.commit()
        else:
            frappe.msgprint(
                _(
                    f"Error: {returnMessage} with error number: {returnCode} <BR><BR>{dataitem}"
                )
            )
        # sales_efris_response = frappe.new_doc("Goods Stock Maintain")
    elif doc.efris_return_code == "00":
        frappe.msgprint(
            _(f"DUPLICATE SUBMISSION!<BR><BR>Stock Transfer was already sent to EFRIS")
        )
