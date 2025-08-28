#!/usr/bin/env python3
"""
ポモドーロタイマーのテストスクリプト
Test script for the Pomodoro timer functionality
"""

import time
import sys
import os

# Add current directory to path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pomodoro_timer import PomodoroTimer, Theme, PomodoroSettings


def test_basic_functionality():
    """基本機能のテスト"""
    print("🧪 基本機能テスト開始...")
    
    timer = PomodoroTimer()
    
    # 初期状態テスト
    assert timer.state.value == "stopped", "初期状態はstoppedであるべき"
    assert timer.completed_pomodoros == 0, "完了ポモドーロ数は0であるべき"
    print("✅ 初期状態テスト通過")
    
    # 作業時間設定テスト
    assert timer.set_work_duration(35), "有効な作業時間設定は成功するべき"
    assert timer.settings.work_duration == 35, "設定した作業時間が保存されるべき"
    assert not timer.set_work_duration(30), "無効な作業時間設定は失敗するべき"
    print("✅ 作業時間設定テスト通過")
    
    # 休憩時間設定テスト
    assert timer.set_break_duration(10), "有効な休憩時間設定は成功するべき"
    assert timer.settings.break_duration == 10, "設定した休憩時間が保存されるべき"
    assert not timer.set_break_duration(20), "無効な休憩時間設定は失敗するべき"
    print("✅ 休憩時間設定テスト通過")
    
    # テーマ設定テスト
    timer.set_theme(Theme.DARK)
    assert timer.settings.theme == Theme.DARK, "テーマが正しく設定されるべき"
    colors = timer.get_theme_colors()
    assert colors['bg'] == '#1C1C1E', "ダークテーマの背景色が正しいべき"
    print("✅ テーマ設定テスト通過")
    
    # サウンド設定テスト
    timer.set_sound_settings(start=False, end=True, tick=True)
    assert not timer.settings.sound_start, "開始音がOFFに設定されるべき"
    assert timer.settings.sound_end, "終了音がONに設定されるべき"
    assert timer.settings.sound_tick, "ティック音がONに設定されるべき"
    print("✅ サウンド設定テスト通過")
    
    print("🎉 基本機能テスト完了！")


def test_timer_functionality():
    """タイマー機能テスト"""
    print("\n🧪 タイマー機能テスト開始...")
    
    timer = PomodoroTimer()
    timer.set_work_duration(15)  # 15分に設定
    
    # 作業セッション開始テスト
    assert timer.start_work_session(), "作業セッション開始は成功するべき"
    assert timer.state.value == "running", "作業セッション開始後は実行中状態であるべき"
    assert timer.is_work_session, "作業セッション中であるべき"
    assert timer.remaining_seconds == 15 * 60, "残り時間は15分であるべき"
    print("✅ 作業セッション開始テスト通過")
    
    # 一時停止/再開テスト
    assert timer.pause(), "一時停止は成功するべき"
    assert timer.state.value == "paused", "一時停止後は停止状態であるべき"
    
    assert timer.resume(), "再開は成功するべき"
    assert timer.state.value == "running", "再開後は実行中状態であるべき"
    print("✅ 一時停止/再開テスト通過")
    
    # 停止テスト
    timer.stop()
    assert timer.state.value == "stopped", "停止後はstopped状態であるべき"
    assert timer.remaining_seconds == 0, "停止後の残り時間は0であるべき"
    print("✅ 停止テスト通過")
    
    # 休憩セッションテスト
    timer.set_break_duration(5)  # 5分に設定
    assert timer.start_break_session(), "休憩セッション開始は成功するべき"
    assert timer.state.value == "break", "休憩セッション開始後は休憩状態であるべき"
    assert not timer.is_work_session, "休憩セッション中は作業中でないべき"
    assert timer.remaining_seconds == 5 * 60, "休憩の残り時間は5分であるべき"
    print("✅ 休憩セッションテスト通過")
    
    timer.stop()
    print("🎉 タイマー機能テスト完了！")


def test_settings_persistence():
    """設定の永続化テスト"""
    print("\n🧪 設定永続化テスト開始...")
    
    # 最初のタイマーで設定を変更
    timer1 = PomodoroTimer()
    timer1.set_work_duration(45)
    timer1.set_break_duration(15)
    timer1.set_theme(Theme.FOCUS)
    timer1.set_sound_settings(start=False, end=False, tick=True)
    
    # 新しいタイマーで設定が読み込まれるかテスト
    timer2 = PomodoroTimer()
    assert timer2.settings.work_duration == 45, "作業時間設定が永続化されるべき"
    assert timer2.settings.break_duration == 15, "休憩時間設定が永続化されるべき"
    assert timer2.settings.theme == Theme.FOCUS, "テーマ設定が永続化されるべき"
    assert not timer2.settings.sound_start, "開始音設定が永続化されるべき"
    assert not timer2.settings.sound_end, "終了音設定が永続化されるべき"
    assert timer2.settings.sound_tick, "ティック音設定が永続化されるべき"
    
    print("✅ 設定永続化テスト通過")
    print("🎉 設定永続化テスト完了！")


def test_time_calculations():
    """時間計算テスト"""
    print("\n🧪 時間計算テスト開始...")
    
    timer = PomodoroTimer()
    timer.remaining_seconds = 125  # 2分5秒
    
    minutes, seconds = timer.get_remaining_time()
    assert minutes == 2, "分の計算が正しいべき"
    assert seconds == 5, "秒の計算が正しいべき"
    
    # 進捗率テスト
    timer.total_seconds = 1500  # 25分
    timer.remaining_seconds = 750  # 12.5分
    progress = timer.get_progress()
    assert abs(progress - 0.5) < 0.001, "進捗率は50%であるべき"
    
    print("✅ 時間計算テスト通過")
    print("🎉 時間計算テスト完了！")


def demonstrate_features():
    """機能のデモンストレーション"""
    print("\n🎬 機能デモンストレーション開始...")
    
    timer = PomodoroTimer()
    
    # 利用可能な時間オプション表示
    print(f"📋 利用可能な作業時間: {timer.WORK_TIME_OPTIONS}分")
    print(f"📋 利用可能な休憩時間: {timer.BREAK_TIME_OPTIONS}分")
    
    # 各テーマの色設定表示
    for theme in Theme:
        timer.set_theme(theme)
        colors = timer.get_theme_colors()
        print(f"🎨 {theme.value.upper()}テーマ:")
        print(f"   背景色: {colors['bg']}")
        print(f"   テキスト色: {colors['text']}")
        print(f"   アクセント色: {colors['accent']}")
    
    # カスタマイズ例
    print("\n⚙️ カスタマイズ例:")
    timer.set_work_duration(35)
    timer.set_break_duration(10) 
    timer.set_theme(Theme.FOCUS)
    timer.set_sound_settings(start=True, end=True, tick=False)
    
    print(f"   作業時間: {timer.settings.work_duration}分")
    print(f"   休憩時間: {timer.settings.break_duration}分")
    print(f"   テーマ: {timer.settings.theme.value}")
    print(f"   サウンド設定:")
    print(f"     開始音: {'ON' if timer.settings.sound_start else 'OFF'}")
    print(f"     終了音: {'ON' if timer.settings.sound_end else 'OFF'}")
    print(f"     ティック音: {'ON' if timer.settings.sound_tick else 'OFF'}")
    
    print("🎉 機能デモンストレーション完了！")


def main():
    """メインテスト実行"""
    print("🍅 ポモドーロタイマー機能テスト実行")
    print("=" * 50)
    
    try:
        test_basic_functionality()
        test_timer_functionality()
        test_settings_persistence()
        test_time_calculations()
        demonstrate_features()
        
        print("\n" + "=" * 50)
        print("🎉 すべてのテストが正常に完了しました！")
        print("✅ カスタマイズ可能なポモドーロタイマーの実装が成功しています")
        
    except AssertionError as e:
        print(f"\n❌ テスト失敗: {e}")
        return 1
    except Exception as e:
        print(f"\n💥 予期しないエラー: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())