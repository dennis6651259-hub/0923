# 📐 專案系統設計文件 (design.md)

> **專案名稱**: 台灣氣象預報 AI × Data 儀表板 (`Taiwan Weather Dashboard`)  
> **文件版本**: v1.0.0  
> **更新日期**: 2026-09-23  
> **作者**: 煥哥 AI × Data 實作小組

---

## 1. 🎯 系統概述 (System Overview)

本專案旨在建構一個自動化、資料驅動的**台灣氣象動態儀表板 Web 應用程式**。系統自動從**中央氣象署 (CWA) Open Data API** 擷取全台各縣市一週天氣預報，經由 Python 進行數據清洗與結構化，儲存至 SQLite 本地資料庫，最終透過 **Streamlit** 與 **Folium** 呈現互動式的視覺化儀表板與地圖。

---

## 2. 🏗️ 系統架構圖 (System Architecture)

```mermaid
graph TD
    subgraph 外部資料源 (External Data)
        CWA[中央氣象署 CWA Open Data API]
    end

    subgraph 後端資料管道 (Data Pipeline)
        Fetcher[API 資料擷取器<br/>requests]
        Parser[JSON 解析與轉化器<br/>json / pandas]
        Cleaner[資料清理與正規化模組<br/>Pandas]
        DB[SQLite 本地資料庫<br/>data.db]
    end

    subgraph 前端應用與視覺化 (Streamlit Web App)
        App[Streamlit 主程式<br/>app/main.py]
        Selector[控制器: 地區/日期選擇器]
        Chart[Plotly 折線圖: 氣溫趨勢]
        Table[Pandas 數據表格]
        Map[Folium 互動地圖: 全台氣溫]
    end

    CWA -->|HTTPS / JSON| Fetcher
    Fetcher --> Parser
    Parser --> Cleaner
    Cleaner -->|SQL Insert/Replace| DB
    DB -->|SQL Query| App
    App --> Selector
    Selector --> Chart
    Selector --> Table
    Selector --> Map
```

---

## 3. 🔄 資料流程設計 (Data Pipeline Design)

1. **資料擷取 (Fetch)**:
   - 使用 `requests.get()` 搭配 `Authorization` API Key 呼叫 CWA 預報 API（例如：全台各縣市未來 2 天 / 1 週預報）。
2. **解析與萃取 (Parse & Extract)**:
   - 解析多層 JSON，提取 `locations` -> `locationName` (縣市/區域) 以及 `weatherElement` 中的 `MinT` (最低溫) 與 `MaxT` (最高溫)。
3. **清洗與轉換 (Clean & Transform)**:
   - 將 ISO 時間字串轉為日期格式 (`YYYY-MM-DD`)。
   - 將數值型態轉為 `float` 或 `int`。
   - 建立統一的 DataFrame 結構：`[regionName, dataDate, minT, maxT]`。
4. **持久化儲存 (Persistence)**:
   - 自動連線至 `data/data.db`。
   - 執行 Upsert (插入或更新)，避免重複資料寫入。
5. **前端載入與呈現 (Render)**:
   - StreamlitApp 讀取 DB 後快取 (`@st.cache_data`)，提高使用者瀏覽順暢度。

---

## 4. 🗄️ 資料庫 Schema 設計 (Database Schema)

資料庫選用 **SQLite3**，檔案路徑為 `data/data.db`。

### 資料表：`TemperatureForecasts`

| 欄位名稱 (Column) | 資料型態 (Type) | 條件限制 (Constraints) | 說明 (Description) |
|-------------------|-----------------|------------------------|--------------------|
| `id`              | `INTEGER`       | PRIMARY KEY AUTOINCREMENT | 主鍵 ID |
| `regionName`      | `TEXT`          | NOT NULL               | 地區/縣市名稱 (例：北部地區、臺北市) |
| `dataDate`        | `TEXT`          | NOT NULL               | 預報日期 (`YYYY-MM-DD`) |
| `minT`            | `REAL`          | NOT NULL               | 最低氣溫 (℃) |
| `maxT`            | `REAL`          | NOT NULL               | 最高氣溫 (℃) |
| `created_at`      | `DATETIME`      | DEFAULT CURRENT_TIMESTAMP | 資料寫入時間 |

#### 唯一約束 (Unique Constraint)
- `UNIQUE(regionName, dataDate)`：防止同一地區同一天重複插入數據。

```sql
CREATE TABLE IF NOT EXISTS TemperatureForecasts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    regionName TEXT NOT NULL,
    dataDate TEXT NOT NULL,
    minT REAL NOT NULL,
    maxT REAL NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(regionName, dataDate)
);
```

---

## 5. 🧩 模組架構與程式碼組織 (Software Architecture)

```
0923/
├── app/
│   ├── __init__.py
│   ├── main.py              # Streamlit Web App 入口與 UI 排版
│   ├── components/          # UI 元件模組 (圖表、地圖、數據卡片)
│   │   ├── charts.py        # 折線圖與 Plotly 圖表元件
│   │   └── map.py           # Folium 地圖繪製元件
│   └── utils/
│       ├── cwa_api.py       # CWA API 串接與 JSON 解析邏輯
│       └── db_helper.py     # SQLite 資料庫 CRUD 操作封裝
├── data/
│   └── data.db              # SQLite 本地資料庫
├── myplan/
│   ├── myworkflow.md        # 24堂課實作工作流程路線圖
│   └── design.md            # 本系統設計文件
├── assets/                  # 靜態圖片與樣式
├── .gitignore               # Git 忽略設定
├── README.md                # 專案說明文件
└── requirements.txt         # 依賴套件清單
```

---

## 6. 🎨 前端 UI/UX 設計 (Streamlit UI Layout)

頁面採用響應式兩欄式/三欄式配置 (`st.columns`)：

```
+-------------------------------------------------------------------+
| 🌤️ 台灣天氣預報儀表板 (Taiwan Weather Dashboard)                  |
+-------------------------------------------------------------------+
| [側邊欄 Sidebar]                                                  |
| 1. 輸入/確認 CWA API Key                                          |
| 2. 選擇目標地區 (北部/中部/南部/東部/各縣市)                       |
| 3. 選擇預報日期 (Date Picker)                                     |
| 4. [按鈕] 立即更新資料庫                                          |
+------------------------------------+------------------------------+
| 主展示區 (Main Section)            | 地圖展示區                   |
| 📈 一週高低溫趨勢圖 (Plotly Chart) | 🗺️ 全台氣溫視覺化地圖 (Folium)|
|                                    |                              |
+------------------------------------+------------------------------+
| 📋 詳細氣溫預報數據表 (DataFrame)                                 |
+-------------------------------------------------------------------+
```

---

## 7. 🛡️ 例外處理與程式品質 (Error Handling & Code Quality)

1. **API 連線異常**:
   - 捕捉 `requests.exceptions.RequestException`，提供友善提示而非 crash。
   - API Key 無效時，前端呈現警告卡片 (`st.warning`) 導引使用者設定。
2. **資料庫連線管理**:
   - 使用 Context Manager (`with sqlite3.connect(...) as conn:`) 確保連線自動釋放與安全關閉。
3. **程式碼規範 (Clean Code)**:
   - 遵循 PEP 8 命名規範。
   - 所有 critical 函式皆包含 Type Hints 與 Docstrings。

---

## 8. 🚀 部署與擴充規劃 (Future Extensions)

- **自動化排程 (Cron/GitHub Actions)**: 定期每日更新 CWA 天氣資料。
- **Line Bot 推播通知**: 當預報低於特定溫度時，自動推播低溫特報。
- **AI 旅遊建議整合**: 結合 LLM (如 Gemini API) 依據天氣自動生成穿搭與行程建議。
