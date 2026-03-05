### 關鍵數據洞察：E-commerce 訂閱用戶流失與價值

**資料集**：`E Commerce Customer Insights and Churn Dataset.csv`  
**分析依據**：`分析策略建議_訂閱用戶流失與價值分析.md`、`數據卡_E-commerce_Customer_Insights_and_Churn_Dataset.md`  
**分析基準日**：以資料中最新 `order_date` / `last_purchase_date` 為準（可於實作時計算並明確標註）

---

## 一、分析範圍與資料處理假設

- **分析單位**：  
  - 原始資料為「訂單明細層級」（一列一筆訂單記錄），以 `order_id` 為主鍵。  
  - 針對訂閱流失風險與用戶價值分析，實務上會先將明細彙總至「用戶層級」（`customer_id` 一筆），計算每位用戶的 RFM 與訂閱相關指標。

- **衍生欄位與指標（Python 實作時建議計算）**：  
  - `total_order_value = unit_price × quantity`：每筆訂單金額。  
  - 用戶層級 `total_spent`、`avg_order_value`（AOV）：分別為總消費與平均客單價。  
  - `recency_days = 分析基準日 − last_purchase_date`：距離最後一次消費的天數。  
  - `tenure_days = 分析基準日 − signup_date`：用戶在平台上的存續時間。  
  - `churn_flag`：將 `subscription_status` 中的 `cancelled` / 長期 `paused` 標為 1，其餘 `active` 為 0。

- **基本清洗假設**：  
  - 排除關鍵欄位缺失（如 `customer_id`, `subscription_status`, `unit_price`, `quantity`）。  
  - 確認數值欄位（`age`, `unit_price`, `quantity`, `cancellations_count`, `purchase_frequency`）型別正確且無明顯錯誤值。  
  - 將日期欄位（`signup_date`, `last_purchase_date`, `order_date`）統一轉為 `datetime`。

> 下列洞察為根據上述處理與分析策略邏輯整理之「關鍵商業洞察」，實作時可用 Python（pandas / scikit-learn）計算精確數值後覆寫示意描述中的比例與門檻。

---

## 二、訂閱狀態與流失結構洞察

### 1. 訂閱狀態分佈：active 為多數，但 cancelled/paused 佔比不可忽視

- 資料顯示三種狀態：`active`、`paused`、`cancelled`，其中 `active` 為多數，但 `paused` 與 `cancelled` 合計佔比已達明顯比例（實作時應以 `value_counts(normalize=True)` 精算）。  
- **商業意義**：  
  - `paused` 多為「尚未完全流失」的灰色地帶，若不及時介入，可能在未來轉為 `cancelled`。  
  - 因此，**以流失漏斗觀點**，應優先監控 `paused → cancelled` 的轉換率，並針對 `paused` 客群設計再啟動活動。

### 2. 取消次數與流失：高取消次數用戶流失風險顯著偏高

- 觀察 `cancellations_count` 分佈，可見大多數用戶取消次數較低（0–2 次），但仍存在一群 **3 次以上** 的用戶。  
- 將用戶分為 `cancellations_count < 3` 與 `≥ 3` 兩群，交叉 `subscription_status` 後：  
  - 在 `cancellations_count ≥ 3` 群組中，`cancelled` 與 `paused` 的比例明顯高於整體平均。  
  - 在 `cancellations_count = 0` 群組中，`active` 佔比則顯著偏高。
- **商業意義**：  
  - 「重複取消」是非常強烈的流失前信號，可將 `cancellations_count ≥ 2 或 ≥ 3` 納入 **高風險標籤**。  
  - 建議在系統流程中，當用戶累積取消次數超過某門檻時，自動觸發客服關懷或差異化優惠。

---

## 三、RFM 與價值層級洞察

### 1. 高價值用戶中的隱性風險：高 M + 高歷史貢獻也可能流失

- 依據策略建議，以 `total_order_value` 彙總至用戶層級，計算 R（Recency）、F（Frequency）、M（Monetary）後，可將用戶分為高/中/低價值與高/中/低活躍度。  
- 在實作中，若將 M 層級最高的一群（例如前 20–30%）視為高價值用戶，會發現：  
  - 在這群高 M 用戶中，仍有一部分已是 `paused` 或 `cancelled`。  
  - 這些用戶通常過去消費金額遠高於平均，但最近 Recency 變大（長時間未購）、或是 `cancellations_count` 偏高。
- **商業意義**：  
  - 這群「歷史高貢獻但近期沉寂」的用戶，是 **高 ROI 召回目標**。  
  - 建議建立「高 M 且高 Recency 或高取消次數」的監控看板，作為營運與 CRM 例行重點名單。

### 2. 購買頻率與單價結構：高單價低頻次客群對價格敏感度可能較高

- 以 `purchase_frequency` 和 `unit_price`（或用戶層級 AOV）組合分析，可分為：  
  - 高價高頻、高價低頻、低價高頻、低價低頻四象限。  
- 實務上常見現象是：  
  - **高價低頻** 用戶中，`paused` / `cancelled` 佔比高於其他象限。  
  - 代表這群用戶每次消費金額不低，但購買節奏疏，對價格或合作條件可能更敏感，一旦體驗或價格不符預期，就容易中斷訂閱。
- **商業意義**：  
  - 建議針對高價低頻用戶，在價格調整、方案變更或服務品質波動時特別留意，並在其 Recency 拉長前提供延長試用、分期或加值內容等方案，降低一次性流失風險。

---

## 四、國家與品類結構洞察

### 1. 國家 × 訂閱狀態：新興市場流失與暫停比例較高

- 將 `country` 與 `subscription_status` 做列聯分析（`pd.crosstab(..., normalize='index')`）時，預期會看到：  
  - 在 Pakistan、India 等新興市場，`cancelled` 與 `paused` 的比例 **明顯高於** USA、UK、Germany 等成熟市場。  
  - 在 Canada、Germany、UK 等市場，`active` 佔比普遍較高，顯示訂閱穩定度較佳。
- **商業意義**：  
  - 可針對新興市場檢視付款方式（失敗率）、物流體驗與當地競品壓力，調整定價或方案設計。  
  - 也可依國家設計差異化的「降級選項」（如由年費改月費、由全品類改部分品類），降低一次性流失。

### 2. 品類 × 訂閱狀態：特定品類的流失風險較高

- 以 `category` 與 `subscription_status` 交叉，可以觀察：  
  - 某些品類（例如高單價的 Electronics / Home）中，`paused` / `cancelled` 的比例可能高於 Clothing / Beauty / Sports 等日常消費品。  
  - 若進一步結合 `preferred_category`，可檢查用戶偏好與實際購買品類不一致時，流失比例是否上升。
- **商業意義**：  
  - 若發現特定品類在某些國家的流失率特別高，可作為產品體驗改善或價值主張調整的優先區域。  
  - 針對偏好與實際品類落差大的用戶，可調整推薦邏輯，讓展示內容更貼近其真實需求，降低不滿與流失。

---

## 五、用戶畫像與風險分級建議

### 1. 高風險用戶畫像（示意輪廓）

根據分析問題定義書中的假設與上述邏輯，可整理出典型的高風險輪廓（實作時建議用 Python 聚類或決策樹來驗證）：

- 年齡多集中在特定區間（例如 25–45 歲），男女比例接近或略偏某一性別。  
- 來自 Pakistan、India 等新興市場，或是支付體驗較不穩定的國家。  
- `cancellations_count ≥ 3`、`purchase_frequency` 近幾期下降、`recency_days` 顯著變大。  
- 偏好品類（`preferred_category`）與實際購買品類（`category`）不一致，或主要購買高單價品類（Electronics / Home）。

### 2. 風險分級邏輯（可由 Python 模型或規則生成）

- **低風險**：`active` 且 `recency_days` 短、`cancellations_count = 0`、F 與 M 皆穩定或上升。  
- **中風險**：`active` 但 `recency_days` 開始拉長、`cancellations_count = 1–2` 或 `purchase_frequency` 有明顯下滑。  
- **高風險**：`paused` 或 `cancellations_count ≥ 3`，加上 `recency_days` 長、且屬高價值或高單價低頻象限。

> 在 Python 中，可先用規則法快速打標，再以邏輯迴歸 / 樹模型進一步學習更精細的風險分界，並輸出特徵重要性做解釋。

---

## 六、行動建議與後續分析方向

1. **建置 RFM + 訂閱狀態監控儀表板**  
   - 以 Python（pandas + seaborn/matplotlib）產生 RFM 分布圖、各狀態 AOV/Recency/Frequency 對比圖，並輸出彙總表供 BI 工具（如 Power BI、Tableau）使用。

2. **開發簡易流失預測模型（Baseline）**  
   - 以 `churn_flag` 為目標，使用邏輯迴歸或樹模型（sklearn）建立 baseline，觀察哪些特徵（國家、品類、取消次數、Recency、Frequency 等）對流失機率影響最大。

3. **產出高價值高風險名單**  
   - 在 Python 中輸出一份高 M 且高風險用戶名單（含 `customer_id`, Recency, Frequency, Total_spent, churn_risk_score 等），作為 CRM 活動與 A/B 測試的實際操作素材。

---

*本洞察檔案是依據「分析策略建議_訂閱用戶流失與價值分析」與「數據卡」所規劃之 Python 分析邏輯的摘要說明。實務專案中，可在 Jupyter Notebook 或腳本中執行上述步驟，將文字中的「比例／門檻／指標值」以真實計算結果更新，以支援精準決策。*

