# 🌤️ Taiwan Weather Dashboard (台灣天氣預報儀表板)
> AI × Data × 氣象 × 實作

利用中央氣象署（CWA）Open Data API，結合 Python 資料處理、SQLite 資料庫與 Streamlit，打造動態互動式台灣天氣儀表板。

---

## 🚦 五關卡開發進度追蹤 (Five-Gate Tracker)

| 關卡 (Gate) | 名稱 (Name) | 狀態 (Status) | 說明 (Description) |
|------------|-------------|--------------|-------------------|
| **Gate 1** | API Data Ingestion | **PASS ✅** | 成功使用 `gate1_fetch.py` 串接 CWA API 抓取全台氣象 JSON 並輸出至 `gate1_output.json` |
| **Gate 2** | Database Storage | **PASS ✅** | 成功建立 `gate2_database.py`，使用 `INSERT OR REPLACE` 與 `UNIQUE(location_name, forecast_start)` 將預報紀錄載入 SQLite (`data/data.db`) |
| **Gate 3** | Local Taiwan GIS Web | **PASS ✅** | 使用 Streamlit + Folium + OpenStreetMap 呈現全台 GIS 地圖、氣溫顏色標示與資訊彈窗 |
| **Gate 4** | Weather Visual Analytics | **PASS ✅** | Plotly 雙軸最高/最低氣溫折線圖、降雨機率柱狀圖與衛星/雷達圖資展示 |
| **Gate 5** | Automated Crawler & Deployment | **PASS ✅** | 獨立每日自動爬蟲 `crawler.py` 搭配隱私金鑰 `.env` 與 GitHub 儲存庫同步 |

---

## 📌 專案目標

- 串接 CWA Open Data API (F-C0032-001) 取得即時氣象資料
- 使用 `gate1_fetch.py` 與 `gate2_database.py` 實現高可靠性 ETL Pipeline
- 以 SQLite 儲存與管理氣象預報資料 (`data/data.db` / `data/weather_database.db`)
- 使用 Streamlit 建立互動式 Web App 儀表板
- 整合 Folium 實現台灣各縣市氣溫分佈地圖視覺化
- 使用 Plotly 繪製高低溫雙軸趨勢圖與降雨機率柱狀圖

---

## 🗂️ 專案結構

```
0923/
├── app/                  # Streamlit Web App 主程式與元件
│   ├── main.py           # 應用程式入口
│   ├── components/       # UI 元件 (charts.py, map.py)
│   └── utils/            # 功能模組 (cwa_api.py, db_helper.py)
├── data/                 # SQLite 資料庫 & 原始資料
│   ├── data.db           # 本地 SQLite 主資料庫
│   └── weather_database.db # Gate 2 標準 SQLite 資料庫
├── myplan/               # 專案流程與設計文件
│   ├── myworkflow.md     # 24堂課實作路線圖
│   ├── workflow.md       # 系統執行與架構流程圖
│   └── design.md         # 系統設計文件
├── gate1_fetch.py        # Gate 1: CWA API 資料抓取腳本
├── gate2_database.py     # Gate 2: SQLite 資料庫處理與驗證腳本
├── crawler.py            # 每日獨立自動爬蟲腳本
├── gate1_output.json     # Gate 1 擷取之原始氣象 JSON 數據
├── .env                  # 個人 API Key 設定 (不推送到 GitHub)
├── .env.example          # 環境變數範例檔
├── requirements.txt      # Python 套件需求清單
└── README.md             # 專案說明文件
```

---

## 🧰 技術棧

| 技術 | 用途 |
|------|------|
| `requests` | 呼叫 CWA API 取得 JSON 預報資料 |
| `pandas` | 資料整理、剖析、結構化與 SQL SELECT 驗證 |
| `sqlite3` | 本地 SQLite 資料庫儲存與 SQL 查詢 (`INSERT OR REPLACE`) |
| `streamlit` | 互動式 Web App 儀表板架構 |
| `folium` / `streamlit-folium` | 台灣地圖動態視覺化 |
| `plotly` | 高低溫雙軸折線圖與降雨機率圖 |

---

## 🚀 快速開始

### 1. 安裝套件

```bash
pip install -r requirements.txt
```

### 2. 執行 Gate 1 & Gate 2 流程

```bash
# 1. 抓取 API 資料
python gate1_fetch.py

# 2. 解析並寫入 SQLite 資料庫
python gate2_database.py
```

### 3. 啟動 Web App 觀測儀表板

```bash
streamlit run app/main.py
```

---

## 🙌 作者

學習自「煥哥」—— *技術可以解決問題，但更重要的是用技術創造更好的未來！*

---

> **AI for Learning, AI for a Better Taiwan** 🇹🇼
