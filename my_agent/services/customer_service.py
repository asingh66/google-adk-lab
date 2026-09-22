CUSTOMERS = {
    "C100": {
        "name": "John Smith",
        "membership": "GOLD",
    },
    "C200": {
        "name": "Jane Miller",
        "membership": "STANDARD",
    },
}


def find_customer(customer_id: str) -> dict | None:
    """Retrieve customer information for a customer."""
    return CUSTOMERS.get(customer_id)
