# In your .py file
import frappe
from frappe import _

@frappe.whitelist()
def create_stock_entry(items, warehouse, posting_date):
    try:
        stock_entry = frappe.new_doc("Stock Entry")
        stock_entry.purpose = "Material Receipt"
        stock_entry.posting_date = posting_date
        stock_entry.set("items", [])

        for item in items:
            stock_entry.append("items", {
                "item_code": item.get("item_code"),
                "qty": item.get("qty"),
                "rate": item.get("rate"),
                "warehouse": warehouse,
            })

        stock_entry.insert(ignore_permissions=True)
        stock_entry.submit()

        return True

    except Exception as e:
        frappe.log_error(_("Error creating Stock Entry: {0}").format(str(e)))
        return False
