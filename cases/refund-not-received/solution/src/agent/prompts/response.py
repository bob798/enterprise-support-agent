"""
Response templates — all factual fields come from tool output.
No LLM inference on financial values.
"""

TEMPLATES = {
    "pending": (
        "您好，已查询到订单 {order_id} 的退款状态：**处理中**。\n\n"
        "退款金额：{amount} {currency}\n"
        "预计到账时间：{expected_arrival}\n\n"
        "如到期后仍未到账，请重新提交工单，我们将为您进一步跟进。"
    ),
    "initiated": (
        "您好，已查询到订单 {order_id} 的退款状态：**已发起**，正在等待银行处理。\n\n"
        "退款金额：{amount} {currency}\n"
        "预计到账时间：{expected_arrival}\n\n"
        "银行处理通常需要 3–5 个工作日，请耐心等待。如超期仍未到账，请联系我们。"
    ),
    "succeeded": (
        "您好，已查询到订单 {order_id} 的退款状态：**已成功**。\n\n"
        "退款金额：{amount} {currency}\n\n"
        "退款已完成，请确认收款方是否已收到。如买家仍未收到，建议联系其开户行核实，"
        "或重新提交工单由我们协助排查。"
    ),
    "insufficient_funds": (
        "您好，已查询到订单 {order_id} 的退款状态：**失败**。\n\n"
        "失败原因：账户余额不足，无法完成退款。\n\n"
        "请为账户充值后，重新发起退款操作。如操作后仍有问题，请联系我们。"
    ),
    "account_frozen": (
        "您好，已查询到订单 {order_id} 的退款状态：**失败**。\n\n"
        "失败原因：账户存在异常（已冻结或触发风控）。\n\n"
        "请联系您的运营团队处理账户异常后，重新发起退款。如需协助，请提交工单由专员跟进。"
    ),
    "risk_control": (
        "您好，已查询到订单 {order_id} 的退款状态：**失败**。\n\n"
        "失败原因：该笔退款触发了风险控制拦截。\n\n"
        "请联系您的运营团队确认账户风控状态，处理后重新发起退款。"
    ),
    "ask_order_id": (
        "您好，请提供订单号，以便我为您查询退款状态。\n\n"
        "（例：订单号 10248）"
    ),
    "ask_clarification": (
        "您好，请问您是需要查询某笔退款的状态吗？"
        "如是，请提供订单号，我将为您查询。"
    ),
    "order_not_found": (
        "抱歉，未找到订单号 {order_id} 对应的记录。\n\n"
        "请确认订单号是否正确，或重新提供。"
    ),
    "escalated": (
        "您好，您的问题需要人工协助处理，我已将详情转交给技术支持团队。\n\n"
        "我们将在 1 个工作日内与您联系，感谢您的耐心等待。"
    ),
    "error": (
        "抱歉，系统暂时无法查询，已为您提交人工处理请求。\n\n"
        "我们将尽快与您联系。"
    ),
}


def render(template_key: str, **kwargs) -> str:
    template = TEMPLATES.get(template_key, TEMPLATES["error"])
    try:
        return template.format(**kwargs)
    except KeyError:
        return template
