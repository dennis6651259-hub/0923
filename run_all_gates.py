"""
run_all_gates.py - 執行五關卡 (Gate 1 ~ Gate 5) 全自動終端驗證
"""

import sys
import os

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from gate1_fetch import fetch_and_save_gate1
from gate2_database import process_gate2
from gate3_gis import verify_gate3
from gate4_analytics import verify_gate4
from gate5_automation import verify_gate5

def run_all():
    print("\n🚀 ==================================================")
    print("🚀 [Five-Gate Pipeline] 開始全自動終端驗證流程 (Gate 1 ~ Gate 5)")
    print("🚀 ==================================================\n")
    
    # Gate 1
    fetch_and_save_gate1()
    
    # Gate 2
    process_gate2()
    
    # Gate 3
    verify_gate3()
    
    # Gate 4
    verify_gate4()
    
    # Gate 5
    verify_gate5()
    
    print("\n==================================================")
    print("🎉 ALL FIVE GATES PASSED! (Gate 1 ~ Gate 5 100% 完成)")
    print("==================================================")
    print("  ✅ Gate 1: API Data Ingestion - PASS")
    print("  ✅ Gate 2: Database Storage - PASS")
    print("  ✅ Gate 3: Local Taiwan GIS Web - PASS")
    print("  ✅ Gate 4: Weather Visual Analytics - PASS")
    print("  ✅ Gate 5: Automated Crawler & Deployment - PASS")
    print("==================================================\n")

if __name__ == "__main__":
    run_all()
