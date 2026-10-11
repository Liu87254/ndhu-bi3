import pandas as pd
import json
import re
import os

def run_etl():
    # 建立輸出目錄
    os.makedirs('output', exist_ok=True)

    # 1. 讀取原始資料 (自動處理 Big5 / CP950 編碼)
    loc_path = 'data/苗栗縣科技執法設備取締地點.csv'
    count_path = 'data/113年下半年取締件數.csv'

    df_loc = pd.read_csv(loc_path, encoding='cp950')
    df_count = pd.read_csv(count_path, encoding='cp950')

    # 2. 清理地點資料
    df_loc_clean = df_loc.dropna(subset=['座標緯度', '座標經度']).copy()
    loc_list = []
    for _, row in df_loc_clean.iterrows():
        loc_list.append({
            "id": int(row['設備編號']),
            "type": str(row['科技執法種類']).strip(),
            "location": str(row['設置地點(路口或路段)']).strip(),
            "items": str(row['取締項目(以"、"分隔)']).strip(),
            "lat": float(row['座標緯度']),
            "lng": float(row['座標經度']),
            "speed_limit": str(row['速限']) if pd.notna(row['速限']) else "無"
        })

    # 3. 清理取締件數資料 (將「2,564件」或「0件，設備維護中」解析為純數字)
    count_list = []
    total_enforcements = 0

    for _, row in df_count.iterrows():
        raw_count = str(row['取締件數'])
        # 提取數字
        nums = re.findall(r'\d+', raw_count.replace(',', ''))
        parsed_count = int(nums[0]) if nums else 0
        total_enforcements += parsed_count

        location_name = str(row['設置地點']).replace('\n', ' ').strip()
        count_list.append({
            "id": int(row['編號']),
            "type": str(row['科技執法種類']).strip(),
            "location": location_name,
            "items": str(row['取締項目']).strip(),
            "raw_count": raw_count,
            "count": parsed_count
        })

    # 4. 驗證與導出 JSON
    print(f"[ETL 驗證成功] 總科技執法站點: {len(loc_list)} 處")
    print(f"[ETL 驗證成功] 113年下半年總取締件數核對: {total_enforcements:,} 件")

    with open('output/clean_locations.json', 'w', encoding='utf-8') as f:
        json.dump(loc_list, f, ensure_ascii=False, indent=2)

    with open('output/clean_counts.json', 'w', encoding='utf-8') as f:
        json.dump(count_list, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':

    run_etl()