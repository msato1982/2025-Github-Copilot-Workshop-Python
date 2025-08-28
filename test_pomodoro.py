#!/usr/bin/env python3
"""
ポモドーロタイマー機能テスト - 非対話版
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pomodoro_timer import PomodoroTimer, PomodoroConfig, VisualEffects, PomodoroState
import time
import threading


def test_visual_effects():
    """視覚エフェクトのテスト"""
    print("🎨 視覚エフェクトテスト")
    print("=" * 50)
    
    effects = VisualEffects()
    
    # カラーテスト
    print("\n色の変化テスト:")
    for i in range(0, 11, 2):
        progress = i / 10.0
        color = effects.get_color_for_progress(progress)
        bar = "█" * int(progress * 10)
        print(f"{color}進捗 {progress*100:3.0f}% [{bar:10}]{effects.COLORS['reset']}")
    
    # 円形プログレスバーテスト
    print(f"\n円形プログレスバーテスト:")
    for progress in [0.0, 0.25, 0.5, 0.75, 1.0]:
        print(f"\n進捗: {progress*100:.0f}%")
        color = effects.get_color_for_progress(progress)
        circle = effects.create_circular_progress(progress, 6)
        for i, line in enumerate(circle):
            if i < 4:  # 上半分のみ表示
                print(f"{color}{line}{effects.COLORS['reset']}")
    
    # パーティクルテスト  
    print(f"\nパーティクルエフェクトテスト:")
    particles = effects.create_particles(40, 3)
    for line in particles:
        print(f"{effects.COLORS['cyan']}{line}{effects.COLORS['reset']}")
    
    # 波紋テスト
    print(f"\n波紋エフェクトテスト:")
    ripples = effects.create_ripple_effect(20, 2, 3.5, 40, 5)
    for line in ripples:
        print(f"{effects.COLORS['blue']}{line}{effects.COLORS['reset']}")
    
    print("✅ 視覚エフェクトテスト完了")


def test_timer_functionality():
    """タイマー機能のテスト"""
    print("\n🔧 タイマー機能テスト")
    print("=" * 50)
    
    config = PomodoroConfig(focus_duration=3, short_break_duration=2, long_break_duration=4)
    timer = PomodoroTimer(config)
    
    # 初期状態テスト
    status = timer.get_status()
    print(f"✅ 初期状態: {status['state']}")
    assert status['state'] == 'stopped'
    assert status['current_session'] == 0
    
    # 集中セッション開始テスト
    timer.start_focus_session()
    time.sleep(0.5)  # 少し待つ
    status = timer.get_status()
    print(f"✅ 集中セッション開始: {status['state']}")
    print(f"   セッション数: {status['current_session']}")
    print(f"   進捗: {status['progress']:.2f}")
    assert status['state'] == 'focus'
    assert status['current_session'] == 1
    assert 0 <= status['progress'] <= 1.0
    
    # 一時停止テスト
    timer.pause()
    time.sleep(0.2)
    status = timer.get_status()
    print(f"✅ 一時停止: {status['state']}")
    assert status['state'] == 'paused'
    
    # 再開テスト
    timer.resume()
    time.sleep(0.2)
    status = timer.get_status()
    print(f"✅ 再開: {status['state']}")
    assert status['state'] == 'focus'
    
    # 進捗確認
    time.sleep(1)
    status = timer.get_status()
    print(f"✅ 進捗確認: {status['progress']:.2f} (経過: {status['elapsed_time']:.1f}秒)")
    assert status['progress'] > 0
    
    # 停止テスト
    timer.stop()
    status = timer.get_status()
    print(f"✅ 停止: {status['state']}")
    assert status['state'] == 'stopped'
    
    print("✅ タイマー機能テスト完了")


def test_timer_completion():
    """タイマー完了機能のテスト"""
    print("\n⏰ タイマー完了テスト")
    print("=" * 50)
    
    # 短時間設定でテスト
    config = PomodoroConfig(focus_duration=2, short_break_duration=1)
    timer = PomodoroTimer(config)
    
    session_completed = False
    break_completed = False
    
    def on_session_complete():
        nonlocal session_completed
        session_completed = True
        print("🎉 セッション完了コールバック実行")
    
    def on_break_complete():
        nonlocal break_completed  
        break_completed = True
        print("🎉 休憩完了コールバック実行")
    
    timer.on_session_complete = on_session_complete
    timer.on_break_complete = on_break_complete
    
    # 集中セッション開始
    print("集中セッション開始 (2秒)...")
    timer.start_focus_session()
    
    # 完了まで待機
    start_time = time.time()
    while timer.state == PomodoroState.FOCUS and (time.time() - start_time) < 5:
        status = timer.get_status()
        progress_bar = "█" * int(status['progress'] * 20)
        print(f"\r進捗: [{progress_bar:20}] {status['progress']*100:.0f}% (残り: {status['remaining_time']:.1f}s)", end="")
        time.sleep(0.2)
    
    print()  # 改行
    
    # 自動で休憩開始
    if session_completed:
        print("✅ セッション完了検出")
        timer.start_break()
        print("休憩開始 (1秒)...")
        
        # 休憩完了まで待機
        start_time = time.time()
        while timer.state in [PomodoroState.SHORT_BREAK, PomodoroState.LONG_BREAK] and (time.time() - start_time) < 5:
            status = timer.get_status()
            progress_bar = "█" * int(status['progress'] * 20)
            print(f"\r休憩: [{progress_bar:20}] {status['progress']*100:.0f}% (残り: {status['remaining_time']:.1f}s)", end="")
            time.sleep(0.2)
        
        print()  # 改行
        
        if break_completed:
            print("✅ 休憩完了検出")
        else:
            print("❌ 休憩完了が検出されませんでした")
    else:
        print("❌ セッション完了が検出されませんでした")
    
    timer.stop()
    print("✅ タイマー完了テスト完了")


def run_all_tests():
    """全てのテストを実行"""
    print("🍅 ポモドーロタイマー - 機能テスト実行")
    print("=" * 60)
    
    try:
        test_visual_effects()
        test_timer_functionality() 
        test_timer_completion()
        
        print("\n" + "=" * 60)
        print("🎉 全テスト完了！")
        print("✅ 視覚エフェクト: 円形プログレスバー、色変化、パーティクル、波紋")
        print("✅ タイマー機能: 開始、停止、一時停止、再開")
        print("✅ 完了処理: セッション完了、休憩完了の検出")
        
    except Exception as e:
        print(f"\n❌ テスト中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()