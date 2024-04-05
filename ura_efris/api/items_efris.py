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


def before_save(doc, method):
    if doc.is_efris:
        item_code = doc.name
        price_list = "Standard Selling"
        item_price = frappe.get_value(
            "Item Price",
            filters={
                "item_code": item_code,
                "price_list": price_list,
                "selling": 1,
                "uom": doc.stock_uom,
            },
            fieldname="price_list_rate",
        )
        if item_price:
            doc.item_price = item_price
        else:
            frappe.msgprint(
                _(
                    f"Please set the price for the item {doc.item_code} and uom {doc.stock_uom} in the price list {price_list}"
                )
            )
        if doc.taxes:
            first_item_tax_template = doc.taxes[0].item_tax_template
            taxcategorycode = frappe.get_value(
                "Item Tax Template",
                first_item_tax_template,
                "efris_tax_category_code",
            )
            doc.efris_value_, doc.value = frappe.get_value(
                "taxCategoryCode", taxcategorycode, ["value", "taxcategorycode"]
            )
        else:
            frappe.throw(f"Please set the tax for the item {doc.item_code}")


@frappe.whitelist()
def send_request_to_api_item(doc, method):
    if doc.is_efris:
        tin, deviceNo, url = get_ura_efris_settings(doc)
        dataitem = {
            "operationType": doc.operationtype,
            "goodsName": doc.item_name,
            "goodsCode": doc.item_code,
            "measureUnit": doc.measureunit,
            "unitPrice": doc.item_price,
            "currency": "101",
            "commodityCategoryId": doc.goodscategoryid,
            "haveExciseTax": "102",
            "description": "1",
            "stockPrewarning": "10",
            "pieceMeasureUnit": "",
            "havePieceUnit": "102",
            "pieceUnitPrice": "",
            "packageScaledValue": "",
            "pieceScaledValue": "",
            "exciseDutyCode": "",
            "haveOtherUnit": "102",
            "goodsTypeCode": "101",
        }
        temp = json.dumps([dataitem])
        base64_message = b64encode(temp)
        data = {
            "returnStateInfo": {"returnCode": "", "returnMessage": ""},
        }
        data["data"] = create_data(base64_message)
        data["globalInfo"] = create_global_info("T130", deviceNo, tin)
        response = requests.post(url, json=data)
        returnCode, returnMessage = get_return_code_and_message(response)
        doc.efris_return_code = returnCode
        if returnCode == "00":
            frappe.msgprint(
                _(f"Thanks. Your Item {doc.item_code} has been Created in EFRIS"),
                alert=True,
            )
        elif returnCode == "45":
            frappe.msgprint(
                _(
                    f"<br>Some information for EFRIS is missing. Check item {doc.name} and update the item for Efris registration"
                )
            )
        else:
            frappe.msgprint(
                _(str({"returnCode": returnCode, "returnMessage": returnMessage}))
            )
        return str(response.json())
    elif doc.efris_return_code == "00":
        frappe.msgprint(_("This Document has already been sent to EFRIS"), alert=True)
