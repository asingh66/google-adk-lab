SHIPPING = {
    "12345": {
        "estimated_delivery": "2026-09-25",
        "shipping_status": "IN_TRANSIT",
    },
    "67890": {
        "estimated_delivery": "2026-09-28",
        "shipping_status": "NOT_SHIPPED",
    },
}


def find_shipping(order_id: str) -> dict | None:
    """Retrieve shipping information for an order."""
    return SHIPPING.get(order_id)