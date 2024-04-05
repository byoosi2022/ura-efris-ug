# ..............imports to EFRIS.................
import frappe
from frappe import _
from frappe.utils import nowdate, getdate
from ura_efris.api.utils import (
    get_ura_efris_settings,
    create_global_info,
    b64encode,
    get_main_content_from_reponse,
    get_return_code_and_message,
    create_data,
)
import json
import requests
import datetime


@frappe.whitelist()
def send_request_to_api(docname, modified=None):
    doc = frappe.get_doc("Sales Invoice", docname)
    send_request_to_post_sales(doc=doc, method="from_api")


@frappe.whitelist()
def send_request_to_post_sales(doc, method):
    if doc.is_return:
        return
    if (
        doc.is_efris
        and doc.update_stock
        and doc.docstatus == 1
        and not (doc.qr_code or doc.efris_return_qrcode)
    ):
        tin, deviceNo, url = get_ura_efris_settings(doc)
        # frappe.msgprint(_("Thanks your Data has been sent to Efris"+tin+deviceNo+url))
        # Combine dictionaries into a new one

        url = url
        goodsDetails = []
        taxDetails = []
        orderNumber = 0  # initialize the order number to 0
        total_net_amount = 0
        total_taxes_and_charges = 0
        for activity in doc.items:
            total_net_amount += activity.net_amount
            gross_amount = activity.net_amount * (
                1 + float(0 if activity.efris_value == "-" else activity.efris_value)
            )
            tax_amount = activity.net_amount * float(
                0 if activity.efris_value == "-" else activity.efris_value
            )
            gross_total = activity.net_amount + tax_amount
            total_taxes_and_charges += round(tax_amount, 2)
            goodsDetails.append(
                {
                    "item": activity.item_name,
                    "itemCode": activity.item_code,
                    "qty": activity.stock_qty,
                    "unitOfMeasure": activity.unitofmeasure,
                    "unitPrice": str(round(gross_amount / activity.stock_qty, 7)),
                    "total": str(round(gross_amount, 7)),
                    "taxRate": activity.efris_value,
                    "tax": str(round(tax_amount, 2)),
                    "discountTotal": "",
                    "discountTaxRate": "0",
                    "orderNumber": str(
                        orderNumber
                    ),  # add the order number to the dictionary,
                    "discountFlag": "2",
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
        # frappe.msgprint(f"taxDetails: {taxDetails}")
        grand_total = total_net_amount + total_taxes_and_charges
        if isinstance(doc.posting_date, str):
            issue_date = doc.posting_date
        elif isinstance(doc.posting_date, datetime.datetime):
            issue_date = doc.posting_date.strftime("%Y-%m-%d")
        else:
            issue_date = getdate(nowdate()).strftime("%Y-%m-%d %H:%M:%S")
        if doc.efris_payment_mode == "Credit":
            paymentAmount = doc.outstanding_amount
        elif doc.efris_payment_mode == "Cash":
            paymentAmount = doc.paid_amount
        else:
            paymentAmount = 0
        dataitem = {
            "sellerDetails": {
                "tin": tin,
                "ninBrn": "",
                "legalName": doc.company,
                "businessName": doc.company,
                "address": "",
                "mobilePhone": "0700816291",
                "linePhone": "",
                "emailAddress": "info@byoosi.com",
                "placeOfBusiness": "Kampala",
                "referenceNo": doc.name,
                "branchId": "",
                "isCheckReferenceNo": "",
            },
            "basicInformation": {
                "invoiceNo": doc.name,
                "antifakeCode": "",
                "deviceNo": "",
                "issuedDate": issue_date,
                "operator": doc.owner,
                "currency": "UGX",
                "oriInvoiceId": "",
                "invoiceType": doc.efris_invoice_reciept,
                "invoiceKind": "1",
                "dataSource": "106",
                "invoiceIndustryCode": "106",
                "isBatch": "0",
            },
            "buyerDetails": {
                "buyerTin": doc.tax_id,
                "buyerNinBrn": "76869876",
                "buyerPassportNum": doc.buyerpassportnum,
                "buyerLegalName": doc.customer_name,
                "buyerBusinessName": doc.customer_name,
                "buyerAddress": doc.buyeraddress or "Kampala",
                "buyerEmail": doc.buyeremail,
                "buyerMobilePhone": doc.buyermobilephone,
                "buyerLinePhone": doc.buyerlinephone,
                "buyerPlaceOfBusi": doc.buyerplaceofbusi,
                "buyerType": "0",
                "buyerCitizenship": "1",
                "buyerSector": "1",
                "buyerReferenceNo": doc.name,
            },
            "buyerExtend": {
                "propertyType": "",
                "district": "Kampala",
                "municipalityCounty": "Kira",
                "divisionSubcounty": "Kira",
                "town": "Kiraka",
                "cellVillage": "central",
                "effectiveRegistrationDate": "",
                "meterStatus": "",
            },
            "summary": {
                "netAmount": str(round(total_net_amount, 2)),  # 45,677.97
                "taxAmount": str(round(total_taxes_and_charges, 2)),  # 8,222.03
                "grossAmount": str(round(grand_total, 2)),  # 53,900.00
                "itemCount": str(activity.idx),
                "modeCode": "0",
                "remarks": "E-Tax invoices and receipts",
                "qrCode": "",
            },
            "payWay": {
                "paymentMode": doc.efris_pd_code,
                "paymentAmount": paymentAmount,
                "orderNumber": doc.po_no,
            },
            "extend": {"reason": "", "reasonCode": ""},
        }

        # frappe.msgprint(f"dataitem: {dataitem['summary']}")
        payload = {}
        payload.update(dataitem)
        payload["goodsDetails"] = goodsDetails
        # frappe.throw(f"taxDetails: str({taxDetails})")
        payload["taxDetails"] = taxDetails
        # Encode as base64
        temp = json.dumps(payload)
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
        data["global_info"] = create_global_info("T109", deviceNo, tin)
        response = requests.post(url, json=data)
        returnCode, returnMessage = get_return_code_and_message(response)
        in_returnCode = int(returnCode)
        if in_returnCode == 00:
            main_content = get_main_content_from_reponse(response)
            update_doc_returned_data(
                doc=doc,
                main_content=main_content,
                method=method,
                response=response,
            )
        elif in_returnCode == 2253:
            frappe.msgprint(
                _(
                    f"Return code: {in_returnCode}.<BR> Return Message: {str(returnMessage)}"
                )
            )

            import re

            # Find the third occurrence of the pattern using regular expressions
            pattern = r"\((.*?)\)"
            matches = re.finditer(pattern, returnMessage)
            occurrence = 3

            # Extract the Seller's Reference Number from the third occurrence
            if not doc.sellers_reference_number:
                for match in matches:
                    occurrence -= 1
                    if occurrence == 0:
                        doc.sellers_reference_number = match.group(1)
                        break

            if doc.sellers_reference_number:
                get_invoice_details(doc, method, doc.sellers_reference_number)

        else:
            doc.efris_remarks = returnMessage
            if method == "from_api":
                doc.save()
                frappe.db.commit()
            frappe.msgprint(
                _(str({"returnCode": returnCode, "returnMessage": returnMessage}))
            )
    elif not doc.update_stock:
        frappe.throw(_("Please check Update Stock to send to EFRIS"))
    elif doc.qr_code:
        frappe.throw(_("Invoice has already been sent to EFRIS"))
    elif doc.docstatus == 0:
        frappe.throw(_("Please Submit the Invoice to send to EFRIS"))
    elif not doc.is_efris:
        frappe.throw(_("Please check Is Efris to send to EFRIS"))


def send_to_api_bulk():
    sales_invoices = frappe.get_all(
        "Sales Invoice",
        filters={
            "docstatus": 1,
            "update_stock": 1,
            "is_efris": 1,
            "qr_code": None,
        },
        fields=["name"],
        pluck="name",
    )
    for sales_invoice in sales_invoices:
        try:
            send_request_to_api(sales_invoice)
        except Exception as e:
            frappe.log_error(f"{str(e)}", _("Failed to send Sales Invoice to EFRIS"))


def get_invoice_details(doc, method, seller_reference_number):
    tin, deviceNo, url = get_ura_efris_settings(doc)

    invoice_details_request = {"invoiceNo": seller_reference_number}
    invoice_details_request_json = json.dumps(invoice_details_request)
    base64_message = b64encode(invoice_details_request_json)
    data = {
        "data": {
            "content": base64_message,
            "signature": "",
            "dataDescription": {"codeType": "0", "encryptCode": "1", "zipCode": "0"},
        },
        "returnStateInfo": {"returnCode": "", "returnMessage": ""},
    }
    data["data"] = create_data(base64_message)
    data["global_info"] = create_global_info("T108", deviceNo, tin)
    response = requests.post(url, json=data)
    main_content = get_main_content_from_reponse(response)
    update_doc_returned_data(
        doc=doc, main_content=main_content, method=method, response=response
    )


def update_doc_returned_data(doc, main_content, method="from_api", response=None):
    returnCode, returnMessage = get_return_code_and_message(response)
    data = json.loads(main_content)
    summary_print = data["summary"]
    net_amount_sumary_print = summary_print["netAmount"]

    basic_info = data["basicInformation"]
    antifake_code = basic_info["antifakeCode"]
    oriinvoiceid = basic_info["invoiceId"]
    oriinvoiceNo = basic_info["invoiceNo"]
    device_no = basic_info["deviceNo"]
    operator_print = basic_info["operator"]
    issued_date_print = basic_info["issuedDate"]
    issued_date_print = basic_info["issuedDate"]

    seller_details = data["sellerDetails"]
    brn_print = seller_details["ninBrn"]
    tin_print = seller_details["tin"]
    legal_name_print = seller_details["legalName"]
    address_print = seller_details["address"]
    referenceno_print = seller_details["referenceNo"]
    tin_print = seller_details["tin"]

    summary = data["summary"]

    qr_code = summary["qrCode"]
    doc.db_set("qr_code", qr_code)
    doc.db_set("antifake_code", antifake_code)
    doc.db_set("verification_code", device_no)
    doc.db_set("returnmessage", returnMessage)
    doc.db_set("main_content", main_content)
    doc.db_set("original_invoiceid", oriinvoiceid)
    doc.db_set("original_invoiceno", oriinvoiceNo)
    doc.db_set("qr_code", qr_code)
    doc.db_set("brn", brn_print)
    doc.db_set("tin", tin_print)
    doc.db_set("document_type", "Original")
    doc.db_set("legal_name", legal_name_print)
    doc.db_set("trade_name", legal_name_print)
    doc.db_set("served_by", operator_print)
    doc.db_set("issued_date", issued_date_print)
    doc.db_set("time", doc.posting_time)
    doc.db_set("device_number", device_no)
    doc.db_set("fiscal_document_number", oriinvoiceNo)
    doc.db_set("address", address_print)
    doc.db_set("sellers_reference_number", referenceno_print)
    doc.db_set("net_amount", net_amount_sumary_print)
    sales_efris_response = frappe.new_doc("Sales Efris Responses")
    sales_efris_response.update(
        {
            "sales_invoice": doc.name,
            "qr_code": qr_code,
            "custom": doc.customer,
            "status_code": returnMessage,
            "antifake_code": antifake_code,
            "verification_code": antifake_code,
            "original_invoiceid": oriinvoiceid,
            "original_invoiceno": oriinvoiceNo,
            "sales_invoice_content": main_content[:1000],
        }
    )
    sales_efris_response.insert()
    if method == "from_api":
        doc.save()
        frappe.db.commit()
    frappe.msgprint(_("Thanks. Your Data has been sent to EFRIS"), alert=True)
