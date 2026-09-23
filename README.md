# 🌤️ Taiwan Weather Dashboard (台灣天氣預報儀表板)
> AI × Data × 氣象 × 實作

利用中央氣象署（CWA）Open Data API，結合 Python 資料處理、SQLite 資料庫與 Streamlit，打造動態互動式台灣天氣儀表板。

---

## 📌 專案目標

- 串接 CWA Open Data API (F-C0032-001) 取得即時氣象資料
- 使用 Pandas 進行資料清理、轉化與結構化
- 以 SQLite 儲存與管理氣象預報資料 (`data/data.db`)
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
│   └── data.db           # 本地 SQLite 資料庫
├── myplan/               # 專案流程與設計文件
│   ├── myworkflow.md     # 24堂課實作路線圖
│   ├── workflow.md       # 系統執行與架構流程圖
│   └── design.md         # 系統設計文件
├── assets/               # 圖片、靜態資源
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
| `pandas` | 資料整理、剖析與結構化 |
| `sqlite3` | 本地 SQLite 資料庫儲存與 SQL 查詢 |
| `streamlit` | 互動式 Web App 儀表板架構 |
| `folium` / `streamlit-folium` | 台灣地圖動態視覺化 |
| `plotly` | 高低溫雙軸折線圖與降雨機率圖 |

---

## 🚀 快速開始

### 1. 安裝套件

```bash
pip install -r requirements.txt
```

### 2. 設定 API Key

建立 `.env` 檔案並填入您的 CWA API Key (或於 Web App 側邊欄直接輸入)：

```bash
CWA_API_KEY="CWA-223C5412-50E5-418B-89EE-B6C402197BF8"
```

### 3. 啟動 Web App

```bash
streamlit run app/main.py
```

---

## 📊 功能進度 CheckList

- [x] 專案架構建立
- [x] CWA API 資料取得 (F-C0032-001)
- [x] JSON 解析 & Pandas 結構化整理
- [x] SQLite 資料庫自動建表與 Upsert 寫入 (`data.db`)
- [x] Streamlit 高質感暗色系介面設計
- [x] Plotly 雙軸氣溫折線圖（最高/最低溫）
- [x] 下拉選單選擇地區與縣市篩選
- [x] Folium 台灣地圖動態氣溫標示
- [x] 完整 Dashboard 整合與 CSV 數據匯出

---

## 📚 課程參考

本專案依照「煥哥 AI × Data 24堂課」學習路線實作：

1. 課程介紹 & 學習地圖
2. 台灣天氣與生活
3. 中央氣象署 CWA API
4. API 資料取得（requests）
5. JSON 資料解析
6. 提取最高 / 最低氣溫
7. 資料整理與預覽（Pandas）
8. 建立 SQLite 資料庫
9. 資料庫設計
10. 查詢資料驗證
11. Streamlit 入門
12. 從資料庫讀取資料
13. 下拉選單選擇地區
14. 繪製折線圖
15. 顯示資料表格
16. 整合 Web App 介面
17. 進階：台灣地圖視覺化（Folium）
18. 選擇日期顯示地圖
19. 完整成果展示
20. 程式品質與優化
21. 專案上傳至 GitHub
22. 延伸應用與想法
23. 回顧與重點整理
24. 下一步：繼續探索

---

## 🙌 作者

學習自「煥哥」—— *技術可以解決問題，但更重要的是用技術創造更好的未來！*

---

> **AI for Learning, AI for a Better Taiwan** 🇹🇼
