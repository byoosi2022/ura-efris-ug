from frappe import _
import frappe

@frappe.whitelist()
def insert_efris_data(doc=None, method=None):
    try:
        # Data for AdjustType doctype
        adjust_types = [
            {"adjusttype": "Expired Goods", "code": "102", "operationtype": "101"},
            {"adjusttype": "Damaged Goods", "code": "102", "operationtype": "102"},
            {"adjusttype": "Personal Uses", "code": "102", "operationtype": "103"},
            {"adjusttype": "Raw Material(s)", "code": "102", "operationtype": "105"}
        ]

        for adjust_type in adjust_types:
            validate_and_insert(adjust_type, "AdjustType Efris", "adjusttype")

        # Data for InvoiceApplyCategoryCode doctype
        invoice_categories = [
            {"label": "credit note", "code": "101"},
            {"label": "cancellation of debit note", "code": "103"},
            {"label": "multiple values", "code": "101,103"},
            {"label": "debit note", "code": "102"},
            {"label": "cancel of credit note", "code": "104"}
        ]

        for invoice_category in invoice_categories:
            validate_and_insert(invoice_category, "efris credit note invoiceApplyCategoryCode", "label")

        # Data for Efris paymentModes doctype
        payment_modes = [
            {"efris_payment_mode": "Credit", "efris_pd_code": "101"},
            {"efris_payment_mode": "Cash", "efris_pd_code": "102"},
            {"efris_payment_mode": "Cheque", "efris_pd_code": "103"},
            {"efris_payment_mode": "Demand draft", "efris_pd_code": "104"},
            {"efris_payment_mode": "Mobile Money", "efris_pd_code": "105"},
            {"efris_payment_mode": "Visa/Master card", "efris_pd_code": "106"}
        ]

        for mode in payment_modes:
            validate_and_insert(mode, "Efris paymentModes", "efris_payment_mode")

        # Data for taxCategoryCode doctype
        tax_categories = [
            {"description": "Exempt", "taxcategorycode": "3", "value": "-"},
            {"description": "Excise Duty", "taxcategorycode": "5", "value": ""},
            {"description": "Deemed", "taxcategorycode": "4", "value": "18%"},
            {"description": "Standard", "taxcategorycode": "1", "value": "0.18"},
            {"description": "Zero (0%)", "taxcategorycode": "2", "value": "0"},
            {"description": "Test Onistall)", "taxcategorycode": "4", "value": "0"}
        ]

        for category in tax_categories:
            validate_and_insert(category, "taxCategoryCode", "description")

        frappe.msgprint(_("Data inserted successfully"))
    except Exception as e:
        frappe.log_error(f"Error inserting data: {e}")
        frappe.msgprint(_("Failed to insert data. Please check the error log for details."))

def validate_and_insert(data, doctype, field_to_check):
    existing_doc = frappe.get_list(doctype, filters={field_to_check: data[field_to_check]})
    if not existing_doc:
        new_doc = frappe.get_doc({
            "doctype": doctype,
            **data  # Include all fields from the data dictionary
        })
        new_doc.insert(ignore_permissions=True)
        frappe.msgprint(_(f"{doctype} '{data[field_to_check]}' inserted successfully"))
    else:
        frappe.msgprint(_(f"{doctype} '{data[field_to_check]}' already exists"))
