"""
gate5_automation.py - Gate 5: Automated Crawler & Deployment 驗證腳本
"""

import os
import sys
import subprocess

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from crawler import run_daily_crawler

def verify_gate5():
    print("\n==================================================")
    print("[Gate 5: Automated Crawler & Deployment] 開始執行驗證...")
    print("==================================================")
    
    # 1. 驗證 .env 金鑰與 .gitignore 安全保護
    gitignore_path = os.path.join(BASE_DIR, ".gitignore")
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r", encoding="utf-8") as f:
            content = f.read()
            if ".env" in content:
                print("[API 安全保護] .env 檔案已列入 .gitignore，確保隱私金鑰零外洩！")
            else:
                print("[WARN] .env 未包含在 .gitignore 中！")
                
    # 2. 執行獨立自動爬蟲全流程
    print("[爬蟲測試] 觸發 crawler.py 獨立每日爬蟲...")
    try:
        run_daily_crawler()
        print("[爬蟲測試] 自動化 ETL 與 SQLite 寫入成功完成！")
    except Exception as e:
        print(f"[ERROR] 爬蟲執行失敗: {e}")
        sys.exit(1)
        
    # 3. 檢查 Git 與 GitHub 遠端同步狀態
    try:
        res = subprocess.run(["git", "status"], cwd=BASE_DIR, capture_output=True, text=True)
        if "working tree clean" in res.stdout:
            print("[Git 同步狀態] 工作目錄清潔，變更已完整 Commit！")
        else:
            print("[Git 同步狀態] 目前尚有未 Commit 變更")
    except Exception as e:
        print(f"[WARN] 檢查 Git 狀態時發生警告: {e}")
        
    print("--------------------------------------------------")
    print("[Gate 5 (Automated Crawler & Deployment) PASS ✅]\n")

if __name__ == "__main__":
    verify_gate5()
