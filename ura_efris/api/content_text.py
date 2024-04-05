import frappe
from frappe import _

@frappe.whitelist()
def get_matching_efris_response(sales_invoice_name):
    sales_invoice_doc = frappe.get_doc("Sales Invoice", sales_invoice_name)

    # Retrieve the Sales Efris Responses document that matches the Sales Invoice name
    if not sales_invoice_doc.is_return:
        efris_response_doc = frappe.get_doc("Sales Efris Responses", {"sales_invoice": sales_invoice_name})
    else:
        efris_response_doc = frappe.get_doc("Sales Return Efris Responses", {"sales_invoice": sales_invoice_name})

    # If a matching Sales Efris Responses document is found, return it
    if efris_response_doc:
        sales_invoice_doc.main_content = efris_response_doc.sales_invoice_content
        sales_invoice_doc.save()
        frappe.db.commit()
        frappe.msgprint("Message Content field has been successfully saved")
        return efris_response_doc

    # If no matching Sales Efris Responses document is found, return None
    return "No matching Sales Efris Responses document found for Sales Invoice {}.".format(sales_invoice_name)


@frappe.whitelist()
def before_save(doc, method):
    # Get the original state of the doc
    original_doc = frappe.get_doc("Sales Invoice", doc.name)

    # Check if any fields have been updated
    if doc.as_dict() != original_doc.as_dict():
        # Save the updated doc
        doc.save()

    # Return the doc object
    return doc