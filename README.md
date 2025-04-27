# Healthcare XML Converter

iPhoneの「ヘルスケアデータ」からエクスポートしたXMLデータをCSVファイルに変換するPythonスクリプトです。

## 機能

このスクリプトは以下の3つのカテゴリーのヘルスケアデータを処理します：

### 1. 栄養関連データ (healthcare_nutrition.csv)
- 消費カロリー
- 基礎代謝
- 体重
- 摂取カロリー
- 総脂肪摂取量
- タンパク質摂取量
- 炭水化物摂取量

### 2. 心拍・呼吸関連データ (healthcare_heartrate.csv)
- 心拍数
- 心拍変動
- 呼吸数
- 安静時心拍数
- 歩行時平均心拍数

### 3. 歩行関連データ (healthcare_walk.csv)
- 歩行速度
- 歩幅

## 必要条件

以下のPythonパッケージが必要です：
- xmltodict
- pandas
- pytz
- tqdm

## 使用方法

1. Apple HealthからエクスポートしたXMLファイルを`export.xml`という名前で保存します。
2. スクリプトを実行します：
```bash
python convert_health_xml.py
```

## 出力ファイル

スクリプトは以下の3つのCSVファイルを生成します：
- `healthcare_nutrition.csv`: 栄養関連データ
- `healthcare_heartrate.csv`: 心拍・呼吸関連データ
- `healthcare_walk.csv`: 歩行関連データ

各CSVファイルには以下の列が含まれます：
- datetime: 日時（日本時間、YYYY-MM-DD HH:MM:SS +0900形式）
- type: データタイプ（日本語）
- value: 測定値

## データ処理の特徴

- すべての日時は日本時間（Asia/Tokyo）に変換されます
- 栄養データは日付ごとに集計されます
- 体重データは日付ごとの最大値が記録されます
- その他の栄養データは日付ごとの合計値が記録されます 
