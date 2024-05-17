
import frappe
import json

@frappe.whitelist()
def send_request_to_post_sales(docname):
    # Fetch the Sales Invoice document using the provided docname
    doc = frappe.get_doc("Sales Invoice", docname)
    
    # Extract necessary fields from the Sales Invoice document
    main_content = doc.main_content
    net_total = doc.net_total
    total_taxes_and_charges = doc.total_taxes_and_charges
    grand_total = doc.grand_total 
    
    # Parse the main_content field which is expected to be a JSON string
    message_dict = json.loads(main_content)
    
    # Extract the tax_rate from the message_dict
    tax_rate = (
        message_dict.get("doc.main_content", {})
        .get("basicInformation", {})
        .get("antifakeCode")
    )
    
    # Return the required values
    return {
        "message_dict": message_dict,
        "net_total": net_total,
        "total_taxes_and_charges": total_taxes_and_charges,
        "grand_total": grand_total,
      }
