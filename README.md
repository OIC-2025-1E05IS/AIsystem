# KEIBA MONEY

競馬の購入金額・払戻金額を記録し、収支と回収率を自動計算するスマートフォン向けアプリです。Python + Kivyで作成し、データは端末内のSQLiteに保存します。

## 主な機能

- レース名・日付・購入金額・払戻金額の登録
- 収支（払戻金額 − 購入金額）の自動計算
- 総購入額・総払戻額・総収支・回収率の表示
- 登録履歴の一覧表示と削除
- SQLiteによるローカル保存
- ネイビー × ネオンブルー × パープルのホログラム風UI

## 動作環境

- Python 3.11以上
- Kivy 2.3以上
- Androidでの実機利用を想定。開発時はデスクトップでも起動できます。

## セットアップ

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS / Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

## テスト

Kivyの画面を起動せず、収支計算・入力検証・SQLite保存をテストできます。

```bash
python -m unittest discover -s tests -v
python -m compileall -q main.py keiba_money tests
```

## Androidビルドについて

Android APK化にはBuildozer等のAndroidビルド環境が別途必要です。現時点のCIはPythonの構文チェックとユニットテストを実行します。APK生成・実機操作の検証は未実施です。
