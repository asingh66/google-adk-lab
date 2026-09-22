from google.adk.agents import Agent

from .tools.order_tools import get_order_status
from .tools.customer_tools import get_customer
from .tools.shipping_tools import get_shipping_eta


root_agent = Agent(
    name="order_support_agent",
    model="gemini-2.5-flash",

    description="""
    Order support agent that can retrieve order,
    customer, and shipping information.
    """,

    instruction="""
    You are an order support agent.

    Use the available tools whenever the user asks
    for factual information about orders, customers,
    or shipping.

    Never invent order, customer, or shipping information.

    If information is unavailable from the tools,
    clearly tell the user that the information is unavailable.

    When a question requires information from multiple
    systems, use all necessary tools before answering.
    """,

    tools=[
        get_order_status,
        get_customer,
        get_shipping_eta,
    ],
)