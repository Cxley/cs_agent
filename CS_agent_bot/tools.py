import json

# database
ORDERS_DB = {
    "X27": {"item": "Washing Machine X27", "status": "shortage", "eta": "3-5 extra days"},
    "X30": {"item": "Washing Machine X30", "status": "shipped",  "eta": "2 days"},
    "X15": {"item": "Washing Machine X15", "status": "delivered","eta": "already delivered"},
}

# company policy document
POLICY = """
COMPANY POLICY DOCUMENT
=======================

SHIPPING POLICY:
- Standard delivery takes 5-7 business days.
- Express delivery (2-3 days) is available for an extra fee of $15.
- Free shipping on orders above $500.
- Shipping is available nationwide. International shipping is not supported.

RETURN POLICY:
- Items can be returned within 30 days of delivery.
- The item must be unused and in its original packaging.
- To initiate a return, contact support with your order number.
- Return shipping costs are covered by the company for defective items.

REFUND POLICY:
- Refunds are processed within 7-10 business days after the return is received.
- Refunds are issued to the original payment method.
- Partial refunds may apply for items that are not in original condition.
- Sale items are non-refundable unless they arrive damaged or defective.
"""


def policy_tool(question: str) -> str:
    """
    Returns the relevant company policy text.
    The AI will use this to answer the customer's question naturally.
    """
    return POLICY


def order_tool(item_number: str) -> str:
    """
    Looks up the status of an order by item number.
    Returns a JSON string with order details.
    """
    item_number = item_number.upper().strip()
    if item_number in ORDERS_DB:
        return json.dumps(ORDERS_DB[item_number])
    return json.dumps({"error": f"No order found for item number {item_number}."})


def register_order_tool(name: str, item_number: str) -> str:
    """
    Registers a new order for a customer.
    Returns a confirmation message.
    """
    item_number = item_number.upper().strip()
    return json.dumps({
        "success": True,
        "message": f"Order for item {item_number} has been successfully registered under the name {name}."
    })
