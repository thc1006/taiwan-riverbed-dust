# 濁水溪河床揚塵，真的吹到下風處了嗎？

冬季濁水溪裸露河床揚塵是台灣中部熟知的空品問題，文獻上卻幾乎空白。本專案用環境部逐時測站
資料實測它。主結果顯著（p = 0.0001），然後被三道事前寫好的防線推翻，是一份誠實的否定。

![negative control](figures/fig1_negative_control_fires.png)

## 識別策略：同一小時、跨測站

同一小時內，比較位於河床下風與非下風的測站 PM10，再扣掉各測站基準。東北季風、境外傳輸、季節、
全台性汙染事件同一小時打在所有測站上，因此被小時內比較差分掉。同一個測站在不同小時會在下風
與非下風之間切換，自己就是自己的對照組。

## 結果：三道防線同時觸發

資料為 2025-12-01 到 2026-02-25，32 個測站，48,890 筆逐時觀測。

| 檢驗 | 結果 | 判讀 |
|---|---|---|
| 粗顆粒 PM10−PM2.5（主結果） | +0.65 µg/m³，p = 0.0001 | 顯著 |
| PM2.5 陰性對照 | +0.55，p < 0.0001 | 揚塵是粗顆粒，PM2.5 卻漲得幾乎一樣多 |
| 北移 25 km 假來源 | +0.73，高於真來源的 0.65 | 非河床的假點，效果反而更強 |
| 風速機制 | 低風 +0.91、高風 +0.32（p = 0.42） | 方向完全相反（揚塵需要風力抬升） |

![placebos](figures/fig2_placebos_and_mechanism.png)

## 真正的混淆：順風向的空間梯度

小時固定效果拿掉的是區域平均水準，拿不掉沿著風向的空間梯度。東北季風下，河床下風的測站同時
也是全島上游都市與工業源、以及境外傳輸的下風，「下游什麼都比較髒」會偽裝成揚塵訊號。粗顆粒
指標和小時固定效果都攔不住它，只有陰性對照與位移安慰劑攔得住。效應量本身也很小（約粗顆粒
均值的 3%）。「事件太稀少被平均掉」這個辯解也被機制檢驗擋掉：強風時段正是揚塵該最明顯的地方，
那裡卻什麼都沒有。

## 怎麼跑

```bash
uv venv --python 3.12 && source .venv/bin/activate
uv pip install -r requirements.txt
python run.py
```

免金鑰。首次執行抓約 14 萬筆逐時資料（可中斷續抓）。

## 資料來源（全開放）

環境部 [`aqx_p_488`](https://data.moenv.gov.tw/dataset/detail/aqx_p_488)：逐時測站空品，含 PM10、
PM2.5、風速、風向、經緯度。金鑰取得、日期分頁的雷、下風判定與紀律聲明見 [NOTES.md](NOTES.md)。

## 本系列

同一套混淆稽核工法，套用在不同題目上，四個誠實的案例、四種不同的推論失敗：

- [taiwan-solar-dimming](https://github.com/thc1006/taiwan-solar-dimming) — 光電 × 氣膠，季節同步
- [taiwan-earthquake-fab](https://github.com/thc1006/taiwan-earthquake-fab) — 地震 × 晶圓廠，檢定力不足、測不到
- **taiwan-riverbed-dust**（本專案）— 河床揚塵 × PM10，順風向空間梯度
- [taiwan-vre-drought](https://github.com/thc1006/taiwan-vre-drought) — 電網備轉 × 再生能源，會計恆等式

稽核清單見 [CONFOUND-AUDIT.md](CONFOUND-AUDIT.md)。
