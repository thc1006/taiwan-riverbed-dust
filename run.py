"""端到端：抓環境部逐時空品 → 下風對比 + 三道防線 → 出圖與報告。

    uv run run.py          # 或 python run.py

首次執行會逐頁抓約 14 萬筆逐時測站資料（142 次請求，逐批落地、可中斷續抓）。
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from analyze import run as analyze_run
from make_figures import make_figures

DATA = Path("data/winter.csv")


def main() -> int:
    if not DATA.exists():
        print("抓取環境部逐時空品資料（免金鑰；逐批落地，可中斷續抓）…")
        subprocess.run([sys.executable, "fetch.py"], check=True)

    if not DATA.exists():
        print("資料抓取失敗，請重跑（fetch.py 會從中斷處續抓）")
        return 1

    analyze_run(str(DATA))

    figs = make_figures(str(DATA))
    print("\n圖已輸出：")
    for p in figs:
        print(f"  {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
