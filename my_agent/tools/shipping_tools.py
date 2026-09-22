from ..services.shipping_service import find_shipping


def get_shipping_eta(order_id: str) -> dict:
    """Get shipping status and estimated delivery date.

    Args:
        order_id: Unique identifier of the order.

    Returns:
        Shipping information for the requested order.
    """

    shipping = find_shipping(order_id)

    if shipping is None:
        return {
            "success": False,
            "error": "SHIPPING_NOT_FOUND",
            "order_id": order_id,
        }

    return {
        "success": True,
        "order_id": order_id,
        **shipping,
    }