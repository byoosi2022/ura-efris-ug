frappe.ui.form.on("Sales Invoice", {
    refresh: function (frm) {
        if (frm.doc.is_return) {
            frm.add_custom_button(
                __("Get EFRIS Credit Note Details"),
                function () {
                    frappe.call({
                        method:
                            "ura_efris.api.efris_print_format.send_request_to_post_sales",
                        args: {
                            docname: frm.doc.return_against,
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
    },
});
