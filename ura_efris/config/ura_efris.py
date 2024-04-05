from __future__ import unicode_literals
from frappe import _


def get_data():
    return [
        {
            "label": _("EFRIS Settings"),
            "icon": "octicon octicon-book",
            "items": [
                {
                    "type": "doctype",
                    "name": "Efris Settings Uganda",
                    "label": _("Efris Settings Uganda"),
                    "description": _("Efris Settings"),
                    # Not displayed on dropdown list action but on page after click on module
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "Efris Goods Category Ids",
                    "label": _("Efris Goods Category Ids"),
                    "description": _("Goods Category Ids"),
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "AdjustType Efris",
                    "label": _("AdjustType Efris"),
                    "description": _("AdjustType Efris"),
                    # Not displayed on dropdown list action but on page after click on module
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "Efris Goods Category Ids",
                    "label": _("Efris Goods Category Ids"),
                    "description": _("Efris Goods Category Ids"),
                    # Not displayed on dropdown list action but on page after click on module
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "taxCategoryCode",
                    "label": _("Efris Tax CategoryCode"),
                    "description": _("taxCategoryCode"),
                    # Not displayed on dropdown list action but on page after click on module
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "Efris paymentModes",
                    "label": _("Efris paymentModes"),
                    "description": _("Efris paymentModes"),
                    # Not displayed on dropdown list action but on page after click on module
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "efris credit note invoiceApplyCategoryCode",
                    "label": _("Efris Credit Note InvoiceApply Category Code"),
                    "description": _("Efris paymentModes"),
                    # Not displayed on dropdown list action but on page after click on module
                    "onboard": 1,
                },
            ],
        },
        {
            "label": _("Sales Efris Responses"),
            "icon": "octicon octicon-book",
            "items": [
                {
                    "type": "doctype",
                    "name": "Sales Efris Responses",
                    "label": _("Sales Efris Responses"),
                    "description": _("Efris Stored Responses"),
                    # Not displayed on dropdown list action but on page after click on module
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "Sales Return Efris Responses",
                    "label": _("Sales Return Efris Responses"),
                    "description": _("Efris Stored sales Return Responses"),
                    # Not displayed on dropdown list action but on page after click on module
                    "onboard": 1,
                },
            ],
        },
        {
            "label": _("Implementation"),
            "icon": "octicon octicon-book",
            "items": [
                {
                    "type": "doctype",
                    "name": "Item",
                    "label": _("Enter Efris Item"),
                    "description": _("Efris Item"),
                    # Not displayed on dropdown list action but on page after click on module
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "Purchase Invoice",
                    "label": _("Enter Efris Stock"),
                    "description": _("Efris Stock"),
                    # Not displayed on dropdown list action but on page after click on module
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "Sales Invoice",
                    "label": _("Enter Efris Sales"),
                    "description": _("Efris Sales"),
                    # Not displayed on dropdown list action but on page after click on module
                    "onboard": 1,
                },
                {
                    "type": "doctype",
                    "name": "Stock Entry",
                    "label": _("Stock Efris Adjustment"),
                    "description": _("Stock Efris Adjustment"),
                    # Not displayed on dropdown list action but on page after click on module
                    "onboard": 1,
                },
            ],
        },
    ]
