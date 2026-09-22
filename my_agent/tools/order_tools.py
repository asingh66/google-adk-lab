from ..services.order_service import find_order


def get_order_status(order_id: str) -> dict:
    """Get current order information including status and customer ID.

    Args:
        order_id: Unique identifier of the order.

    Returns:
        Current information for the requested order.
    """

    order = find_order(order_id)

    if order is None:
        return {
            "success": False,
            "error": "ORDER_NOT_FOUND",
            "order_id": order_id,
        }

    return {
        "success": True,
        "order_id": order_id,
        **order,
    }