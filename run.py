"""项目入口：先加载 .env，再启动 tool_governance_demo。

用法：
    python run.py                                   # 离线演示（不需要密钥）
    python run.py --agent --input "查询订单 ord_1001"  # 真实 DeepSeek 闭环（需要 DEEPSEEK_API_KEY）

为什么需要这个文件：
    tool_governance_demo.py 只用 os.environ 读取配置（不依赖 python-dotenv），
    单独执行它不会解析 .env。这里统一做两件事：把 .env 注入进程环境变量、
    把 src/ 加进 sys.path（项目尚未打包，src 不是包）。
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from dotenv import load_dotenv  # noqa: E402

from tool_governance_demo import (  # noqa: E402
    parse_args,
    run_deepseek_agent,
    run_offline_demo,
)

# .env / .env.example 里的占位符前缀，用来给出比"请先设置环境变量"更清楚的提示。
PLACEHOLDER_PREFIXES = ("sk-your", "sk-替换")


def main() -> None:
    # override=False：真实 shell 环境变量优先于 .env，方便临时覆盖。
    load_dotenv(ROOT / ".env", override=False)
    args = parse_args()

    if not args.agent:
        asyncio.run(run_offline_demo())
        return

    api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not api_key or api_key.startswith(PLACEHOLDER_PREFIXES):
        raise SystemExit(
            "DEEPSEEK_API_KEY 还是占位符：请编辑 .env，把 sk-your-deepseek-api-key-here "
            "换成真实密钥，再运行 python run.py --agent"
        )
    asyncio.run(run_deepseek_agent(args.input))


if __name__ == "__main__":
    main()
