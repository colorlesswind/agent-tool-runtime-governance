# Agent Tool Runtime Governance

一个"工具调用治理"教学项目：模型提交的任何工具调用都必须经过唯一的执行入口
`ToolRuntime.invoke()`，依次走完 **Pydantic 参数校验 → 三态权限状态机 → 业务预检 →
一次性参数绑定审批 → 超时与重试恢复 → 结果脱敏 → 审计追踪** 这条链路。

## 环境要求

- Python **>= 3.11**（代码使用了 `StrEnum` 与 `asyncio.timeout`）
- 已在 conda 环境 `agent-tool-runtime-governance`（Python 3.12.16）验证通过

## 1. 安装依赖

```bash
python -m pip install -r requirements.txt
```

## 2. 配置环境变量

```bash
cp .env.example .env      # Windows PowerShell: Copy-Item .env.example .env
```

然后编辑 `.env`，把占位符换成真实密钥：

| 变量 | 必需性 | 默认值 | 说明 |
|---|---|---|---|
| `DEEPSEEK_API_KEY` | 仅 `--agent` 必需 | 无 | DeepSeek API Key |
| `DEEPSEEK_BASE_URL` | 可选 | `https://api.deepseek.com` | OpenAI 兼容接口地址 |
| `DEEPSEEK_MODEL` | 可选 | `deepseek-v4-flash` | 模型名 |

`.env` 已被 `.gitignore` 忽略，不要提交。

> 注意：`src/tool_governance_demo.py` 只用 `os.environ` 读配置，**不会自己解析 `.env`**。
> 需要 `.env` 生效时请通过 `run.py` 启动；直接在 shell 里 export 变量后运行原脚本同样可以。

## 3. 运行

### 3.1 离线演示（推荐，不需要密钥）

跑 6 个预置调用，演示脱敏、审批、参数注入拦截、deny 规则和 plan 模式：

```bash
python run.py
```

等价写法（不经过 `.env`，也不需要任何密钥）：

```bash
python src/tool_governance_demo.py
```

预期末尾输出：

```json
{"side_effects": {"refund_executions": 1, "shell_executions": 0}, "audit_records": 8}
```

### 3.2 真实模型闭环（需要 API Key）

```bash
python run.py --agent --input "请查询订单 ord_1001 的状态和可退金额"
```

- `--input` 默认值为 `请查询订单 ord_1001 的状态和可退金额`
- 只暴露 `get_order` 工具（执行白名单），所有工具调用仍经过 `ToolRuntime.invoke()`
- 若 `DEEPSEEK_API_KEY` 仍是占位符，会直接提示并退出，不会发起网络请求
- 临时覆盖某个变量（`.env` 不会被覆盖，因为 `override=False`）：

  ```bash
  # bash
  DEEPSEEK_MODEL=deepseek-v4-flash python run.py --agent
  # PowerShell
  $env:DEEPSEEK_MODEL="deepseek-v4-flash"; python run.py --agent
  ```

### 3.3 测试

```bash
python -m pytest test/test_tool_governance.py -v -k "transfer"
```

`pytest.ini` 里配置了 `pythonpath = src`，所以无需手动设置 `PYTHONPATH`。
