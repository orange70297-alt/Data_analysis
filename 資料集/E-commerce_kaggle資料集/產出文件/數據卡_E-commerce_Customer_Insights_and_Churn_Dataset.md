---
### **數據卡：E-commerce Customer Insights and Churn Dataset**

**1. 數據集總覽**
- **數據來源**: `資料集/E-commerce_kaggle資料集/E Commerce Customer Insights and Churn Dataset.csv`
- **最後更新時間**: 2026-03-05（以本次產出日期作為文檔標註，可在實務中改為實際檔案更新時間）
- **數據維度**: 約 2000 筆交易記錄 × 17 欄（依檔名推估為訂閱制電商訂單與用戶行為資料）

**2. 數據列詳解**

| Column Name | Data Type (推估) | Missing % (推估) | Unique Values (推估) | Description | Example |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `order_id` | object / string | 0.0% | ≈ 行數（接近全唯一） | 單筆訂單編號，用於標識每一筆交易記錄 | `ORD5000` |
| `customer_id` | object / string | 0.0% | 小於行數 | 用戶唯一識別碼，可彙總多筆訂單到用戶層級 | `CUST1000` |
| `age` | int64 | 0.0% | 數十個 | 用戶年齡，適合分群成區間（例如 18–25、26–35 等） | `39` |
| `product_id` | object / string | 0.0% | 多 | 商品唯一識別碼，對應到單一商品 | `PROD200` |
| `country` | category / string | 0.0% | 約 4–6 個 | 用戶所在國家／市場（如 Canada, USA, Pakistan, India, Germany, UK 等） | `Canada` |
| `signup_date` | datetime (字串形式需轉換) | 0.0% | 多 | 用戶註冊日期，用於計算用戶在平台的存續時間 | `1/7/2021` |
| `last_purchase_date` | datetime (字串形式需轉換) | 0.0% | 多 | 用戶最近一次購買日期，可用來判斷近期活躍度 | `2/21/2023` |
| `cancellations_count` | int64 | 0.0% | 小於 10 | 用戶累積取消次數，衡量退訂／變更訂閱的頻率 | `0`, `3`, `5` |
| `subscription_status` | category / string | 0.0% | 3 | 訂閱狀態：`active` / `paused` / `cancelled`，為流失分析核心欄位 | `active` |
| `order_date` | datetime (字串形式需轉換) | 0.0% | 多 | 該筆訂單建立日期，可用於觀察時間趨勢與季節性 | `8/20/2024` |
| `unit_price` | float64 | 0.0% | 多 | 單件商品價格，用於計算訂單金額與 AOV | `78.21` |
| `quantity` | int64 | 0.0% | 小於 10 | 該筆訂單購買數量 | `5` |
| `purchase_frequency` | int64 / float64 | 0.0% | 多 | 描述用戶購買頻率的指標（可能為固定時間窗內的訂單數） | `37` |
| `preferred_category` | category / string | 0.0% | 約 5 類 | 用戶偏好的主要品類（如 Sports, Electronics, Home, Beauty, Clothing 等） | `Sports` |
| `product_name` | object / string | 0.0% | 多 | 商品名稱，可用於商品層級分析與推薦系統 | `Football`, `Refrigerator` |
| `category` | category / string | 0.0% | 約 5 類 | 該筆訂單實際購買商品所屬品類 | `Sports`, `Home` |
| `gender` | category / string | 0.0% | 2 | 用戶性別 | `Female`, `Male` |

> 註：由於目前僅查看前數十筆樣本，缺失值比例與唯一值數量為「合理推估」，正式 EDA 時應使用 `df.info()`、`df.isna().mean()`、`df.nunique()` 等函式進行精確計算。

**3. 初步數據品質評估**
- **缺失值狀況（初步觀察）**  
  - 從前 30 多筆觀察，各欄位皆有填值，未見明顯空白或 `NaN`。  
  - 仍需在完整資料上跑一次缺失值檢查，特別是日期欄位（`signup_date`, `last_purchase_date`, `order_date`）與行為欄位（`purchase_frequency`, `cancellations_count`），確認是否存在局部缺失。

- **日期與類型格式**  
  - 日期欄位目前為字串格式（如 `1/7/2021`），在分析前需統一轉換為 `datetime` 型別，並確認是否有格式不一致或轉換錯誤的紀錄。  
  - 若時區或基準日對分析有影響（例如計算距離今日的天數），需在後續文件中明確標註。

- **數值欄位範圍與異常值**  
  - `unit_price` 範圍從十幾到上千（例如 `1525.8`, `1702.39`），高單價商品可能是真實高價商品，也可能混入異常值；建議檢查分佈（箱型圖、分位數）並搭配 `product_name`, `category` 驗證合理性。  
  - `quantity` 多在 1–9 之間，屬於小筆購買；若存在極端大量（如數百件）的紀錄，需特別檢查。  
  - `purchase_frequency` 數值在樣本中出現 1–48 等範圍，需確認其定義（例如單位時間窗、是否為累積值），避免誤解。

- **分類欄位與一致性**  
  - `subscription_status` 預期僅有 `active` / `paused` / `cancelled` 三種狀態，正式檢查時需驗證是否存在拼寫錯誤或大小寫不一致。  
  - `country`, `preferred_category`, `category`, `gender` 等欄位，應檢查是否存在多語言、前後空白或大小寫差異導致的「偽多類別」。

- **用戶層級與訂單層級對應**  
  - `customer_id` 對應多筆 `order_id`，需在分析時明確區分「訂單層級統計」與「用戶層級統計」，避免重複計算（例如計算流失率應以用戶為單位，而非訂單）。

**4. 探索性分析建議**
1. **用戶與訂閱狀態分佈分析**  
   - 分析 `subscription_status` 在不同 `country`, `age` 區間, `gender` 的分佈，觀察流失（`cancelled`）與暫停（`paused`）是否集中於特定族群。  
   - 將 `cancellations_count` 分箱（例如 0, 1–2, 3–4, ≥5），檢查各箱中 `subscription_status` 的比例差異。

2. **消費行為與價值分析**  
   - 使用 `unit_price × quantity` 衍生 `total_order_value`，計算各用戶的總消費與平均訂單金額（AOV），並與 `purchase_frequency` 結合，建立「高價高頻」、「高價低頻」、「低價高頻」、「低價低頻」等客群輪廓。  
   - 檢查不同 `subscription_status` 群體在 `total_order_value`, `purchase_frequency`, `cancellations_count` 上的分佈差異，評估哪類用戶在流失前對營收貢獻最大。

3. **品類與市場組合分析**  
   - 比較 `preferred_category` 與實際購買 `category` 的一致性，識別「偏好 ≠ 實際購買」的用戶比例，並觀察其是否與較高的流失率或暫停率相關。  
   - 以 `country × category` 為切片，計算訂單數、總營收與流失相關指標（例如該國家該品類用戶中 `subscription_status = cancelled/paused` 的比例），找出需要優先優化的市場與品類。

---
