# RFM 客群與沈睡 VIP 召回監控儀表板

依 **動態儀表板藍圖_RFM沈睡VIP.md** 與 **Streamlit_App_Generator_Prompt.md** 實作之 Streamlit 動態儀表板。

## 資料來源

- 讀取同層級 `../02數據分析/` 之：
  - `rfm_segment_summary.csv`（客群摘要）
  - `sleep_vip_list.csv`（沈睡 VIP 名單）

請先執行 `02數據分析/rfm_analysis_online_retail.py` 產出上述 CSV，再啟動本儀表板。

## 安裝與執行

本儀表板使用 **repo 根目錄** 的 `pyproject.toml` 與虛擬環境，請在根目錄安裝依賴並執行。

### 使用 uv（推薦）

```bash
# 在專案根目錄 (Data_analysis)
cd "C:\Users\Elvis\git\Data_analysis"

# 安裝依賴（若尚未執行過）
uv sync

# 執行儀表板（指定 app.py 路徑）
uv run streamlit run "AI 數據分析工作坊/上課用prompt/儀錶板系統上線_streamlit/app.py"
```

### 使用 pip

```bash
# 在專案根目錄 (Data_analysis) 啟動虛擬環境後：
cd "C:\Users\Elvis\git\Data_analysis"
.venv\Scripts\activate
streamlit run "AI 數據分析工作坊/上課用prompt/儀錶板系統上線_streamlit/app.py"
```

瀏覽器會開啟本機位址（預設 http://localhost:8501）。

## 功能摘要

- **KPI 卡片**：有效客戶數、總營收、沈睡 VIP 人數／營收佔比／平均客單價
- **圖表**：客群人數 vs 營收佔比（分組柱狀）、營收與平均客單價（組合圖）、樣本漏斗、營收構成環圈圖、沈睡 VIP vs 一般流失條形圖
- **側欄篩選**：客群多選、名單排序（營收／Recency）、名單顯示筆數（50／100／200／全部）
- **沈睡 VIP 名單表**：可排序、可下載 CSV
