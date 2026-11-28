---
title: 企业知识与工单助手：运行第一个完整本地闭环
description: 从只读查询、跨租户边界到草稿、人工审批和幂等提交，运行并测试一个本地 HTTP 教学服务。
---

# 企业知识与工单助手：运行第一个完整本地闭环

前面的示例分别解释了[知识查询](./knowledge-assistant-first-slice)、[回归评估](./knowledge-assistant-evaluation)和[审批与幂等](./ticket-approval-and-retry)。现在把这些动作放进同一条可以实际调用的 HTTP 链路：客服查询规则，创建一份待审工单；审核人查看并批准；客服提交，重复请求不会重复创建工单。

**这是本地教学服务，不是生产级 Agent。** 文档、用户和身份标识都是虚构的；服务包含简单的本地练习页面，但没有调用模型，也没有真实身份认证、外部工单系统或完整企业安全控制。它的价值是让你先看到一条真实运行的请求链，再有依据地逐步替换模拟部件。

## 1. 你将运行什么

```text
客服 → 授权范围内查询文档 → 返回内容与版本引用 / 无证据拒答
  ↓
创建工单草稿 → 同租户审核人查看草稿 → 批准当前内容
  ↓
客服提交 operation ID → SQLite 中创建一条模拟工单
  ↓
重复相同请求 → 返回已有结果，不再创建
```

HTTP 服务仅监听 `127.0.0.1`，使用 Python 标准库和本地 SQLite，不需要 API 密钥或第三方依赖。**不要改为公网监听，也不要放入真实客户资料。** 固定的 `X-Demo-Token` 仅用于演示“服务端如何得到身份”，任何知道字符串的人都能冒充该身份，绝不是生产登录方案。

## 2. 启动并跑通一次

获取本项目源码后，在仓库根目录打开一个终端：

```bash
cd examples/enterprise-agent-lab
python3 server.py
```

保持服务运行，另开终端并进入同一个目录：

```bash
python3 walkthrough.py
python3 -m unittest -v
```

也可以在本机浏览器打开 [http://127.0.0.1:8765](http://127.0.0.1:8765)，依次点击“查询”“创建草稿”“读取草稿”“批准已查看版本”和“提交工单”；再点一次提交，观察重放结果。这个地址只在你的本地服务启动后有效。

需要 Python 3.10 或更新版本。命令行演示应输出“知识查询”“待审草稿”“审批结果”“首次提交”和“重复提交”：前者的 `replayed` 为 `False`，后者为 `True`，两次工单 ID 相同。ID 每次运行不同；本地 HTTP 测试还会验证跨租户读取、审批过期与撤销、并发重试、文档版本及旧数据库升级。可选 SDK 测试缺少依赖时会跳过。

完整代码见 [enterprise-agent-lab](https://github.com/xiaoqianbaobao/ai-guide/tree/main/examples/enterprise-agent-lab)。按 `Ctrl+C` 停止服务；演示数据保存在该目录的 `lab.sqlite3`，文件已加入忽略列表。仅使用教学数据时，可以停止服务后删除这个文件重新开始。

## 3. 沿着请求看数据边界

| 请求 | 示例身份 | 服务端处理 | 预期结果 |
| --- | --- | --- | --- |
| `POST /api/ask` | 客服 | 根据服务端身份选择租户文档，再做字面匹配 | 返回 `refund-v1`，或资料不足 |
| `GET /api/documents/{id}` | 同租户审核人 | 获取当前文档与版本 | 为更新或撤回提供待核对的版本 |
| `POST /api/document-update` | 同租户审核人 | 在事务内检查预期版本，保存新版本与历史 | 成功递增版本；旧版本请求返回 409 |
| `POST /api/document-withdraw` | 同租户审核人 | 在事务内标记撤回并保存历史 | 后续查询不再命中撤回文档 |
| `POST /api/drafts` | 客服 | 创建同租户草稿，记录创建者和内容摘要 | 返回待审批的草稿 ID |
| `POST /api/draft-update` | 同租户草稿创建者 | 检查预期版本后更新文本、修订号并清除批准 | 版本冲突返回 409，修改后需重新批准 |
| `GET /api/drafts/{id}` | 审核人 | 按服务端租户读取草稿 | 审核人能看到实际内容 |
| `POST /api/approve` | 审核人 | 提交查看时获得的版本；事务中比对并保存审核人 | 草稿变化时返回 409，要求重新查看 |
| `POST /api/revoke` | 审核人 | 在同一事务内确认工单尚未提交并撤销批准 | 提交前可以撤销；已提交则返回 409 |
| `POST /api/submit` | 客服 | 核对批准摘要，在本地事务中按操作 ID 创建模拟工单 | 首次创建；相同请求可重放 |

例如，在服务运行时，可直接用 `curl` 发起知识查询。这里的标识是公开的教学字符串，不是密钥：

```bash
curl -s http://127.0.0.1:8765/api/ask \
  -H 'Content-Type: application/json' \
  -H 'X-Demo-Token: demo-support' \
  -d '{"question":"退款"}'
```

你应看到 `answered`、退款规则片段和 `refund-v1`。将问题改为“薪酬”，客服身份会得到 `insufficient_evidence` 与空引用。示例按原文子串查找，“退钱”未必匹配“退款”；这正是需要用任务集测量的检索缺陷。

### 演练知识更新和撤回

下面使用**独立临时数据库和 8766 端口**，不会修改上面 8765 服务的数据库。在 `examples/enterprise-agent-lab` 的一个新终端运行，保持该终端打开：

```bash
LAB_DIR="$(mktemp -d)"
python3 -c 'import sys; from server import make_server; make_server(sys.argv[1], 8766).serve_forever()' "$LAB_DIR/lab.sqlite3"
```

在另一个终端依次执行以下请求。第一次查询文档获取 `revision`；示例假设临时数据库是新建的，版本为 1。更新成功返回版本 2，使用旧版本再次更新会得到 HTTP 409。

```bash
curl -s http://127.0.0.1:8766/api/documents/refund-v1 \
  -H 'X-Demo-Token: demo-support-reviewer'
curl -s http://127.0.0.1:8766/api/document-update \
  -H 'Content-Type: application/json' -H 'X-Demo-Token: demo-support-reviewer' \
  -d '{"document_id":"refund-v1","expected_revision":1,"text":"退款需要核对发票与订单。"}'
curl -s http://127.0.0.1:8766/api/ask \
  -H 'Content-Type: application/json' -H 'X-Demo-Token: demo-support' \
  -d '{"question":"发票"}'
curl -s http://127.0.0.1:8766/api/document-withdraw \
  -H 'Content-Type: application/json' -H 'X-Demo-Token: demo-support-reviewer' \
  -d '{"document_id":"refund-v1","expected_revision":2}'
curl -s http://127.0.0.1:8766/api/ask \
  -H 'Content-Type: application/json' -H 'X-Demo-Token: demo-support' \
  -d '{"question":"发票"}'
```

更新后的查询包含 `source_versions`，其中 `refund-v1` 的 `revision` 为 2；撤回后的查询返回 `insufficient_evidence`。`refund-v1` 是沿用的固定文档 ID，实际版本以独立的 `revision` 字段为准。完成后用 `Ctrl+C` 停止 8766 服务；临时目录只含虚构数据，可自行删除。教学页面目前没有文档管理界面，上述接口通过命令或测试演练。

这里的检索直接读取数据库，没有向量索引或缓存，因此演示的是**源文档更新和撤回**，不是已经解决索引、缓存或已展示回答的失效问题。历史表保存完整旧文本供本地观察，旧数据库迁移只能保存迁移时的当前快照，无法恢复此前丢失的版本；真实系统需要单独设计历史版本的访问、保留、删除和审计。可选[模型调用链](./enterprise-agent-model-tool-loop)会在生成答案后检查检索版本是否仍有效，但检查完成到答案显示之间仍可能发生变更；版本号也不证明生成内容受来源支持。

## 4. 为什么同一条链路要测试失败

`test_server.py` 启动一个随机端口的本地服务，真实发起 HTTP 请求并使用临时数据库，检查：

1. 客服能查询自己租户的退款规则，不能从回答中取得人事租户的薪酬原文。
2. 人事身份不能查看客服草稿；客服不能充当审核人，未批准不能提交。
3. 审核人看到草稿并批准后，相同操作 ID 重试只保留一张模拟工单；同一草稿换 ID 再提交会被拒绝。
4. 测试直接修改数据库中的草稿文本以模拟篡改，原审批不再适用。
5. 多个客户端并发重试同一操作时，SQLite 事务与唯一约束使示例中只有一次创建。
6. 审核人读取草稿后、批准前内容被修改，旧版本返回 409，提交仍被拒绝；重新查看后才能批准。
7. 批准在服务端 5 分钟后过期，或审核人撤销批准后，新提交被拒绝；提交与撤销同时发生时，只有先完成的事务生效。
8. 只有同租户审核人能修改文档；两个更新使用同一版本时一个成功、另一个返回 409。撤回后查询不再命中，重启也不会恢复已撤回文档；旧数据库迁移保留迁移时的内容。
9. 两份草稿内容相同时，查看第一份得到的版本不能用于批准第二份；批准后创建者发生变化，也不能再提交。

### 内容相同，为什么仍是两次审批？

假设两份草稿文字都是“请核实退款”，但草稿 ID 或创建者不同。如果审核版本只计算“租户 + 文本”，审核人读取第一份后，调用方就可能将相同版本值用于批准第二份，即使审核人没有看过第二份。现在示例将**租户、草稿 ID、创建者、文本和递增修订号**一起编码并计算版本摘要，审批和首次提交都会重新计算：

```bash
cd examples/enterprise-agent-lab
python3 -m unittest \
  test_server.ApiTests.test_review_of_one_draft_cannot_approve_another_with_same_text \
  test_server.ApiTests.test_creator_change_invalidates_approval \
  test_server.ApiTests.test_old_unexpired_content_only_approval_requires_reapproval -v
```

三个测试使用虚构身份、临时 SQLite 数据库和本地 HTTP 服务。第三项模拟旧版本只按内容生成的审批：即使尚未过期，也不能用于新版本的首次提交，必须重新读取并批准。加入修订号前生成的审批也需要重新确认。**已完成工单的相同操作 ID 重试仍返回已有回执**，不会因此创建新工单。

摘要只用于检测所列字段是否变化，不是签名，也不能证明审核人确实阅读或拥有权限。真实审批需要可信身份和服务端鉴权，显示并绑定实际接收目标、动作、参数、数据版本及有效期；示例没有真实接收目标。发布这种审批格式变更时，还要考虑旧批准如何失效、如何通知审核人，以及避免新旧服务实例同时使用不同计算规则。

### 草稿修改：文本改回原样也要重新审核

`POST /api/draft-update` 接收 `draft_id`、读取草稿时获得的 `expected_version` 和新 `text`。服务端在一个 SQLite 写事务中检查租户、创建者、是否已经提交和预期版本；成功后递增修订号并清除已有批准。两个请求使用同一个旧版本并发修改时，先完成的成功，后一个收到 409。

在本地网页的“人工审核”区域可以亲自体验：创建并读取草稿，点击批准；在下方修改文本并保存，观察提交按钮重新禁用；再次读取、批准后才能提交。网页只是用固定演示身份分别模拟操作员和审核人，按钮禁用也不代替服务端检查。

为什么要增加修订号？如果草稿从 A 改成 B 又改回 A，只比较内容摘要会让旧版 A 看起来再次有效。修订号记录了**修改发生过**，所以旧审批不能复用。可以运行：

```bash
cd examples/enterprise-agent-lab
python3 -m unittest \
  test_server.ApiTests.test_edit_invalidates_approval_even_if_text_is_restored \
  test_server.ApiTests.test_draft_update_concurrency_and_authorization -v
```

示例的修订号和审批清除依赖所有修改都经过这个服务；有权限直接改数据库的人仍可能绕过它。生产系统应限制数据库写权限，并将状态变更、版本和审计记录纳入同一可信事务。

### 过期与重试为什么需要分开处理

一次批准只允许在有效期内首次提交。服务端在本地事务内检查版本与到期时间；撤销使用同一数据库的写事务，避免撤销与首次提交同时成功。若提交先完成，撤销会返回 409：**撤销审批不会撤回已经创建的工单**，后者需要另行设计业务补偿。

如果工单已经创建，而客户端丢失了响应，即使审批后来过期，相同租户、草稿和操作 ID 的重试仍应返回已有回执；它没有再次执行写入。示例先查找已完成操作，再检查新写入的审批条件。若操作 ID 或草稿与已有记录不匹配，服务端拒绝请求。

可以在页面上创建草稿、读取并批准后点击“撤销批准”，再尝试提交；也可以等到批准过期后再提交。自动化测试使用可注入的测试时钟，不需要真的等待五分钟。旧版教学数据库没有记录到期时间时，服务升级会添加字段，并要求重新批准；不会把旧批准当成永久有效。

测试证明的是这几个教学输入在本地实现中的结果；它们不证明系统对所有越权、注入、并发、日志、备份或基础设施问题都安全。服务中的同租户可见范围也很粗，并没有实现文档级和项目级授权。

如果想把前一课的四条知识问答任务跑在这个服务上，使用[本地服务评估适配器](./knowledge-assistant-evaluation#用同一组任务评估本地企业助手)。它直接调用服务方法并创建临时数据库，不会接入真实模型或生产数据。

## 5. 把教学服务逐步升级

| 下一步 | 需要替换或增加 | 先补什么验收 |
| --- | --- | --- |
| 真实身份 | 用组织身份提供方建立可信服务端会话；移除固定教学标识 | 过期凭证、角色撤销、租户切换与越权访问 |
| 检索与模型 | 接入授权的文档源、版本与模型适配器；保留无证据拒答 | 同义召回、引用支持结论、文档撤回、提示注入 |
| 审批体验 | 在可信界面展示接收目标、内容和版本；持久记录审批有效期与撤回 | 过期或变更后的审批失效、越权审批拒绝 |
| 外部工单 | 集成真实服务，确认其幂等、查询与失败语义 | 响应丢失、重复事件、对账与人工补偿 |
| 运维与观测 | 限流、超时、脱敏日志、审计权限、备份与恢复演练 | 服务重启、依赖故障、并发、恢复和泄露检查 |

当前工单表与草稿表在同一个 SQLite 数据库里，本地事务不能代表跨服务一致性。示例使用服务端墙上时钟和固定五分钟有效期；真实系统还要设计时间同步、时钟异常、持久审计与策略配置。教学页面不是可信认证界面，也没有真实审核人认证或外部系统状态验证。固定身份、HTTP 明文、简易输入限制、审计和错误处理都只适合这次练习。**不要把这个仓库示例直接部署为企业服务。**

## 6. 给自己加一个验收任务

### 集成的第一步：固定已审批的外部提交意图

跨服务写入不能把“检查审批”和“记录将要提交什么”拆成两个互不关联的步骤：中间如果草稿被修改或批准被撤销，后续发送的内容就可能不再是审核人看过的内容。本实验新增 `prepare_external_submission`，在**同一个 SQLite 写事务**中检查演示身份、租户、当前草稿版本和批准有效期，保存操作 ID、内容、批准版本、审核人和有效期。重复准备同一操作会返回已保存记录；不同意图不能复用该操作 ID。

在仓库根目录运行：

```bash
cd examples/enterprise-agent-lab
python3 -m unittest test_external_prepare -v
```

测试覆盖未批准、跨租户、过期、重启后重放、相同操作并发、准备与撤销竞争，以及与原有本地提交路径的 ID 冲突。并发测试中，准备先完成则普通撤销被拒绝；普通撤销先完成则准备因无有效批准失败。这里的 `prepared` 只是**已保存意图**，没有发送请求，也没有创建外部工单。

这个中间阶段冻结已准备的草稿，阻止继续修改、重新批准、普通撤销或通过旧路径提交。演示代码提供独立的 `cancel_external_submission` 方法：同租户审核人仅能取消仍为 `prepared` 的意图；它在事务中保留已取消操作 ID 和审核信息、释放草稿并清除原批准。要再次准备，必须重新审批并使用新操作 ID；重复取消旧操作不会影响新的准备记录。如果状态已经是 `unknown`，方法拒绝取消，因为此时不能假定外部写入没有发生。

批准在准备后到期时，重放只返回原记录，**不会延长批准，也不代表之后可以发送**。固定版本和 SQLite 事务也不能让外部服务和本地数据库成为一个事务。

### 接上本机模拟下游：发送、崩溃与对账

现在已有一个独立的 Python 集成练习，把准备阶段与[跨服务写入与对账恢复](./cross-service-write-recovery)的本机模拟 HTTP 服务接起来；仍没有对外 HTTP 入口或真实身份认证。运行：

```bash
cd examples/enterprise-agent-lab
python3 -m unittest test_external_delivery -v
```

时序如下：

1. 发送者在本地事务中再次检查当前批准版本和有效期，把 `prepared` 改为 `unknown` 后提交事务；取消也需要同一数据库写锁，因此两者只能有一个先成功。
2. 只有拿到发送资格的调用者向本机模拟服务写入。载荷绑定租户、草稿 ID、批准版本与内容；演示下游按操作 ID 去重。
3. 收到有效回执时记录 `confirmed`。如果响应丢失、进程在网络调用前后退出，状态保留 `unknown`；再次调用发送函数不会盲目重发。
4. 对账使用同一个操作 ID 查下游，核对回执和载荷摘要；匹配才确认。查不到、查询失败或摘要不匹配都不能宣称成功。

例如测试先让模拟服务提交工单后主动断开连接，再重建本地服务对象、查询下游，确认只有一条工单。另一个测试在发送资格取得后模拟进程中断：下游没有记录，但本地仍为 `unknown`，不会自动重发。这些是隔离环境测试，不是外部业务系统的运行结果。源码见 [external_delivery.py](https://github.com/xiaoqianbaobao/ai-guide/blob/main/examples/enterprise-agent-lab/external_delivery.py) 和 [test_external_delivery.py](https://github.com/xiaoqianbaobao/ai-guide/blob/main/examples/enterprise-agent-lab/test_external_delivery.py)。

**时效边界：**本例在领取发送资格时检查批准有效期；进程可能在事务提交后暂停很久，实际网络发送时批准已过期。SQLite 无法约束另一台机器何时执行。真实系统需要结合下游可验证的授权和截止时间、可靠任务租约与短时凭证等机制，定义并验证业务允许的发送时点；如果下游不能强制执行该约束，就不能声称本例实现了严格的发送时授权。模拟下游还假设可信回执、持久幂等和可查询；没有真实认证、生产权限、自动重试预算或人工对账界面。`unknown` 查不到时仍需人工处理，不能无限冻结或擅自解锁。

下一篇[接入模型：只读工具调用链](./enterprise-agent-model-tool-loop)会用离线模拟测试模型如何请求查询；真实 API 调用需要自行配置且尚未在本课程中实测。

## 参考资料

- [OpenAI：A practical guide to building agents](https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/)：从工具、编排和防护边界入手设计 Agent。
- [Anthropic：Demystifying evals for AI agents](https://www.anthropic.com/research/demystifying-evals-for-ai-agents)：把任务结果和轨迹转化为可重复评估。
- [Stripe：Idempotent requests](https://docs.stripe.com/api/idempotent_requests)：接入真实外部服务时，核对其版本对应的幂等与重试语义。

资料核验日期：2026-11-25。
