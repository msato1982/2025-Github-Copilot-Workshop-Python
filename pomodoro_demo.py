#!/usr/bin/env python3
"""
ポモドーロタイマーのテスト用デモ版
短時間での動作確認用
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pomodoro_timer import PomodoroTimer, PomodoroConfig, VisualEffects, PomodoroState
import time
import threading


def demo_visual_effects():
    """視覚エフェクトのデモ"""
    print("🎨 視覚エフェクトデモ")
    print("=" * 50)
    
    effects = VisualEffects()
    
    # カラーグラデーションのデモ
    print("\n色の変化デモ (青 → 黄 → 赤):")
    for i in range(11):
        progress = i / 10.0
        color = effects.get_color_for_progress(progress)
        print(f"{color}進捗 {progress*100:3.0f}% {'█' * int(progress * 20)}{effects.COLORS['reset']}")
        time.sleep(0.1)
    
    # 円形プログレスバーのデモ
    print("\n円形プログレスバーのアニメーション:")
    for i in range(21):
        progress = i / 20.0
        color = effects.get_color_for_progress(progress)
        
        effects.clear_screen()
        print(f"{color}進捗: {progress*100:3.0f}%{effects.COLORS['reset']}")
        
        circle = effects.create_circular_progress(progress, 8)
        for line in circle:
            print(f"{color}{line}{effects.COLORS['reset']}")
        
        time.sleep(0.2)
    
    print("\n視覚エフェクトデモ完了！")


def demo_short_timer():
    """短時間タイマーのデモ"""
    print("\n⏰ 短時間タイマーデモ (10秒集中 → 5秒休憩)")
    print("=" * 50)
    
    # 短時間設定
    config = PomodoroConfig(
        focus_duration=10,  # 10秒
        short_break_duration=5,  # 5秒
        long_break_duration=8,  # 8秒
        sessions_until_long_break=2
    )
    
    timer = PomodoroTimer(config)
    
    # コールバック設定
    def on_session_complete():
        print("\n🎉 集中セッション完了！")
    
    def on_break_complete():
        print("\n🎉 休憩完了！")
    
    timer.on_session_complete = on_session_complete
    timer.on_break_complete = on_break_complete
    
    # 自動でセッションを実行
    def auto_advance():
        """自動で次のフェーズに進む"""
        time.sleep(1)  # 少し待ってから開始
        
        # 1回目の集中
        print("\n🍅 自動で集中セッション開始...")
        timer.start_focus_session()
        
        # 10秒待つ
        time.sleep(11)
        
        # 自動で休憩開始
        print("\n☕ 自動で休憩開始...")
        timer.start_break()
        
        # 5秒待つ
        time.sleep(6)
        
        print("\n✅ デモ完了！")
        timer.stop()
    
    # 自動進行スレッド開始
    auto_thread = threading.Thread(target=auto_advance, daemon=True)
    auto_thread.start()
    
    # メインループ（最大30秒で終了）
    start_time = time.time()
    try:
        while timer.state != PomodoroState.STOPPED and (time.time() - start_time) < 30:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n終了中...")
        timer.stop()
    
    print("短時間タイマーデモ完了！")


def test_timer_functionality():
    """タイマー機能のテスト"""
    print("\n🔧 タイマー機能テスト")
    print("=" * 50)
    
    config = PomodoroConfig(focus_duration=3, short_break_duration=2)
    timer = PomodoroTimer(config)
    
    # 状態テスト
    print("✓ 初期状態:", timer.get_status()['state'])
    
    # 集中セッション開始テスト
    timer.start_focus_session()
    print("✓ 集中セッション開始:", timer.get_status()['state'])
    
    # 一時停止テスト
    time.sleep(1)
    timer.pause()
    print("✓ 一時停止:", timer.get_status()['state'])
    
    # 再開テスト
    timer.resume()
    print("✓ 再開:", timer.get_status()['state'])
    
    # 進捗確認
    time.sleep(1)
    status = timer.get_status()
    print(f"✓ 進捗: {status['progress']:.2f} (経過: {status['elapsed_time']:.1f}秒)")
    
    # 停止テスト
    timer.stop()
    print("✓ 停止:", timer.get_status()['state'])
    
    print("タイマー機能テスト完了！")


def main():
    """デモメイン関数"""
    print("🍅 ポモドーロタイマー - デモ版")
    print("=" * 50)
    print("このデモでは以下の機能を確認できます:")
    print("1. 視覚エフェクト (色の変化、円形プログレスバー)")
    print("2. 短時間タイマー (実際の動作確認)")
    print("3. タイマー機能テスト (基本機能)")
    
    while True:
        print("\n選択してください:")
        print("1. 視覚エフェクトデモ")
        print("2. 短時間タイマーデモ")
        print("3. タイマー機能テスト")
        print("4. 全て実行")
        print("0. 終了")
        
        try:
            choice = input("\n選択 (0-4): ").strip()
            
            if choice == '1':
                demo_visual_effects()
            elif choice == '2':
                demo_short_timer()
            elif choice == '3':
                test_timer_functionality()
            elif choice == '4':
                demo_visual_effects()
                test_timer_functionality()
                demo_short_timer()
            elif choice == '0':
                print("デモを終了します。")
                break
            else:
                print("無効な選択です。")
                
        except KeyboardInterrupt:
            print("\n\nデモを終了します。")
            break
        except Exception as e:
            print(f"\nエラーが発生しました: {e}")
            print("デモを続行します...")


if __name__ == "__main__":
    main()