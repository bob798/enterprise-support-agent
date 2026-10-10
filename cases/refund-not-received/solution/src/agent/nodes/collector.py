"""
Node: Information Collector

Ensures order_id is present before calling tools.
If missing, increments retry count and routes back to ask.
Max retries = 2; beyond that → escalate.
"""

from agent.state import AgentState

MAX_RETRIES = 2


def check_order_id(state: AgentState) -> dict:
    """
    Routing node — decides next action based on whether we have an order_id.
    Does not modify state; returns empty dict.
    Pure routing logic lives in graph.py edges.
    """
    return {}


def increment_retry(state: AgentState) -> dict:
    retries = state.get("collect_retries", 0) + 1
    return {"collect_retries": retries}
