# ポモドーロタイマーWebアプリ 段階的実装計画

## 1. プロジェクト初期セットアップ
- ディレクトリ構成の作成（static, templates, routes, services, tests など）
- 必要ファイルの雛形作成（app.py, requirements.txt, README.md など）

## 2. タイマーUIの最小実装
- index.html, style.css でタイマーUI作成
- timer.js でカウントダウンロジック
- 開始・停止・リセットボタン

## 3. Flaskバックエンド構築
- app.py でFlaskアプリの基本構造
- / ルートでテンプレート表示

## 4. タイマー状態管理API
- REST API（/api/timer）で状態取得・更新
- routes/timer_routes.py, services/timer_service.py でロジック分離

## 5. フロントエンドとバックエンド連携
- JavaScriptからFetch APIで状態取得・更新
- 非同期通信の実装

## 6. 通知機能
- タイマー終了時に音や画面通知（フロントエンド）

## 7. 履歴管理（オプション）
- 履歴保存・取得API
- 履歴表示UI

## 8. テスト実装
- サービス層・ルートのユニットテスト（tests/）
- 異常系・モック/スタブの活用

## 9. UI/UXブラッシュアップ
- 画像やアイコン追加
- CSSフレームワーク導入（必要に応じて）
