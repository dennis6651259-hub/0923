# 🌤️ Taiwan Weather Dashboard (台灣天氣預報儀表板)
<img width="1282" height="809" alt="image" src="https://github.com/user-attachments/assets/6f3dd890-c6f9-4b5d-93e8-066a2b80afb2" />


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

