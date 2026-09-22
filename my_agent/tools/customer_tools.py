from ..services.customer_service import find_customer


def get_customer(customer_id: str) -> dict:
    """Get customer information.

    Args:
        customer_id: Unique identifier of the customer.

    Returns:
        Information about the requested customer.
    """

    customer = find_customer(customer_id)

    if customer is None:
        return {
            "success": False,
            "error": "CUSTOMER_NOT_FOUND",
            "customer_id": customer_id,
        }

    return {
        "success": True,
        "customer_id": customer_id,
        **customer,
    }