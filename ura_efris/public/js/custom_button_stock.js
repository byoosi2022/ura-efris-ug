frappe.ui.form.on("Stock Entry", {
    refresh: function (frm) {
        if (frm.doc.docstatus == 1) {
            frm.add_custom_button(
                __("Send To EFRIS"),
                function () {
                    frappe.call({
                        method: "ura_efris.api.efris_stock_entry.send_request_to_api",
                        args: {
                            docname: frm.doc.name,
                            modified: frm.doc.modified,
                        },
                        callback: function (response) {
                            console.log(response);
                        },
                    });
                },
                __("EFRIS")
            );
        }
    },
});

