#!/usr/bin/env python3
"""
ポモドーロタイマーの機能デモスクリプト
Demo script showcasing Pomodoro timer features
"""

import time
import sys
import os

# Add current directory to path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pomodoro_timer import PomodoroTimer, Theme


def demo_short_timer():
    """短時間タイマーのデモ（5秒）"""
    print("🎬 5秒タイマーのデモ開始...")
    
    timer = PomodoroTimer()
    
    # 5秒のテスト用設定（実際のアプリでは使用不可）
    timer.settings.work_duration = 1  # 実際には1分だが、デモ用に秒で制御
    timer.total_seconds = 5
    timer.remaining_seconds = 5
    timer.state = timer.state.__class__("running")
    timer.is_work_session = True
    
    # コールバック設定
    def on_tick():
        minutes, seconds = timer.get_remaining_time()
        progress = timer.get_progress()
        progress_bar = "█" * int(progress * 20) + "░" * (20 - int(progress * 20))
        print(f"\r⏱️  残り時間: {timer.remaining_seconds:02d}秒 [{progress_bar}] {progress:.0%}", end="", flush=True)
    
    def on_end():
        print("\n🔔 タイマー終了！")
    
    timer.on_timer_tick = on_tick
    timer.on_timer_end = on_end
    
    # 手動でタイマー実行
    for i in range(5):
        on_tick()
        time.sleep(1)
        timer.remaining_seconds -= 1
        timer.total_seconds = 5  # 進捗計算のため
    
    on_end()
    print("✅ デモ完了！\n")


def demo_settings_showcase():
    """設定のショーケース"""
    print("🎨 カスタマイズ機能ショーケース")
    print("=" * 40)
    
    timer = PomodoroTimer()
    
    # 各設定の組み合わせをデモ
    settings_demos = [
        {
            'name': 'ライトワーク（短時間集中）',
            'work': 15,
            'break': 5,
            'theme': Theme.LIGHT,
            'sounds': {'start': True, 'end': True, 'tick': False}
        },
        {
            'name': 'スタンダード（クラシック）',
            'work': 25,
            'break': 5,
            'theme': Theme.LIGHT,
            'sounds': {'start': True, 'end': True, 'tick': False}
        },
        {
            'name': 'ディープワーク（長時間集中）',
            'work': 45,
            'break': 15,
            'theme': Theme.DARK,
            'sounds': {'start': True, 'end': True, 'tick': True}
        },
        {
            'name': 'フォーカスモード（ミニマル）',
            'work': 35,
            'break': 10,
            'theme': Theme.FOCUS,
            'sounds': {'start': False, 'end': True, 'tick': False}
        }
    ]
    
    for i, demo in enumerate(settings_demos, 1):
        print(f"\n{i}. {demo['name']}")
        print("-" * 30)
        
        # 設定を適用
        timer.set_work_duration(demo['work'])
        timer.set_break_duration(demo['break'])
        timer.set_theme(demo['theme'])
        timer.set_sound_settings(**demo['sounds'])
        
        # 設定表示
        colors = timer.get_theme_colors()
        print(f"⏰ 作業時間: {timer.settings.work_duration}分")
        print(f"☕ 休憩時間: {timer.settings.break_duration}分")
        print(f"🎨 テーマ: {timer.settings.theme.value.upper()}")
        print(f"   背景色: {colors['bg']}")
        print(f"   テキスト色: {colors['text']}")
        print(f"   アクセント色: {colors['accent']}")
        print(f"🔊 サウンド:")
        print(f"   開始音: {'🔔' if timer.settings.sound_start else '🔇'}")
        print(f"   終了音: {'🔔' if timer.settings.sound_end else '🔇'}")
        print(f"   ティック音: {'🔔' if timer.settings.sound_tick else '🔇'}")
    
    print("\n✨ すべての設定は自動的に保存されます！")


def demo_user_scenarios():
    """ユーザーシナリオのデモ"""
    print("\n👥 ユーザーシナリオ例")
    print("=" * 40)
    
    scenarios = [
        {
            'user': 'プログラマー',
            'scenario': 'コーディングに集中したい',
            'settings': {
                'work': 35,
                'break': 10,
                'theme': Theme.DARK,
                'sounds': {'start': True, 'end': True, 'tick': False}
            },
            'reason': 'ダークテーマで目に優しく、適度な集中時間で深く考える作業に最適'
        },
        {
            'user': '学生',
            'scenario': '勉強の習慣化',
            'settings': {
                'work': 25,
                'break': 5,
                'theme': Theme.LIGHT,
                'sounds': {'start': True, 'end': True, 'tick': False}
            },
            'reason': 'クラシックな25分設定で習慣化しやすく、明るいテーマで活力を保つ'
        },
        {
            'user': 'ライター',
            'scenario': '執筆に没頭したい',
            'settings': {
                'work': 45,
                'break': 15,
                'theme': Theme.FOCUS,
                'sounds': {'start': False, 'end': True, 'tick': False}
            },
            'reason': 'フォーカスモードで気が散らず、長時間集中で創作フローを維持'
        },
        {
            'user': '在宅ワーカー',
            'scenario': 'タスクを効率的に処理',
            'settings': {
                'work': 15,
                'break': 5,
                'theme': Theme.LIGHT,
                'sounds': {'start': True, 'end': True, 'tick': True}
            },
            'reason': '短時間で区切ってタスクスイッチング、ティック音で時間意識を保つ'
        }
    ]
    
    timer = PomodoroTimer()
    
    for scenario in scenarios:
        print(f"\n👤 {scenario['user']}")
        print(f"🎯 目的: {scenario['scenario']}")
        
        # 設定を適用
        s = scenario['settings']
        timer.set_work_duration(s['work'])
        timer.set_break_duration(s['break'])
        timer.set_theme(s['theme'])
        timer.set_sound_settings(**s['sounds'])
        
        print(f"⚙️  推奨設定:")
        print(f"   作業時間: {timer.settings.work_duration}分")
        print(f"   休憩時間: {timer.settings.break_duration}分")
        print(f"   テーマ: {timer.settings.theme.value}")
        print(f"   サウンド: {', '.join([k for k, v in s['sounds'].items() if v])}")
        print(f"💡 理由: {scenario['reason']}")


def main():
    """デモメイン実行"""
    print("🍅 ポモドーロタイマー カスタマイズ機能デモ")
    print("=" * 50)
    
    demo_short_timer()
    demo_settings_showcase()
    demo_user_scenarios()
    
    print("\n" + "=" * 50)
    print("🎉 デモ完了！")
    print("💡 これらの設定はすべてリアルタイムで変更可能です")
    print("📱 個人の好みに合わせてカスタマイズしてください！")
    print("\n実際のアプリを起動するには:")
    print("   python3 main.py")


if __name__ == "__main__":
    main()