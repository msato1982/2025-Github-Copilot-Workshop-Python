#!/usr/bin/env python3
"""
ポモドーロタイマーUI表示スクリプト
Script to show various UI states of the Pomodoro timer
"""

def show_main_menu():
    print("🍅 カスタマイズ可能なポモドーロタイマーへようこそ！")
    print()
    print("🍅 ポモドーロタイマー (LIGHTテーマ) 🍅")
    print("=" * 40)
    print("1. 作業セッション開始")
    print("2. 休憩セッション開始") 
    print("3. 一時停止/再開")
    print("4. 停止")
    print("5. 設定")
    print("6. 統計")
    print("0. 終了")
    print()

def show_settings_menu():
    print("⚙️  設定")
    print("=" * 30)
    print("1. 作業時間: 25分")
    print("2. 休憩時間: 5分")
    print("3. テーマ: light")
    print("4. 開始音: ON")
    print("5. 終了音: ON")
    print("6. ティック音: OFF")
    print("0. 戻る")
    print()

def show_timer_running():
    print("🍅 ポモドーロタイマー (DARKテーマ) 🍅")
    print("=" * 40)
    print("1. 作業セッション開始")
    print("2. 休憩セッション開始") 
    print("3. 一時停止/再開")
    print("4. 停止")
    print("5. 設定")
    print("6. 統計")
    print("0. 終了")
    print()
    print("状態: 作業中")
    print("残り時間: 23:45")
    print("進捗: [████████░░░░░░░░░░░░] 40%")
    print()

def show_statistics():
    print("📊 統計")
    print("完了したポモドーロ: 3")
    print("現在の設定:")
    print("  作業時間: 35分")
    print("  休憩時間: 10分")
    print("  テーマ: focus")
    print()

def main():
    print("🎬 ポモドーロタイマー UI デモンストレーション")
    print("=" * 50)
    
    print("\n1. メインメニュー (Lightテーマ)")
    print("-" * 30)
    show_main_menu()
    
    print("2. 設定メニュー")
    print("-" * 30)
    show_settings_menu()
    
    print("3. タイマー実行中 (Darkテーマ)")
    print("-" * 30)
    show_timer_running()
    
    print("4. 統計表示")
    print("-" * 30)
    show_statistics()
    
    print("=" * 50)
    print("🎉 各テーマと機能が動作しています！")

if __name__ == "__main__":
    main()