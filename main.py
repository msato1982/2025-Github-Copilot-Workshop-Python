#!/usr/bin/env python3
"""
ポモドーロタイマー - メインランチャー

使用方法:
- python3 main.py: 通常のポモドーロタイマー実行
- python3 test_pomodoro.py: 機能テストの実行
- python3 pomodoro_demo.py: デモ版の実行
"""

import sys
import os

def main():
    """メインランチャー関数"""
    print("🍅 ポモドーロタイマー - 視覚的フィードバック強化版")
    print("=" * 60)
    print()
    print("実装済み機能:")
    print("✅ 円形プログレスバーのアニメーション（残り時間に応じた滑らかな減少）")
    print("✅ 色の変化（時間経過に応じて青→黄→赤のグラデーション）")
    print("✅ 背景エフェクト（集中時間中のパーティクルエフェクトや波紋アニメーション）")
    print("✅ ポモドーロ技法の完全サポート（25分集中→5分休憩→4セッション後に長い休憩）")
    print("✅ 一時停止・再開機能")
    print("✅ カスタマイズ可能な設定")
    print()
    
    print("実行オプション:")
    print("1. ポモドーロタイマーを開始")
    print("2. 機能テストを実行")
    print("0. 終了")
    
    try:
        choice = input("\n選択してください (0-2): ").strip()
        
        if choice == '1':
            # ポモドーロタイマーを実行
            from pomodoro_timer import main as pomodoro_main
            pomodoro_main()
        elif choice == '2':
            # テストを実行
            from test_pomodoro import run_all_tests
            run_all_tests()
        elif choice == '0':
            print("終了します。")
        else:
            print("無効な選択です。")
            
    except KeyboardInterrupt:
        print("\n\n終了します。")
    except ImportError as e:
        print(f"\nモジュールのインポートに失敗しました: {e}")
        print("必要なファイルが見つからない可能性があります。")
    except Exception as e:
        print(f"\nエラーが発生しました: {e}")


if __name__ == "__main__":
    main()
