#! python3
import xmltodict
import pandas as pd
from datetime import datetime
import pytz
from tqdm import tqdm

# XMLファイルのパス
xml_file = "export.xml"

# XMLデータを開く
with open(xml_file, "r", encoding="utf-8") as file:
    data = xmltodict.parse(file.read())

# ヘルスケアデータの抽出
records = data["HealthData"]["Record"]

# カテゴリーごとのデータを格納するリスト
nutrition_data = []  # 栄養関連データ
heartrate_data = []  # 心拍・呼吸関連データ
walk_data = []      # 歩行関連データ

# データタイプの定義
NUTRITION_TYPES = [
    "HKQuantityTypeIdentifierActiveEnergyBurned",  # 消費カロリー
    "HKQuantityTypeIdentifierBasalEnergyBurned",   # 基礎代謝
    "HKQuantityTypeIdentifierBodyMass",            # 体重
    "HKQuantityTypeIdentifierDietaryEnergyConsumed",  # 摂取カロリー
    "HKQuantityTypeIdentifierDietaryFatTotal",     # 総脂肪摂取量
    "HKQuantityTypeIdentifierDietaryProtein",      # タンパク質摂取量
    "HKQuantityTypeIdentifierDietaryCarbohydrates"  # 炭水化物摂取量
]

HEARTRATE_TYPES = [
    "HKQuantityTypeIdentifierHeartRate",           # 心拍数
    "HKQuantityTypeIdentifierHeartRateVariabilitySDNN",  # 心拍変動
    "HKQuantityTypeIdentifierRespiratoryRate",     # 呼吸数
    "HKQuantityTypeIdentifierRestingHeartRate",    # 安静時心拍数
    "HKQuantityTypeIdentifierWalkingHeartRateAverage"  # 歩行時平均心拍数
]

WALK_TYPES = [
    "HKQuantityTypeIdentifierWalkingSpeed",        # 歩行速度
    "HKQuantityTypeIdentifierWalkingStepLength"    # 歩幅
]

# 型名を日本語に変換する辞書
type_to_japanese = {
    "HKQuantityTypeIdentifierActiveEnergyBurned": "消費カロリー",
    "HKQuantityTypeIdentifierBasalEnergyBurned": "基礎代謝",
    "HKQuantityTypeIdentifierBodyMass": "体重",
    "HKQuantityTypeIdentifierDietaryEnergyConsumed": "摂取カロリー",
    "HKQuantityTypeIdentifierDietaryFatTotal": "総脂肪摂取量",
    "HKQuantityTypeIdentifierDietaryProtein": "タンパク質摂取量",
    "HKQuantityTypeIdentifierDietaryCarbohydrates": "炭水化物摂取量",
    "HKQuantityTypeIdentifierHeartRate": "心拍数",
    "HKQuantityTypeIdentifierHeartRateVariabilitySDNN": "心拍変動",
    "HKQuantityTypeIdentifierRespiratoryRate": "呼吸数",
    "HKQuantityTypeIdentifierRestingHeartRate": "安静時心拍数",
    "HKQuantityTypeIdentifierWalkingHeartRateAverage": "歩行時平均心拍数",
    "HKQuantityTypeIdentifierWalkingSpeed": "歩行速度",
    "HKQuantityTypeIdentifierWalkingStepLength": "歩幅"
}

# データの分類と収集
for record in tqdm(records, desc="レコード処理中"):
    # 数値データのみを処理
    if "@value" not in record:
        continue
    try:
        value = float(record["@value"])
    except (ValueError, TypeError):
        continue  # 数値に変換できないデータはスキップ
    datetime_str = record["@startDate"]
    type_name = record["@type"]
    if type_name in NUTRITION_TYPES:
        nutrition_data.append({
            "datetime": datetime_str,
            "type": type_to_japanese[type_name],
            "value": value
        })
    elif type_name in HEARTRATE_TYPES:
        heartrate_data.append({
            "datetime": datetime_str,
            "type": type_to_japanese[type_name],
            "value": value
        })
    elif type_name in WALK_TYPES:
        walk_data.append({
            "datetime": datetime_str,
            "type": type_to_japanese[type_name],
            "value": value
        })

def process_dataframe(df):
    """データフレームの共通処理"""
    # datetimeをパースしてタイムゾーンを設定
    df["datetime"] = pd.to_datetime(df["datetime"])
    if not df["datetime"].dt.tz:
        df["datetime"] = df["datetime"].dt.tz_localize("UTC")
    df["datetime"] = df["datetime"].dt.tz_convert("Asia/Tokyo")
    
    # 日付でソート
    df = df.sort_values("datetime")
    
    # datetime列を指定された形式に変換
    df["datetime"] = df["datetime"].dt.strftime("%Y-%m-%d %H:%M:%S +0900")
    
    return df[["datetime", "type", "value"]]  # 必要なカラムのみを選択

# 栄養関連データの処理
if nutrition_data:
    df_nutrition = pd.DataFrame(nutrition_data)
    
    # 日付列を追加（集計用）
    df_nutrition["date"] = pd.to_datetime(df_nutrition["datetime"]).dt.date
    
    # 体重データと他の栄養データを分けて処理
    weight_data = []
    other_nutrition_data = []
    
    # 日付ごとにグループ化して処理
    for date, group in df_nutrition.groupby("date"):
        # datetimeをパース
        group["datetime_parsed"] = pd.to_datetime(group["datetime"])
        
        # 体重データの処理（最大値と、その時点のdatetime）
        weight_group = group[group["type"] == "体重"]
        if not weight_group.empty:
            max_weight_idx = weight_group["value"].idxmax()
            weight_data.append({
                "datetime": weight_group.loc[max_weight_idx, "datetime"],
                "type": "体重",
                "value": weight_group.loc[max_weight_idx, "value"]
            })
        
        # その他の栄養データの処理（合計値と、最終測定時点のdatetime）
        for type_name in set(group["type"]) - {"体重"}:
            type_group = group[group["type"] == type_name]
            if not type_group.empty:
                last_datetime = type_group.loc[type_group["datetime_parsed"].idxmax(), "datetime"]
                other_nutrition_data.append({
                    "datetime": last_datetime,
                    "type": type_name,
                    "value": type_group["value"].sum()
                })
    
    # 体重データとその他の栄養データを結合
    df_nutrition_processed = pd.DataFrame(weight_data + other_nutrition_data)
    
    if not df_nutrition_processed.empty:
        # datetimeの処理
        df_nutrition_processed = process_dataframe(df_nutrition_processed)
        df_nutrition_processed.to_csv("healthcare_nutrition.csv", index=False, encoding="utf-8-sig")
        print("healthcare_nutrition.csv を作成しました！")

# 心拍・呼吸関連データの処理
if heartrate_data:
    df_heartrate = pd.DataFrame(heartrate_data)
    df_heartrate = process_dataframe(df_heartrate)
    df_heartrate.to_csv("healthcare_heartrate.csv", index=False, encoding="utf-8-sig")
    print("healthcare_heartrate.csv を作成しました！")

# 歩行関連データの処理
if walk_data:
    df_walk = pd.DataFrame(walk_data)
    df_walk = process_dataframe(df_walk)
    df_walk.to_csv("healthcare_walk.csv", index=False, encoding="utf-8-sig")
    print("healthcare_walk.csv を作成しました！")
