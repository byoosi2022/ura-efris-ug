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
    get_main_content_from_reponse,
    get_return_code_and_message,
    create_data,
)


@frappe.whitelist()
def send_request_to_api(docname, modified):
    doc = frappe.get_doc("Sales Invoice", docname)
    credit_note_application(doc, "on_submit")


@frappe.whitelist()
def credit_note_application(doc, method):
    if doc.is_return and doc.update_stock and not doc.oriinvoiceid:
        tin, deviceNo, url = get_ura_efris_settings(doc)
        goodsDetails = []
        taxDetails = []
        payWay = []
        orderNumber = 0  # initialize the order number to 0
        total_net_amount = 0
        total_taxes_and_charges = 0
        for activity in doc.items:
            tax_amount = activity.net_amount * float(
                0 if activity.efris_value == "-" else activity.efris_value
            )
            gross_total = activity.net_amount + tax_amount
            total_net_amount += activity.net_amount
            total_taxes_and_charges += round(tax_amount, 2)
            goodsDetails.append(
                {
                    "item": activity.item_name,
                    "itemCode": activity.item_code,
                    "qty": activity.stock_qty,
                    "unitOfMeasure": activity.unitofmeasure,
                    "unitPrice": str(round(activity.stock_uom_rate)),
                    "total": str(round(activity.amount, 2)),
                    "taxRate": activity.efris_value,
                    "tax": str(round(tax_amount, 2)),
                    "orderNumber": str(
                        frappe.get_value(
                            "Sales Invoice Item", activity.sales_invoice_item, "idx"
                        )
                        - 1
                    ),  # add the order number to the dictionary,,
                    "deemedFlag": "2",
                    "exciseFlag": "2",
                    "categoryId": "",
                    "categoryName": "",
                    "goodsCategoryId": activity.goodscategoryid,
                    "goodsCategoryName": "",
                    "exciseRate": "",
                    "exciseRule": "",
                    "exciseTax": "",
                    "pack": "",
                    "stick": "",
                    "exciseUnit": "",
                    "exciseCurrency": "",
                    "exciseRateName": "",
                    "vatApplicableFlag": "1",
                }
            )
            orderNumber += 1  # increment the order number for the next item
            taxDetails.append(
                {
                    "taxCategoryCode": activity.value_code,
                    "netAmount": str(round(activity.net_amount, 2)),
                    "taxRate": activity.efris_value,
                    "taxAmount": str(round(tax_amount, 2)),
                    "grossAmount": str(round(gross_total, 2)),
                    "exciseUnit": "",
                    "exciseCurrency": "",
                    "taxRateName": "",
                }
            )
            grand_total = total_net_amount + total_taxes_and_charges
            payWay.append(
                {
                    "paymentMode": doc.efris_pd_code,
                    "paymentAmount": str(
                        round(grand_total - doc.outstanding_amount, 2)
                    ),
                    "orderNumber": doc.po_no,
                }
            )
        dataitem = {
            "oriInvoiceId": doc.original_invoiceid,
            "oriInvoiceNo": doc.original_invoiceno,
            "reasonCode": "101",
            "applicationTime": now_datetime().strftime("%Y-%m-%d %H:%M:%S"),
            "invoiceApplyCategoryCode": "101",
            "currency": "UGX",
            "contactName": "1",
            "contactMobileNum": "1",
            "contactEmail": doc.buyeremail,
            "source": "101",
            "remarks": doc.remarks,
            "sellersReferenceNo": doc.name,
            "summary": {
                "netAmount": str(round(total_net_amount, 2)),
                "taxAmount": str(round(total_taxes_and_charges, 2)),
                "grossAmount": str(round(grand_total, 2)),
                "itemCount": str(activity.idx),
                "modeCode": "0",
                "qrCode": "",
            },
            "buyerDetails": {
                "buyerTin": doc.tax_id,
                "buyerNinBrn": "201905081705",
                "buyerPassportNum": doc.buyerpassportnum,
                "buyerLegalName": doc.customer,
                "buyerBusinessName": doc.customer,
                "buyerAddress": doc.buyeraddress,
                "buyerEmail": doc.buyeremail,
                "buyerMobilePhone": doc.buyermobilephone,
                "buyerLinePhone": doc.buyerlinephone,
                "buyerPlaceOfBusi": doc.buyerplaceofbusi,
                "buyerType": "1",
                "buyerCitizenship": "1",
                "buyerSector": "1",
                "buyerReferenceNo": doc.name,
            },
            "importServicesSeller": {
                "importBusinessName": "",
                "importEmailAddress": "",
                "importContactNumber": "",
                "importAddress": "",
                "importInvoiceDate": doc.posting_date.strftime("%Y-%m-%d"),
                "importAttachmentName": "",
                "importAttachmentContent": "",
            },
            "basicInformation": {
                "operator": doc.owner,
                "invoiceKind": "1",
                "invoiceIndustryCode": "",
                "branchId": "",
            },
        }
        payload = {}
        payload.update(dataitem)
        payload["goodsDetails"] = goodsDetails
        payload["taxDetails"] = taxDetails
        payload["payWay"] = payWay
        # Encode as base64
        temp = json.dumps(payload)
        base64_message = b64encode(temp)
        data = {
            "returnStateInfo": {"returnCode": "", "returnMessage": ""},
        }
        data["data"] = create_data(base64_message)
        data["globalInfo"] = create_global_info("T110", deviceNo, tin)
        response = requests.post(url, json=data)
        returnCode, returnMessage = get_return_code_and_message(response)
        if returnCode == 00:
            main_content = get_main_content_from_reponse(response)
            data = json.loads(main_content)
            basic_info = data["basicInformation"]
            antifake_code = basic_info["antifakeCode"]
            oriinvoiceid = basic_info["invoiceId"]
            oriinvoiceNo = basic_info["invoiceNo"]
            device_no = basic_info["deviceNo"]
            reference_number = data["referenceNo"]
            doc.oriinvoiceid = reference_number
            # doc.return_content_sales = main_content
            doc.save()
            frappe.msgprint(
                _("Thank you! A return has been requested for this invoice to EFRIS.")
            )
            # Create Sales Return EFRIS Responses for future use
            sales_return_efris_responses = frappe.new_doc(
                "Sales Return Efris Responses"
            )
            sales_return_efris_responses.update(
                {
                    "sales_invoice": doc.name,
                    "custom": doc.customer,
                    "status_code": returnMessage,
                    "original_invoiceid": oriinvoiceid,
                    "original_invoiceno": oriinvoiceNo,
                    "sales_invoice_content": main_content,
                    "efris_referenceno": oriinvoiceid,
                }
            )

            sales_return_efris_responses.insert()
            sales_return_efris_responses.save()
        else:
            frappe.msgprint(
                _(str({"returnCode": returnCode, "returnMessage": returnMessage}))
            )
        frappe.db.commit()


def before_insert(doc, method):
    if doc.is_return and doc.update_stock:
        # Set default values for credit note
        doc.efris_payment_mode = "Credit"
        doc.invoiceapplyc_ategorycode = "credit note"
        
import frappe
from frappe import _

@frappe.whitelist()
def before_save(docname):
    doc = frappe.get_doc("Sales Invoice", docname)
    if doc.is_return and doc.update_stock:
        # Fetch original_invoiceId from Sales Invoice
        original_invoice_id = frappe.get_value("Sales Invoice", doc.return_against, "original_invoiceId")
        
        # Set the original_invoiceId field of the Return Entry
        doc.original_invoiceId = original_invoice_id

        return {
            "oriInvoiceNo": original_invoice_id
        }
    else:
        return None
