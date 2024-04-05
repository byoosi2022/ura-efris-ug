# ..............imports to EFRIS.................
import frappe
from frappe import _, throw, msgprint
from ura_efris.api.utils import (
    get_ura_efris_settings,
    create_global_info,
    b64encode,
    get_return_code_and_message,
    create_data,
)
import json
import requests


def send_request_to_api_hook(doc, method):
    send_request_to_api(doc.name, doc.modified)


@frappe.whitelist()
def send_request_to_api(docname, modified):
    doc = frappe.get_doc("Purchase Receipt", docname)
    doc.modified = modified
    if doc.is_return:
        send_purchase_return(doc)
        return

    if doc.is_efris and doc.efris_return_code != "00" and doc.docstatus == 1:
        tin, deviceNo, url = get_ura_efris_settings(doc)
        dataitem = {
            "item_code": doc.name,
            "goodsStockIn": {
                "operationType": "101",
                "supplierTin": doc.tax_id or "",
                "supplierName": doc.supplier_name,
                "adjustType": "",
                "remarks": "",
                "stockInDate": "",
                "stockInType": "104" if doc.supplier_name == "Opening Stock" else "102",
                "productionBatchNo": "",
                "productionDate": "",
                "branchId": "",
                "invoiceNo": "",
                "isCheckBatchNo": "",
                "rollBackIfError": "",
                "goodsTypeCode": "101",
            },
            "goodsStockInItem": [],
        }
        for activity in doc.items:
            item = frappe.get_doc("Item", activity.item_code)
            if item.efris_return_code != "00":
                item.is_efris = 1
                item.operationtype = "101"
                item.save()
            dataitem["goodsStockInItem"].append(
                {
                    "commodityGoodsId": "",
                    "goodsCode": activity.item_code,
                    "measureUnit": activity.measureunit,
                    "quantity": activity.stock_qty,
                    "unitPrice": activity.stock_uom_rate,
                    "remarks": "remarks",
                    "fuelTankId": "",
                    "lossQuantity": "",
                    "originalQuantity": "",
                },
            )

        temp = json.dumps(dataitem)
        base64_message = b64encode(temp)
        data = {
            "returnStateInfo": {"returnCode": "", "returnMessage": ""},
        }
        data["data"] = create_data(base64_message)
        data["globalInfo"] = create_global_info("T131", deviceNo, tin)
        response = requests.post(url, json=data)
        response_json = response.json()
        returnStateInfo = response_json["returnStateInfo"]
        returnMessage = returnStateInfo["returnMessage"]
        returnCode = returnStateInfo["returnCode"]
        int_returnCode = int(returnCode)
        if int_returnCode == 00:
            frappe.msgprint(
                _(f"Thanks. Your {doc.doctype} has been Created in EFRIS"), alert=True
            )
            doc.efris_return_code = returnCode
            doc.save()
            frappe.db.commit()
        elif int_returnCode == 45:
            frappe.msgprint(
                _(
                    str(returnMessage)
                    + f"<br>Check and See to make sure all fields for {doc.doctype} {doc.name} are correctly set for EFRIS"
                )
            )
            frappe.msgprint(_(f"<br>Sending to EFRIS<br> {temp}"))
        else:
            frappe.msgprint(_(str(returnStateInfo)))
        return str(response_json)
    elif doc.docstatus != 1:
        frappe.msgprint(_("Please Submit the document first"))
    elif doc.efris_return_code == "00":
        frappe.msgprint(_("This Document has already been sent to EFRIS"), alert=True)


def send_purchase_return(doc):
    if doc.is_efris and doc.efris_return_code != "00" and doc.docstatus == 1:
        tin, deviceNo, url = get_ura_efris_settings(doc)
        dataitem = {
            "item_code": doc.name,
            "goodsStockIn": {
                "operationType": "102",
                "supplierTin": "",
                "supplierName": "",
                "adjustType": "104",
                "remarks": "Purchase Return",
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
            "goodsStockInItem": [],
        }

        for activity in doc.items:
            dataitem["goodsStockInItem"].append(
                {
                    "commodityGoodsId": "",
                    "goodsCode": activity.item_code,
                    "measureUnit": activity.measureunit,
                    "quantity": activity.stock_qty * -1,
                    "unitPrice": activity.stock_uom_rate,
                    "remarks": "Purchase Return",
                    "fuelTankId": "",
                    "lossQuantity": "",
                    "originalQuantity": "",
                }
            )
        temp = json.dumps(dataitem)
        base64_message = b64encode(temp)
        data = {
            "data": {
                "content": base64_message,
                "signature": "",
                "dataDescription": {
                    "codeType": "0",
                    "encryptCode": "1",
                    "zipCode": "0",
                },
            },
            "returnStateInfo": {"returnCode": "", "returnMessage": ""},
        }
        data["globalInfo"] = create_global_info("T131", deviceNo, tin)
        response = requests.post(url, json=data)
        returnCode, returnMessage = get_return_code_and_message(response)
        int_returnCode = int(returnCode)
        if int_returnCode == 00:
            frappe.msgprint(
                _(f"Thanks. Your {doc.doctype} has been Created in EFRIS"), alert=True
            )
            doc.efris_return_code = returnCode
            doc.save()
            frappe.db.commit()
        elif int_returnCode == 45:
            frappe.msgprint(
                _(
                    str(returnMessage)
                    + f"<br>Check and See to make sure all fields for {doc.doctype} {doc.name} are correctly set for EFRIS"
                )
            )
            frappe.msgprint(_(f"<br>Sending to EFRIS<br> {temp}"))

    elif doc.docstatus != 1:
        frappe.msgprint(_("Please Submit the document first"))
    elif doc.efris_return_code == "00":
        frappe.msgprint(_("This Document has already been sent to EFRIS"), alert=True)
