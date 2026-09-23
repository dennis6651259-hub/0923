# 🌤️ Taiwan Weather Dashboard
> AI × Data × 氣象 × 實作

利用中央氣象署（CWA）Open Data API，結合 Python 資料處理與 Streamlit，打造互動式台灣天氣儀表板。

---

## 📌 專案目標

- 串接 CWA Open Data API 取得即時氣象資料
- 使用 Pandas 進行資料清理與分析
- 以 SQLite 儲存歷史氣象資料
- 使用 Streamlit 建立互動式 Web App
- 整合 Folium 實現台灣地圖視覺化

---

## 🗂️ 專案結構

```
0923/
├── app/                  # Streamlit 主程式
│   └── main.py
├── data/                 # SQLite 資料庫 & 原始資料
│   └── data.db
├── assets/               # 圖片、靜態資源
├── requirements.txt      # 套件需求清單
└── README.md
```

---

## 🧰 技術棧

| 技術 | 用途 |
|------|------|
| `requests` | 呼叫 CWA API 取得 JSON 資料 |
| `pandas` | 資料整理與分析 |
| `sqlite3` | 本地資料庫儲存 |
| `streamlit` | 互動式 Web App |
| `folium` | 台灣地圖視覺化 |
| `plotly` | 折線圖 / 圖表呈現 |

---

## 🚀 快速開始

### 1. 安裝套件

```bash
pip install -r requirements.txt
```

### 2. 設定 API Key

前往 [CWA Open Data 平台](https://opendata.cwa.gov.tw/) 申請 API Key，並設定環境變數：

```bash
export CWA_API_KEY="your_api_key_here"
```

### 3. 啟動 App

```bash
streamlit run app/main.py
```

---

## 📊 功能規劃

- [x] 專案架構建立
- [ ] CWA API 資料取得
- [ ] JSON 解析 & Pandas 整理
- [ ] SQLite 資料庫儲存
- [ ] Streamlit 基本介面
- [ ] 折線圖（最高/最低溫）
- [ ] 下拉選單選擇地區
- [ ] Folium 互動地圖
- [ ] 完整 Dashboard 整合

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
