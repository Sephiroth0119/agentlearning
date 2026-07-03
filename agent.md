# AgentLearning Project Note

这个项目用来记录我的 AI agent 学习过程。

当前重点不是做一个完整产品，而是把学习过程沉淀下来：

```text
1. 理解 model / harness / tools / workflow / memory 的关系
2. 用 DeepSeek API 写最小可运行例子
3. 逐步从 demo 过渡到真实 ERP 业务场景
4. 后续重点转向库存通用查询助手 / kchz 场景
```

## 项目定位

```text
这是学习记录仓库
不是生产代码仓库
不是完整框架封装
不是最终 ERP Agent
```

代码可以粗糙一点，但每个例子要说明它在验证什么。

## 当前学习路径

```text
DeepSeek API
  -> messages / role
  -> JSON output
  -> tool calling
  -> agent loop
  -> skill
  -> LangGraph workflow
  -> memory / embedding / rerank
  -> ERP stock agent
```

## 后续方向

下一步优先做：

```text
erp-stock-agent
```

第一目标：

```text
用户自然语言
  -> 查询 kchz
  -> 返回库存业务解释
```

先 mock 数据，跑通流程。
再接真实数据库。
最后再考虑 embedding、rerank、Dify 对照。

## 记录原则

```text
先记真实理解
再补术语
先跑通最小链路
再优化结构
不要为了框架而框架
```
