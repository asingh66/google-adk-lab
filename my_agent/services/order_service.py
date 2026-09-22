ORDERS = {
    "12345": {
        "status": "SHIPPED",
        "customer_id": "C100",
        "carrier": "FedEx",
        "destination": "Seattle",
    },
    "67890": {
        "status": "PROCESSING",
        "customer_id": "C200",
        "destination": "New York",
    },
}


def find_order(order_id: str) -> dict | None:
    """Retrieve order information for an order."""
    return ORDERS.get(order_id)
