frappe.ui.form.on("Sales Invoice", {
    refresh: function (frm) {
        if (!frm.doc.is_return) {
            frm.add_custom_button(
                __("Send Sales Invoice To EFRIS"),
                function () {
                    frappe.call({
                        method: "ura_efris.api.sales_efris.send_request_to_api",
                        args: {
                            docname: frm.doc.name,
                            modified: frm.doc.modified,
                        },
                        callback: function (response) {
                            console.log(response);
                        },
                    });
                    // Add your custom button code here
                },
                __("EFRIS")
            );
        } else {
            frm.add_custom_button(
                __("Send Credit Note To EFRIS"),
                function () {
                    frappe.call({
                        method: "ura_efris.api.credit_note_application.send_request_to_api",
                        args: {
                            docname: frm.doc.name,
                            modified: frm.doc.modified,
                        },
                        callback: function (response) {
                            console.log(response);
                        },
                    });
                    // Add your custom button code here
                },
                __("EFRIS")
            );
        }

        if (frm.doc.is_return) {


            frm.add_custom_button(
                __("Get Original ID"),
                function () {
                    frappe.call({
                        method: "ura_efris.api.credit_note_application.before_save",
                        args: { 
                            docname: frm.doc.name,
                        },
                        callback: function (response) {
                            console.log(response);
                            var invoice_no = response.message.oriInvoiceNo;
                            frm.set_value("original_invoiceid", invoice_no);
                            frappe.msgprint("Original ID has been returned. You can save to print.");
            
                         },
                    });
                },
                __("EFRIS")
            );
            




            frm.add_custom_button(
                __("Get The ID Approval"),
                function () {
                    frappe.call({
                        method: "ura_efris.api.credit_approval.credit_note_approval",
                        args: {
                            docname: frm.doc.name,
                            oriinvoiceid: frm.doc.original_invoiceid,
                            original_invoiceno: frm.doc.original_invoiceno,
                            modified: frm.doc.modified,
                        },
                        callback: function (response) {
                            var efris_return_id = response.message.id;
                            var invoice_no = response.message.oriInvoiceNo;
                            console.log(response);
                            if (efris_return_id) {
                                frm.set_value("efris_return_id", efris_return_id);
                                frappe.msgprint("Id has been returned you can save to print ");
                            } else {
                                frappe.msgprint(
                                    "This Credit Note ID has not been received"
                                );
                            }
                        },
                    });
                    // Add your custom button code here
                },
                __("EFRIS")
            );
            frm.add_custom_button(
                __("Check Approval Status"),
                function () {
                    frappe.call({
                        method:
                            "ura_efris.api.credit_approval_status_code.credit_note_approval",
                        args: {
                            docname: frm.doc.name,
                            modified: frm.doc.modified,
                            efris_return_id: frm.doc.efris_return_id,
                        },
                        callback: function (response) {
                            console.log(response.message);
                            var status_code = response.message;
                            if (status_code == 101) {
                                frappe.msgprint(__("This Credit Note is " + "Approved"));
                            } else if (status_code == 102) {
                                frappe.msgprint(__("This Credit Note is " + "Pending"));
                            } else if (status_code == 103) {
                                frappe.msgprint(__("This Credit Note is " + "Rejected"));
                            }

                            //console.log(response)
                            // Handle the response from the server here
                        },
                    });
                    // Add your custom button code here
                },
                __("EFRIS")
            );
            frm.add_custom_button(
                __("Get Return QR Code"),
                function () {
                    frappe.call({
                        method: "ura_efris.api.credit_approval_check.credit_note_approval",
                        args: {
                            docname: frm.doc.name,
                            modified: frm.doc.modified,
                            efris_return_id: frm.doc.efris_return_id,

                            // grand_total: frm.doc.grand_total
                            // doc: frm.doc,
                            // method: 'ura_efris.api.credit_approval.credit_note_approval',
                            // // Add any arguments to the function here
                        },
                        callback: function (response) {
                            var qr_Code = response.message.summary.qrCode;
                            var efris_return_invoiceid =
                                response.message.basicInformation.invoiceId;
                            var efris_return_invoiceNo =
                                response.message.basicInformation.invoiceNo;
                            var efris_return_verification_code =
                                response.message.basicInformation.antifakeCode;
                            frm.set_value("efris_return_qrcode", qr_Code);
                            frm.set_value("efris_return_invoice_id", efris_return_invoiceid);
                            frm.set_value("efris_return_invoice_no", efris_return_invoiceNo);
                            frm.set_value(
                                "efris_return_verification_code",
                                efris_return_verification_code
                            );
                            frappe.msgprint(
                                "New qrCode has been returned you can save to print "
                            );
                            console.log(response.message);
                            //console.log(response)
                            // Handle the response from the server here
                        },
                    });
                    // Add your custom button code here
                },
                __("EFRIS")
            );

            frm.add_custom_button(
                __("Get EFRIS Invoice Details"),
                function () {
                    frappe.call({
                        method:
                            "ura_efris.api.efris_print_format.send_request_to_post_sales",
                        args: {
                            docname: frm.doc.name,
                            main_content: frm.doc.main_content,
                        },
                        callback: function (response) {
                            console.log(response)

                            // Get the message from the response, which is a dictionary containing the JSON data
                            var message = response.message;
                            // Get the antifakeCode value from the JSON data
                            var antifakeCode = message.basicInformation.antifakeCode;
                            var ninBrn = message.sellerDetails.ninBrn;
                            var tin = message.sellerDetails.tin;
                            var legalName = message.sellerDetails.legalName;
                            var address = message.sellerDetails.address;
                            var referenceNo = message.sellerDetails.referenceNo;
                            var operator = message.basicInformation.operator;
                            var document_type = "Original";
                            var issuedDate = message.basicInformation.issuedDate;
                            var deviceNo = message.basicInformation.deviceNo;
                            buyerTin;
                            var invoiceNo = message.basicInformation.invoiceNo;

                            var buyerTin = message.buyerDetails.buyerTin;
                            var buyerLegalName = message.buyerDetails.buyerLegalName;
                            var goodsDetails = message.goodsDetails;
                            var taxDetails = message.taxDetails;
                            var netAmount = message.summary.netAmount;
                            var taxAmount = message.summary.taxAmount;
                            var grossAmount = message.summary.grossAmount;
                            var paymentAmount = message.payWay.paymentAmount;
                            var currency = message.basicInformation.currency;
                            var itemCount = message.summary.itemCount;
                            var remarks = message.summary.remarks;
                            var qrCode = message.summary.qrCode;

                            frm.set_value("verification_code_efri_", antifakeCode);
                            frm.set_value("brn_efri", ninBrn);
                            frm.set_value("tin_efri", tin);
                            frm.set_value("legal_name_efr", legalName);
                            frm.set_value("trade_name_efr", legalName);
                            frm.set_value("address_efr", address);
                            frm.set_value("sellers_reference_number_efr", referenceNo);
                            frm.set_value("served_by_efr", operator);
                            frm.set_value("document_type_efr", document_type);
                            frm.set_value("issued_date", issuedDate);
                            frm.set_value("device_number", deviceNo);
                            frm.set_value("fiscal_document_number", invoiceNo);
                            frm.set_value("tin_buyers", buyerTin);
                            frm.set_value("name_buyer", buyerLegalName);
                            frm.set_value("net_amount_efr", netAmount);
                            frm.set_value("tax_amount", taxAmount);
                            frm.set_value("gross_amount", grossAmount);
                            frm.set_value("credit", paymentAmount);
                            frm.set_value("efris_remarks", remarks);
                            frm.set_value("number_of_items", itemCount);
                            frappe.msgprint(
                                "Efris Invoice Details has been successfully Retrieved please close and save to print efris pdf "
                            );
                            //  console.log(goodsDetails)
                            frm.doc.goods__details = [];
                            $.each(goodsDetails, function (_i, e) {
                                let entry = frm.add_child("goods__details");
                                // console.log(entry)
                                entry.item = e.item;
                                entry.quantity = e.qty;
                                entry.unit_price = e.unitPrice;
                                entry.total = e.total;
                                // unpaid_amount = unpaid_amount + entry.debt
                            });
                            //   console.log(taxDetails)
                            frm.doc.tax_details = [];
                            $.each(taxDetails, function (_i, e) {
                                let entry = frm.add_child("tax_details");
                                console.log(entry);
                                entry.tax_category = e.taxCategory;
                                entry.net_amount = e.netAmount;
                                entry.tax_amount = e.taxAmount;
                                entry.gross_amount = e.grossAmount;
                                // unpaid_amount = unpaid_amount + entry.debt
                            });
                        },
                    });
                    // Add your custom button code here
                },
                __("EFRIS")
            );
        }

        if (frm.doc.is_efris) {
            frm.add_custom_button(
                __("Print EFRIS pdf"),
                function () {
                    frappe.call({
                        method:
                            "ura_efris.api.efris_print_format.send_request_to_post_sales",
                        args: {
                            docname: frm.doc.name,
                            main_content: frm.doc.main_content,
                        },
                        callback: function (response) {
                            // Get the PDF format name of your custom print format
                            var print_format = "EFRIS PRINT FORMAT SALES";
                            // Generate the URL to download the PDF file
                            var url =
                                "/api/method/frappe.utils.print_format.download_pdf?doctype=Sales Invoice&name=" +
                                frm.doc.name +
                                "&format=" +
                                print_format +
                                "&no_letterhead=0&_lang=en&_print=no";
                            // Open the PDF file in a new tab
                            window.open(url);
                        },
                    });
                    // Add your custom button code here
                },
                __("EFRIS")
            );
            frm.add_custom_button(
                __("Get EFRIS Invoice Details"),
                function () {
                    frappe.call({
                        method:
                            "ura_efris.api.efris_print_format.send_request_to_post_sales",
                        args: {
                            docname: frm.doc.name,
                            main_content: frm.doc.main_content,
                        },
                        callback: function (response) {
                            console.log(response)

                            // Get the message from the response, which is a dictionary containing the JSON data
                            var message = response.message;
                            // Get the antifakeCode value from the JSON data
                            var antifakeCode = message.basicInformation.antifakeCode;
                            var ninBrn = message.sellerDetails.ninBrn;
                            var tin = message.sellerDetails.tin;
                            var legalName = message.sellerDetails.legalName;
                            var address = message.sellerDetails.address;
                            var referenceNo = message.sellerDetails.referenceNo;
                            var operator = message.basicInformation.operator;
                            var document_type = "Original";
                            var issuedDate = message.basicInformation.issuedDate;
                            var deviceNo = message.basicInformation.deviceNo;
                            buyerTin;
                            var invoiceNo = message.basicInformation.invoiceNo;

                            var buyerTin = message.buyerDetails.buyerTin;
                            var buyerLegalName = message.buyerDetails.buyerLegalName;
                            var goodsDetails = message.goodsDetails;
                            var taxDetails = message.taxDetails;
                            var netAmount = message.summary.netAmount;
                            var taxAmount = message.summary.taxAmount;
                            var grossAmount = message.summary.grossAmount;
                            var paymentAmount = message.payWay.paymentAmount;
                            var currency = message.basicInformation.currency;
                            var itemCount = message.summary.itemCount;
                            var remarks = message.summary.remarks;
                            var qrCode = message.summary.qrCode;

                            frm.set_value("verification_code_efri_", antifakeCode);
                            frm.set_value("brn_efri", ninBrn);
                            frm.set_value("tin_efri", tin);
                            frm.set_value("legal_name_efr", legalName);
                            frm.set_value("trade_name_efr", legalName);
                            frm.set_value("address_efr", address);
                            frm.set_value("sellers_reference_number_efr", referenceNo);
                            frm.set_value("served_by_efr", operator);
                            frm.set_value("document_type_efr", document_type);
                            frm.set_value("issued_date", issuedDate);
                            frm.set_value("device_number", deviceNo);
                            frm.set_value("fiscal_document_number", invoiceNo);
                            frm.set_value("tin_buyers", buyerTin);
                            frm.set_value("name_buyer", buyerLegalName);
                            frm.set_value("net_amount_efr", netAmount);
                            frm.set_value("tax_amount", taxAmount);
                            frm.set_value("gross_amount", grossAmount);
                            frm.set_value("credit", paymentAmount);
                            frm.set_value("efris_remarks", remarks);
                            frm.set_value("number_of_items", itemCount);
                            frappe.msgprint(
                                "Efris Invoice Details has been successfully Retrieved please close and save to print efris pdf "
                            );
                            //  console.log(goodsDetails)
                            frm.doc.goods__details = [];
                            $.each(goodsDetails, function (_i, e) {
                                let entry = frm.add_child("goods__details");
                                // console.log(entry)
                                entry.item = e.item;
                                entry.quantity = e.qty;
                                entry.unit_price = e.unitPrice;
                                entry.total = e.total;
                                // unpaid_amount = unpaid_amount + entry.debt
                            });
                            //   console.log(taxDetails)
                            frm.doc.tax_details = [];
                            $.each(taxDetails, function (_i, e) {
                                let entry = frm.add_child("tax_details");
                                console.log(entry);
                                entry.tax_category = e.taxCategory;
                                entry.net_amount = e.netAmount;
                                entry.tax_amount = e.taxAmount;
                                entry.gross_amount = e.grossAmount;
                                // unpaid_amount = unpaid_amount + entry.debt
                            });
                        },
                    });
                    // Add your custom button code here
                },
                __("EFRIS")
            );

            frm.add_custom_button(
                __("credit note query"),
                function () {
                    frappe.call({
                        method: "ura_efris.api.query_credit_note.send_request_to_api",
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
        
        if (frm.doc.is_return) {
            frm.add_custom_button(
                __("Print EFRIS Return pdf"),
                function () {
                    frappe.call({
                        method:
                            "ura_efris.efris_data.credit_note_format.send_request_to_post_sales",
                        args: {
                            docname: frm.doc.return_against,
                        },
                        callback: function (response) {
                            // Get the PDF format name of your custom print format
                            var print_format = "EFRIS RETURNPRINT FORMAT";
                            // Generate the URL to download the PDF file
                            var url =
                                "/api/method/frappe.utils.print_format.download_pdf?doctype=Sales Invoice&name=" +
                                frm.doc.name +
                                "&format=" +
                                print_format +
                                "&no_letterhead=0&_lang=en&_print=no";
                            // Open the PDF file in a new tab
                            window.open(url);
                        },
                    });
                    // Add your custom button code here
                },
                __("EFRIS")
            );
            frm.add_custom_button(
                __("Get EFRIS RETURN Invoice Details"),
                function () {
                    frappe.call({
                        method:
                            "ura_efris.efris_data.credit_note_format.send_request_to_post_sales",
                        args: {
                            docname: frm.doc.return_against,
                          
                        },
                        callback: function (response) {
                            console.log(response)

                            // Get the message from the response, which is a dictionary containing the JSON data
                            var message = response.message.message_dict; 
                            var messages = response.message;                            ;
                            // Get the antifakeCode value from the JSON data
                            var antifakeCode = message.basicInformation.antifakeCode;
                            var ninBrn = message.sellerDetails.ninBrn;
                            var tin = message.sellerDetails.tin;
                            var legalName = message.sellerDetails.legalName;
                            var address = message.sellerDetails.address;
                            var referenceNo = message.sellerDetails.referenceNo;
                            var operator = message.basicInformation.operator;
                            var document_type = "Original";
                            var issuedDate = message.basicInformation.issuedDate;
                            var deviceNo = message.basicInformation.deviceNo;
                            buyerTin;
                            var invoiceNo = message.basicInformation.invoiceNo;

                            var buyerTin = message.buyerDetails.buyerTin;
                            var buyerLegalName = message.buyerDetails.buyerLegalName;
                            var goodsDetails = message.goodsDetails;
                            var taxDetails = message.taxDetails;
                            var netAmount = message.summary.netAmount;
                            var taxAmount = message.summary.taxAmount;
                            var grossAmount = message.summary.grossAmount;
                            var paymentAmount = message.payWay.paymentAmount;
                            var currency = message.basicInformation.currency;
                            var itemCount = message.summary.itemCount;
                            var remarks = message.summary.remarks;
                            var qrCode = message.summary.qrCode;

                            // Create a formatted string with line breaks
                            let formatted_value = `Net Amount: ${messages.net_total}
                            \nTax Amount: ${messages.total_taxes_and_charges}
                            \nGross Amount:: ${messages.grand_total}`;
                
                            // Set the value in the small text field
                            frm.set_value("served_by_efr", formatted_value);

                            frm.set_value("verification_code_efri_", antifakeCode);
                            frm.set_value("brn_efri", ninBrn);
                            frm.set_value("tin_efri", tin);
                            frm.set_value("legal_name_efr", legalName);
                            frm.set_value("trade_name_efr", legalName);
                            frm.set_value("address_efr", address);
                            frm.set_value("sellers_reference_number_efr", referenceNo);
                            frm.set_value("served_by", operator);
                            frm.set_value("document_type_efr", document_type);
                            frm.set_value("issued_date", frm.doc.posting_date);
                            frm.set_value("device_number", deviceNo);
                            frm.set_value("fiscal_document_number", invoiceNo);
                            frm.set_value("tin_buyers", buyerTin);
                            frm.set_value("name_buyer", buyerLegalName);
                            frm.set_value("net_amount_efr", netAmount);
                            frm.set_value("tax_amount", taxAmount);
                            frm.set_value("gross_amount", grossAmount);
                            frm.set_value("credit", paymentAmount);
                            frm.set_value("efris_remarks", remarks);
                            frm.set_value("number_of_items", itemCount);
                            frm.set_value("main_content", "Return of products due to expiry or damage, etc");
                            frappe.msgprint(
                                "Efris Invoice Details has been successfully Retrieved please close and save to print efris pdf "
                            );
                            //  console.log(goodsDetails)
                            frm.doc.goods__details = [];
                            $.each(goodsDetails, function (_i, e) {
                                let entry = frm.add_child("goods__details");
                                // console.log(entry)
                                entry.item = e.item;
                                entry.quantity = e.qty;
                                entry.unit_price = e.unitPrice;
                                entry.total = e.total;
                                // unpaid_amount = unpaid_amount + entry.debt
                            });
                            //   console.log(taxDetails)
                            frm.doc.tax_details = [];
                            $.each(taxDetails, function (_i, e) {
                                let entry = frm.add_child("tax_details");
                                console.log(entry);
                                entry.tax_category = e.taxCategory;
                                entry.net_amount = e.netAmount;
                                entry.tax_amount = e.taxAmount;
                                entry.gross_amount = e.grossAmount;
                                // unpaid_amount = unpaid_amount + entry.debt
                            });
                        },
                    });
                    // Add your custom button code here
                },
                __("EFRIS")
            );

            frm.add_custom_button(
                __("credit note query"),
                function () {
                    frappe.call({
                        method: "ura_efris.api.query_credit_note.send_request_to_api",
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

frappe.ui.form.on("Purchase Receipt", {
    refresh: function (frm) {
        frm.add_custom_button(
            __("Send To EFRIS"),
            function () {
                frappe.call({
                    method: "ura_efris.api.purchase_receipt.send_request_to_api",
                    args: {
                        docname: frm.doc.name,
                        modified: frm.doc.modified,
                    },
                    callback: function (response) {
                        console.log(response);
                    },
                });
                // Add your custom button code here
            },
            __("EFRIS")
        );
    },
});
