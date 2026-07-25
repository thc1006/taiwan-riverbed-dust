# 貢獻指南 · Contributing

這是一份誠實的否定結果，也是一次空間混淆稽核的示範。歡迎你來挑戰它。

## 最歡迎的兩種貢獻

- **戳破稽核**：如果你發現下風判定、PM2.5 陰性對照、位移安慰劑或風速機制有漏洞，
  或效應其實站得住，請告訴我。這個專案的重點，就是一個看似顯著的下風訊號，
  能不能撐過這幾道防線。
- **更好的資料**：更長的窗口、河川流量序列，或實地記錄過的揚塵事件，
  都能讓這題問得更清楚。

## 跑起來

```bash
uv venv --python 3.12 && source .venv/bin/activate
uv pip install -r requirements.txt
python run.py
```

免金鑰。首次執行會逐頁抓約 14 萬筆逐時測站資料（可中斷續抓）。

## 幾點約定

- 改動分析時，請一併說明它如何影響結論，並盡量附上可重現的數字。
- 分析門檻請在看到結果前就定好；若要做探索性分析，請明確標示，不要事後挑到顯著為止。
- 程式風格對齊現有檔案；中文排版遵循
  [中文文案排版指北](https://github.com/sparanoid/chinese-copywriting-guidelines)。
- 想先討論就開一個 [issue](https://github.com/thc1006/taiwan-riverbed-dust/issues)。

這是一個由一人維護的小型研究專案，回覆可能需要一點時間，先謝謝你的耐心。
參與本專案即表示你同意遵守[行為準則](CODE_OF_CONDUCT.md)。
