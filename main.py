import sys
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient

# Azure credentials
endpoint = "https://centralindia.api.cognitive.microsoft.com/"
key = "f22a0281a5a948d8976834683872265b"

def detect_text(image_path):
    document_analysis_client = DocumentAnalysisClient(
        endpoint=endpoint, credential=AzureKeyCredential(key)
    )

    with open(image_path, "rb") as fd:
        poller = document_analysis_client.begin_analyze_document("prebuilt-invoice", fd.read())
    invoices = poller.result()

    items = []
    for idx, invoice in enumerate(invoices.documents):
        items.append(f"--------Recognizing invoice #{idx + 1}--------")
        vendor_name = invoice.fields.get("VendorName")
        if vendor_name:
            items.append(f"Vendor Name: {vendor_name.value} has confidence: {vendor_name.confidence}")
        vendor_address = invoice.fields.get("VendorAddress")
        if vendor_address:
            items.append(f"Vendor Address: {vendor_address.value} has confidence: {vendor_address.confidence}")
        vendor_address_recipient = invoice.fields.get("VendorAddressRecipient")
        if vendor_address_recipient:
            items.append(f"Vendor Address Recipient: {vendor_address_recipient.value} has confidence: {vendor_address_recipient.confidence}")
        customer_name = invoice.fields.get("CustomerName")
        if customer_name:
            items.append(f"Customer Name: {customer_name.value} has confidence: {customer_name.confidence}")
        customer_id = invoice.fields.get("CustomerId")
        if customer_id:
            items.append(f"Customer Id: {customer_id.value} has confidence: {customer_id.confidence}")
        customer_address = invoice.fields.get("CustomerAddress")
        if customer_address:
            items.append(f"Customer Address: {customer_address.value} has confidence: {customer_address.confidence}")
        customer_address_recipient = invoice.fields.get("CustomerAddressRecipient")
        if customer_address_recipient:
            items.append(f"Customer Address Recipient: {customer_address_recipient.value} has confidence: {customer_address_recipient.confidence}")
        invoice_id = invoice.fields.get("InvoiceId")
        if invoice_id:
            items.append(f"Invoice Id: {invoice_id.value} has confidence: {invoice_id.confidence}")
        invoice_date = invoice.fields.get("InvoiceDate")
        if invoice_date:
            items.append(f"Invoice Date: {invoice_date.value} has confidence: {invoice_date.confidence}")
        invoice_total = invoice.fields.get("InvoiceTotal")
        if invoice_total:
            items.append(f"Invoice Total: {invoice_total.value} has confidence: {invoice_total.confidence}")
        due_date = invoice.fields.get("DueDate")
        if due_date:
            items.append(f"Due Date: {due_date.value} has confidence: {due_date.confidence}")
        purchase_order = invoice.fields.get("PurchaseOrder")
        if purchase_order:
            items.append(f"Purchase Order: {purchase_order.value} has confidence: {purchase_order.confidence}")
        billing_address = invoice.fields.get("BillingAddress")
        if billing_address:
            items.append(f"Billing Address: {billing_address.value} has confidence: {billing_address.confidence}")
        billing_address_recipient = invoice.fields.get("BillingAddressRecipient")
        if billing_address_recipient:
            items.append(f"Billing Address Recipient: {billing_address_recipient.value} has confidence: {billing_address_recipient.confidence}")
        shipping_address = invoice.fields.get("ShippingAddress")
        if shipping_address:
            items.append(f"Shipping Address: {shipping_address.value} has confidence: {shipping_address.confidence}")
        shipping_address_recipient = invoice.fields.get("ShippingAddressRecipient")
        if shipping_address_recipient:
            items.append(f"Shipping Address Recipient: {shipping_address_recipient.value} has confidence: {shipping_address_recipient.confidence}")
        items.append("Invoice items:")
        for idx, item in enumerate(invoice.fields.get("Items").value):
            items.append(f"...Item #{idx + 1}")
            item_description = item.value.get("Description")
            if item_description:
                items.append(f"......Description: {item_description.value} has confidence: {item_description.confidence}")
            item_quantity = item.value.get("Quantity")
            if item_quantity:
                items.append(f"......Quantity: {item_quantity.value} has confidence: {item_quantity.confidence}")
            unit = item.value.get("Unit")
            if unit:
                items.append(f"......Unit: {unit.value} has confidence: {unit.confidence}")
            unit_price = item.value.get("UnitPrice")
            if unit_price:
                items.append(f"......Unit Price: {unit_price.value} has confidence: {unit_price.confidence}")
            product_code = item.value.get("ProductCode")
            if product_code:
                items.append(f"......Product Code: {product_code.value} has confidence: {product_code.confidence}")
            item_date = item.value.get("Date")
            if item_date:
                items.append(f"......Date: {item_date.value} has confidence: {item_date.confidence}")
            tax = item.value.get("Tax")
            if tax:
                items.append(f"......Tax: {tax.value} has confidence: {tax.confidence}")
            amount = item.value.get("Amount")
            if amount:
                items.append(f"......Amount: {amount.value} has confidence: {amount.confidence}")
        subtotal = invoice.fields.get("SubTotal")
        if subtotal:
            items.append(f"Subtotal: {subtotal.value} has confidence: {subtotal.confidence}")
        total_tax = invoice.fields.get("TotalTax")
        if total_tax:
            items.append(f"Total Tax: {total_tax.value} has confidence: {total_tax.confidence}")
        previous_unpaid_balance = invoice.fields.get("PreviousUnpaidBalance")
        if previous_unpaid_balance:
            items.append(f"Previous Unpaid Balance: {previous_unpaid_balance.value} has confidence: {previous_unpaid_balance.confidence}")
        amount_due = invoice.fields.get("AmountDue")
        if amount_due:
            items.append(f"Amount Due: {amount_due.value} has confidence: {amount_due.confidence}")
        service_start_date = invoice.fields.get("ServiceStartDate")
        if service_start_date:
            items.append(f"Service Start Date: {service_start_date.value} has confidence: {service_start_date.confidence}")
        service_end_date = invoice.fields.get("ServiceEndDate")
        if service_end_date:
            items.append(f"Service End Date: {service_end_date.value} has confidence: {service_end_date.confidence}")
        service_address = invoice.fields.get("ServiceAddress")
        if service_address:
            items.append(f"Service Address: {service_address.value} has confidence: {service_address.confidence}")
        service_address_recipient = invoice.fields.get("ServiceAddressRecipient")
        if service_address_recipient:
            items.append(f"Service Address Recipient: {service_address_recipient.value} has confidence: {service_address_recipient.confidence}")
        remittance_address = invoice.fields.get("RemittanceAddress")
        if remittance_address:
            items.append(f"Remittance Address: {remittance_address.value} has confidence: {remittance_address.confidence}")
        remittance_address_recipient = invoice.fields.get("RemittanceAddressRecipient")
        if remittance_address_recipient:
            items.append(f"Remittance Address Recipient: {remittance_address_recipient.value} has confidence: {remittance_address_recipient.confidence}")
        items.append("----------------------------------------")

    return items

def main(image_path, output_path):
    items = detect_text(image_path)
    with open(output_path, 'w', encoding='utf-8') as f:
        for item in items:
            f.write(f"{item}\n")

if __name__ == "__main__":
    image_path = sys.argv[1]
    output_path = sys.argv[2]
    main(image_path, output_path)
