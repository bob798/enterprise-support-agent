# TODO

## 进行中

### Case 2: 外卖异常订单退款（food-delivery-damaged-order）

**目标：** 完整复刻 refund-not-received 的交付路径，覆盖含主观判断的退款场景

- [ ] **Discovery**
  - [ ] 梳理外卖平台现有异常订单处理流程（工作流清单）
  - [ ] 识别 AI 介入点：哪些步骤适合自动化，哪些必须人工
  - [ ] 确认小额自动批准阈值的业务决策依据
  - [ ] 完成机会评估打分（目标 ≥ 16/21）

- [ ] **Design**
  - [ ] L4 角色声明：明确 AI 判断损坏描述 vs 规则引擎决定退款金额 的边界
  - [ ] 风险评估：虚假申报风控、高频退款用户识别
  - [ ] 定义验收标准（功能 + 安全 + 性能）
  - [ ] Tool Contract：order_lookup / damage_policy / refund_eligibility / escalate

- [ ] **Build**
  - [ ] AgentState 定义（含 damage_type、evidence_provided、user_refund_history）
  - [ ] 节点实现：intent → collect → damage_assess → eligibility_check → respond/escalate
  - [ ] Mock 数据：订单系统、损坏类型、用户退款历史
  - [ ] Mock 模式支持（无 API Key 可运行）

- [ ] **Validate**
  - [ ] 单元测试：router / responder / escalator
  - [ ] 安全测试：高频退款用户被正确拦截
  - [ ] Demo 场景覆盖（≥ 6 个）：正常损坏、少送、高频用户、无订单号、超时效、大额升级

- [ ] **文档**
  - [ ] problem/：现有流程、机会评估
  - [ ] solution/：架构决策、设计原则（含 L4 表）
  - [ ] benefits/：效率提升、一致性保障
  - [ ] challenges/：主观判断的设计难点记录

---

## 待规划

- [ ] **文章发布**：refund-not-received 三层文章（掘金技术篇 → 知乎方法论篇 → LinkedIn 商业篇）
- [ ] **evals/**：golden_dataset.jsonl（160 case）+ run_eval.py
- [ ] **observability/**：OpenTelemetry 接入，tracing dashboard
- [ ] **多模型支持**：LLM_PROVIDER 环境变量，接入 DeepSeek / GLM / Qwen

---

## 笔记（待整理）

> 以下是思考过程中的原始记录，有价值的内容后续提取到 knowledge/

**LLM 在客服中负责什么：**
- 理解自然语言
- 从用户描述抽取结构化信息
- 解释规则结果
- 调用知识库
- 给出可理解的下一步建议
- 询问缺失信息

**支付公司 B2B 退款场景的卡点：**
- 公司内部概念不统一
- 知识库或文档过时
- 退款状态歧义，需要人工确认
- 流程割裂，跨多个系统

**企业用 AI 客服的前置条件：**（目标客户主要是中大型互联网企业或新型互联网公司）
1. 文档线上化
2. 订单管理系统化
3. 工单系统化

另一种路径：针对存量系统做 AI 扩展（Salesforce、开源 CRM 等）

**典型客户识别 3 个特征：** 客户特征、存在问题、解决方案
