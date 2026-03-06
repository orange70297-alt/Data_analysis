## RFM 客群與沈睡 VIP 儀表板啟動說明（uv 虛擬環境版）

本說明假設你已經在 **專案根目錄 `C:\Users\Elvis\git\Data_analysis`** 用 **uv** 建立虛擬環境並安裝依賴（根目錄有 `pyproject.toml`，內含 `streamlit` 等套件）。

---

### 一、準備分析輸出資料（第一次或資料更新時）

儀表板會讀取 `案例A_Online_Retail_RFM/02數據分析` 產出的 CSV，因此先在根目錄執行 RFM 分析腳本：

```bash
cd "C:\Users\Elvis\git\Data_analysis"

# 使用 uv 在虛擬環境中執行 RFM 腳本（案例 A）
uv run python "案例A_Online_Retail_RFM/02數據分析/rfm_analysis_online_retail.py"
```

執行完成後，會在 `案例A_Online_Retail_RFM/02數據分析/` 產生：

- `rfm_segment_summary.csv`
- `sleep_vip_list.csv`

這兩個檔案是儀表板的主要資料來源。

---

### 二、啟動 Streamlit 儀表板（使用 .venv 的 streamlit.exe）

仍然在專案根目錄 `C:\Users\Elvis\git\Data_analysis` 下，執行：

```bash
cd "C:\Users\Elvis\git\Data_analysis"

# 第一次使用時先建立／同步虛擬環境（只需一次或依需求）
uv sync

# 透過 .venv 內的 streamlit.exe 啟動儀表板（案例 A）
.venv\Scripts\streamlit.exe run "案例A_Online_Retail_RFM\儀錶板系統上線_streamlit\app.py"
```

啟動後，Terminal 會顯示類似：

```text
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  # 或者是 8502、8503（依當下可用的連接埠）
```

請在瀏覽器前往對應的 Local URL，例如：

- `http://localhost:8501`
- 或 `http://localhost:8502`

即可看到：

- KPI 卡片（有效客戶、總營收、沈睡 VIP 指標）
- 客群人數 vs 營收佔比、營收與平均客單價、樣本漏斗、營收構成環圈圖
- 沈睡 VIP 名單（可排序、可下載 CSV）

---

### 三、啟動流程摘要（快速版）

1. 在根目錄產出分析資料（如有新資料或新 Dataset A 時）：
   ```bash
   cd "C:\Users\Elvis\git\Data_analysis"
   uv run python "案例A_Online_Retail_RFM/02數據分析/rfm_analysis_online_retail.py"
   ```
2. 啟動儀表板：
   ```bash
   cd "C:\Users\Elvis\git\Data_analysis"
   uv sync
   .venv\Scripts\streamlit.exe run "案例A_Online_Retail_RFM\儀錶板系統上線_streamlit\app.py"
   ```

兩個指令都在 `C:\Users\Elvis\git\Data_analysis` 執行，並共用同一個由 uv 管理的虛擬環境與 `.venv`。

