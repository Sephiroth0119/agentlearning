# 2026-07-03 上午学习笔记：Harness、Agent、Tools、Skill、Workflow、Memory

## 这次学到的主线

今天上午从 DeepSeek API 的最小调用开始，一步步拆开了一个 agent 系统到底由什么组成。

核心结论：

```text
model = DeepSeek / GPT / Claude 这类模型
harness = 调用模型、组织 messages、执行 tools、维护循环和状态的代码
tools = 外部函数/API/数据库/文件系统等真实能力
skill = 可复用的做事方法包，常被 harness 编译成 system prompt / tools / 输出约束
workflow/graph = 把 agent loop 拆成显式节点、边和状态
memory = 外部存储 + 检索策略 + 上下文注入
agent = model + harness + tools + state + policy 的整体
```

## API 与 Messages

最基础的模型调用不是发 `question:{}`，而是发：

```json
{
  "model": "deepseek-v4-pro",
  "messages": [
    {"role": "system", "content": "规则"},
    {"role": "user", "content": "用户问题"}
  ]
}
```

常见 role：

```text
system    规则、身份、输出要求
user      用户输入
assistant 模型回答或模型发起的 tool_calls
tool      harness 执行工具后的结果
```

多轮对话不是服务端自动记忆，而是 harness 每次把历史 `messages` 重新传给模型。

## JSON 输出

模型返回的原始 JSON 是字符串：

```python
raw_json = response.choices[0].message.content
```

`json.loads(raw_json)` 之后变成 Python dict，打印时会显示单引号：

```python
{'intent': '...', 'language': 'python'}
```

这不是 JSON 文本。要重新打印成标准 JSON，需要：

```python
print(json.dumps(data, ensure_ascii=False, indent=2))
```

## Tool Calling

模型不会真的执行工具。模型只会返回：

```json
{
  "tool_calls": [
    {
      "id": "call_xxx",
      "function": {
        "name": "get_weather",
        "arguments": "{\"location\":\"Hangzhou\"}"
      }
    }
  ]
}
```

harness 负责：

```text
1. 解析 function.name
2. 解析 function.arguments
3. 执行真实 Python 函数/API
4. 把结果作为 role=tool 放回 messages
5. 再调用模型
```

`tool_call.id` 是这一次工具调用的临时编号，每次请求可能变化。返回工具结果时必须对应：

```json
{
  "role": "tool",
  "tool_call_id": "call_xxx",
  "content": "24 C"
}
```

## Harness

`harness` 本义更接近“挽具/线束/安全带”，不是马鞍。放在 agent 里很贴切：

```text
model 提供语言能力
tools 提供外部能力
harness 把 model 和 tools 接起来，并控制流程
```

在本项目里：

```text
4deepseek-response.py               最小 tool calling harness
5deepseek-agent-loop.py             while loop 版本
6deepseek-agent-loop-multi-tools.py 多工具 + finish 工具版本
```

第 6 个例子的关键设计：

```text
get_weather(location)
calculate(expression)
finish(final_answer)
```

模型通过 `finish` 显式决定结束，harness 看到 `finish` 后退出。

## Agent Loop

最小 agent loop：

```text
用户输入
  -> 调模型
  -> 模型返回 tool_calls
  -> harness 执行 tools
  -> tool result 放回 messages
  -> 再调模型
  -> 直到 finish
```

核心边界：

```text
模型决定下一步想做什么
harness 决定能不能做、怎么做、怎么记录结果
```

## Skill

一个纯知识/纯流程/纯风格的 skill，本质上可以理解成：

```text
可复用、可管理、可按需加载的 system prompt
```

但完整 skill 不只是 system prompt。它还可能包含：

```text
tools 列表
response_format
模板
脚本
检查清单
领域知识
工作流程
```

真实 API request body 一般没有 `skill` 字段。skill 通常由 harness 编译成：

```text
messages 里的 system 内容
request_body["tools"]
response_format
前置执行步骤
```

本项目例子：

```text
7deepseek-skill-loader.py
harness-test/skills/weather_math/SKILL.md
```

## Workflow / LangGraph

手写 loop：

```python
while True:
    call_model()
    run_tools()
    if finish:
        break
```

LangGraph 把这个 loop 显式拆成：

```text
State
Node
Edge
Conditional Edge
```

第 8 个例子：

```text
8deepseek-langgraph.py
```

图结构：

```text
initial_state
  -> agent node: 调模型
  -> tools node: 执行工具
  -> conditional edge:
       有 final_answer -> END
       没有 final_answer -> 回 agent
```

你的理解已经比较准确：

```text
你负责设计流程、状态、节点、边界条件
AI 可以帮你补 Python / LangGraph 语法
```

## State

最小 state：

```python
state = {
    "messages": [],
    "final_answer": None,
    "round_index": 1,
}
```

含义：

```text
messages      当前完整上下文
final_answer  是否结束
round_index   第几轮，主要用于日志
```

更教学化的 state 可以拆更多：

```text
last_assistant_message
pending_tool_calls
last_tool_results
```

但很多时候这些都可以从 `messages[-1]` 里拿到。

## Memory

memory 不是模型真的永久记住了，而是：

```text
外部存储 + 检索策略 + 上下文注入
```

不是每次把所有历史都塞给模型。真实做法一般是：

```text
1. 最近几轮 messages
2. 用户长期 profile 的少量摘要
3. 根据当前问题检索出的相关 memory
4. 必要时 rerank 后只取 top-n
```

本项目例子：

```text
9deepseek-memory-demo.py
```

这个例子用 dict 模拟 memory store，只是为了展示：

```text
memory store 可以很多
每次只选相关的一小部分注入 system
```

## Embedding、向量库、Rerank

向量库存两类东西：

```text
原文 text
原文对应的 embedding vector
```

embedding 的作用：

```text
把文字变成语义坐标
意思相近的文本，向量距离近
意思无关的文本，向量距离远
```

LLM 通常不是直接读向量。流程是：

```text
用户问题 -> embedding
向量库检索相近 memory
取出原文 text
把原文放进 messages
LLM 读原文回答
```

常见中文/多语言 embedding：

```text
BAAI/bge-m3
BAAI/bge-small-zh-v1.5
BAAI/bge-base-zh-v1.5
BAAI/bge-large-zh-v1.5
```

不同 embedding 模型的向量不能混用，因为坐标系、维度、分布都不同。换 embedding 模型通常要重算所有向量。

reranker：

```text
embedding 先粗召回 top-k
reranker 再对 query + candidate text 逐条打分
最后选 top-n 给 LLM
```

reranker 多数吃的是原文文本，不是向量，所以换 reranker 不一定要重建向量库。

## 当前仍要明确的疑问点

1. DeepSeek 的不同模型是否都稳定支持 tool calling、reasoning_content、JSON mode。
2. `message.model_dump()` 会带很多字段，正式 harness 是否应该做 message 清洗。
3. `finish` 工具是否适合所有 agent，还是只适合教学/强协议场景。
4. LangGraph 里状态如何拆分最舒服：只保留 `messages`，还是拆出 `pending_tool_calls`。
5. memory 注入应该走 system message、tool result，还是单独的上下文消息。
6. 本地向量库以后选 Chroma、FAISS、SQLite-vss，还是先用纯内存 demo。
7. embedding/rerank 是用本地 BGE，还是用云 API，取决于机器性能和隐私要求。

## 对学习过程的点评

这次学习节奏是对的：从最小 API 开始，没有一上来直接跳 LangGraph/Dify。

比较好的地方：

```text
1. 先看真实 request body，理解 messages
2. 再看 JSON 输出和 Python dict 的区别
3. 再看 tool_calls 和 tool result 的闭环
4. 再把两轮手写升级成 while loop
5. 再引入多工具和 finish
6. 再理解 skill、workflow、memory
```

这个顺序能把“框架魔法”拆掉。现在再看 Dify/LangGraph，会知道它们本质是在帮你管理 harness。

需要注意的地方：

```text
1. Python 语法不是当前重点，不要陷进去。
2. 先用流程图和 state 思考，再让 AI 补代码。
3. 不要把 demo 里的 keyword if 当成真实 memory 方案。
4. 不要把 skill 简化成永远只是 system prompt；它可以更大，但纯文本 skill 确实近似 system prompt。
5. 不要把向量当成 LLM 直接可读的数据；它只是检索索引。
```

总体结果：今天已经把 agent 系统的核心骨架摸到了。后面学框架会轻松很多，因为你已经知道框架在替你封装什么。

## 后续方向：直接做 ERP 库存 Agent

下一步不再继续纯理论学习，也先不做泛用“学习助手 demo”。更值得落地的方向是：

```text
库存通用查询助手
```

这个判断更对。库存不是边角功能，它天然连接 ERP 的核心业务：

```text
物料
仓库
批次
订单
采购
生产
销售
出入库
占用量
可用量
在途量
```

从库存查起，后面能自然扩展成真正的业务问题：

```text
为什么库存不准？
为什么账上有货但不能发？
为什么采购到了但库存没增加？
为什么生产领料缺料？
为什么某个物料库存异常波动？
```

这比“数据检验 / 垃圾数据识别”更适合作为第一个业务 Agent。后者有价值，但容易停在规则校验、SQL 扫描、异常报表，离业务核心隔一层。

## 第一阶段目标

先围绕 `kchz` 做，不要一上来搞完整 ERP Agent。

第一版只做 3 件事：

```text
1. 理解用户问库存的什么问题
2. 转成 kchz / 库存相关 SQL 或查询参数
3. 返回业务化解释，而不是只返回表格
```

目标链路：

```text
用户自然语言
  -> 理解查询意图
  -> 查询 kchz
  -> 整理库存结果
  -> 返回业务解释
```

例子：

```text
用户：查一下 10086 这个物料现在还有多少库存

Agent：
物料 10086 当前账面库存 xxx。
其中：
- A 仓 xxx
- B 仓 xxx
- 可用库存 xxx
- 冻结 / 占用 xxx
```

重点不是“能不能生成 SQL”，而是：

```text
SQL 结果 -> 业务解释
```

## 第一版问题范围

先固定 5 类问题，跑通就算有价值：

```text
1. 某物料当前库存是多少？
2. 某物料在哪些仓库有库存？
3. 某仓库库存最高的物料有哪些？
4. 某物料近期库存变化是否异常？
5. 某物料账面库存和明细是否对得上？
```

第一版不要追求全覆盖。就把这 5 个问题做扎实。

## 第一版工具设计

完整一点可以这样：

```text
search_material(keyword)       查物料
query_kchz(params)             查库存汇总
query_stock_detail(params)     查库存明细
explain_stock_result(data)     解释库存结果
finish(answer)                 结束本轮
```

如果先极简，可以压成：

```text
query_kchz(sql_condition)
run_sql(sql)
finish(answer)
```

但要注意边界：

```text
模型负责理解意图、组织查询参数、解释结果
harness 负责执行 SQL、控制可执行范围、防止危险 SQL
```

不要让模型随便自由拼任意 SQL 直接跑生产库。第一版应该白名单化：

```text
只允许 SELECT
只允许查库存相关视图/表
限制返回行数
先打印 SQL，再决定是否执行
```

## 建议项目结构

```text
erp-stock-agent/
  main.py
  graph.py
  tools.py
  db.py
  prompts/
    stock_query.md
  rules/
    kchz.md
  reports/
```

各文件职责：

```text
main.py              CLI 入口
graph.py             LangGraph 流程
tools.py             search_material / query_kchz / finish
db.py                数据库连接和 SQL 执行
prompts/stock_query  库存查询助手 system prompt / skill
rules/kchz.md        kchz 字段、口径、业务规则说明
reports/             保存查询结果和调试输出
```

## 第一版 Graph

先保持简单：

```text
User input
  -> agent node
  -> tools node
       search_material / query_kchz / query_stock_detail / finish
  -> 如果 finish，结束
  -> 否则回 agent node
```

state 先只放：

```text
messages
final_answer
last_sql
last_result
round_index
```

后面再加：

```text
selected_material
selected_warehouse
query_params
business_context
```

## 实践优先级

接下来不要继续学抽象概念，直接做：

```text
1. 建 erp-stock-agent 项目骨架
2. 写 kchz.md：字段含义、库存口径、常见问题
3. 先 mock 数据跑通 query_kchz
4. 再接真实数据库只读查询
5. 再加库存明细、异常解释、账实核对
```

先 mock，后真实库。不要第一天就被数据库连接、权限、字段名拖死。

主线调整为：

```text
库存业务问题 > 查询口径 > tool 边界 > graph 流程 > 模型解释
```

而不是：

```text
继续研究 agent 概念
```

这个方向更像真正进入 ERP 业务核心。
