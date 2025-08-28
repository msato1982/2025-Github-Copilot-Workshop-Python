#!/usr/bin/env python3
"""
ポモドーロタイマーのデモンストレーション
短い時間でテスト用
"""

from main import PomodoroTimer, display_weekly_graph, display_monthly_graph
import time


def demo_timer():
    """デモ用のタイマー（短時間バージョン）"""
    print("🍅 ポモドーロタイマーデモ（短時間版）")
    print("=" * 40)
    
    # 短い時間でテスト（秒単位）
    timer = PomodoroTimer(work_duration=0.1, short_break=0.05, long_break=0.1)  # 6秒、3秒、6秒
    
    print("\n初期統計:")
    timer.gamification.display_stats()
    
    print("\n=== デモ開始 ===")
    
    # 1回目のポモドーロ
    print("\n1. 最初のポモドーロを開始...")
    timer.start_pomodoro()
    time.sleep(7)  # 完了を待つ
    
    # 2回目のポモドーロ
    print("\n2. 2回目のポモドーロ...")
    time.sleep(4)  # 休憩完了を待つ
    timer.start_pomodoro()
    time.sleep(7)  # 完了を待つ
    
    # 統計表示
    print("\n=== 最終統計 ===")
    timer.gamification.display_stats()
    
    # 週間統計表示
    weekly_stats = timer.gamification.get_weekly_stats()
    display_weekly_graph(weekly_stats)
    
    # 月間統計表示  
    monthly_stats = timer.gamification.get_monthly_stats()
    display_monthly_graph(monthly_stats)
    
    print("\n🎉 デモ完了！")
    print("実際の使用時は 'python main.py' でフルバージョンを起動してください。")


if __name__ == "__main__":
    demo_timer()