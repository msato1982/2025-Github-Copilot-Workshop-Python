import time
import threading
from typing import Optional
from enum import Enum
from point import GamificationSystem


class PomodoroState(Enum):
    """ポモドーロの状態"""
    IDLE = "idle"
    WORKING = "working"
    BREAK = "break"
    LONG_BREAK = "long_break"
    PAUSED = "paused"


class PomodoroTimer:
    """ポモドーロタイマーのメインクラス"""
    
    def __init__(self, work_duration: int = 25, short_break: int = 5, long_break: int = 15):
        self.work_duration = work_duration * 60  # 分を秒に変換
        self.short_break_duration = short_break * 60
        self.long_break_duration = long_break * 60
        
        self.state = PomodoroState.IDLE
        self.remaining_time = 0
        self.pomodoro_count = 0
        self.is_running = False
        self.timer_thread: Optional[threading.Thread] = None
        
        # ゲーミフィケーションシステムを初期化
        self.gamification = GamificationSystem()
    
    def start_pomodoro(self):
        """ポモドーロを開始"""
        if self.state != PomodoroState.IDLE:
            print("既にタイマーが動作中です。")
            return
        
        self.state = PomodoroState.WORKING
        self.remaining_time = self.work_duration
        self.is_running = True
        
        print(f"\n🍅 ポモドーロタイマー開始！ ({self.work_duration // 60}分)")
        print("集中して作業を頑張りましょう！")
        
        self.timer_thread = threading.Thread(target=self._run_timer)
        self.timer_thread.daemon = True
        self.timer_thread.start()
    
    def start_break(self, is_long_break: bool = False):
        """休憩を開始"""
        if is_long_break:
            self.state = PomodoroState.LONG_BREAK
            self.remaining_time = self.long_break_duration
            print(f"\n☕ 長い休憩開始！ ({self.long_break_duration // 60}分)")
        else:
            self.state = PomodoroState.BREAK
            self.remaining_time = self.short_break_duration
            print(f"\n☕ 短い休憩開始！ ({self.short_break_duration // 60}分)")
        
        print("リラックスして休憩してください。")
        self.is_running = True
        
        self.timer_thread = threading.Thread(target=self._run_timer)
        self.timer_thread.daemon = True
        self.timer_thread.start()
    
    def pause_timer(self):
        """タイマーを一時停止"""
        if self.state == PomodoroState.IDLE or not self.is_running:
            print("タイマーが動作していません。")
            return
        
        self.is_running = False
        self.state = PomodoroState.PAUSED
        print("⏸️  タイマーを一時停止しました。")
    
    def resume_timer(self):
        """タイマーを再開"""
        if self.state != PomodoroState.PAUSED:
            print("一時停止中ではありません。")
            return
        
        print("▶️  タイマーを再開しました。")
        if self.remaining_time > 0:
            # 前の状態に戻る（作業中だったのか休憩中だったのか）
            if self.pomodoro_count % 4 == 0 and self.pomodoro_count > 0:
                self.state = PomodoroState.LONG_BREAK
            elif self.remaining_time == self.work_duration:
                self.state = PomodoroState.WORKING
            else:
                self.state = PomodoroState.BREAK
            
            self.is_running = True
            self.timer_thread = threading.Thread(target=self._run_timer)
            self.timer_thread.daemon = True
            self.timer_thread.start()
    
    def stop_timer(self):
        """タイマーを停止"""
        self.is_running = False
        self.state = PomodoroState.IDLE
        self.remaining_time = 0
        print("🛑 タイマーを停止しました。")
    
    def skip_session(self):
        """現在のセッションをスキップ"""
        if self.state == PomodoroState.IDLE:
            print("タイマーが動作していません。")
            return
        
        self.is_running = False
        if self.state == PomodoroState.WORKING:
            print("⏭️  作業セッションをスキップしました。")
            self._start_next_session()
        else:
            print("⏭️  休憩をスキップしました。")
            self._start_next_session()
    
    def _run_timer(self):
        """タイマーのメインループ"""
        while self.remaining_time > 0 and self.is_running:
            time.sleep(1)
            self.remaining_time -= 1
            
            # 残り時間を表示（10秒ごと）
            if self.remaining_time % 10 == 0 or self.remaining_time <= 10:
                mins, secs = divmod(int(self.remaining_time), 60)
                status = "作業中" if self.state == PomodoroState.WORKING else "休憩中"
                print(f"{status}: {mins:02d}:{secs:02d} 残り")
        
        if self.is_running and self.remaining_time <= 0:
            self._session_completed()
    
    def _session_completed(self):
        """セッション完了時の処理"""
        if self.state == PomodoroState.WORKING:
            # 作業セッション完了
            self.pomodoro_count += 1
            print(f"\n🎉 ポモドーロ完了！ ({self.pomodoro_count}回目)")
            
            # ゲーミフィケーション処理
            result = self.gamification.complete_pomodoro()
            
            # XP獲得通知
            print(f"💎 {result['xp_gained']} XP 獲得！")
            
            # レベルアップ通知
            if result['new_level']:
                print(f"🌟 レベルアップ！ レベル {self.gamification.stats.current_level} になりました！")
            
            # 新しいバッジ通知
            newly_earned = [b for b in result['new_badges'] 
                          if b.earned_date and b.earned_date.split()[0] == time.strftime("%Y-%m-%d")]
            if newly_earned:
                print("🏆 新しいバッジを獲得しました！")
                for badge in newly_earned:
                    print(f"   {badge.name}: {badge.description}")
            
            self._start_next_session()
        else:
            # 休憩完了
            print("\n✅ 休憩終了！次のポモドーロを始めましょう。")
            self.state = PomodoroState.IDLE
    
    def _start_next_session(self):
        """次のセッションを開始"""
        if self.pomodoro_count % 4 == 0 and self.pomodoro_count > 0:
            # 4回目の作業後は長い休憩
            self.start_break(is_long_break=True)
        elif self.state == PomodoroState.WORKING:
            # 作業後は短い休憩
            self.start_break(is_long_break=False)
        else:
            # 休憩後は作業
            self.state = PomodoroState.IDLE
            print("次のポモドーロを開始する準備ができました。")
    
    def get_status(self) -> dict:
        """現在の状態を取得"""
        mins, secs = divmod(int(self.remaining_time), 60)
        return {
            "state": self.state.value,
            "remaining_time": f"{mins:02d}:{secs:02d}",
            "pomodoro_count": self.pomodoro_count,
            "is_running": self.is_running
        }
    
    def display_help(self):
        """ヘルプメッセージを表示"""
        print("\n=== ポモドーロタイマー コマンド ===")
        print("start  - ポモドーロを開始")
        print("pause  - タイマーを一時停止")
        print("resume - タイマーを再開") 
        print("stop   - タイマーを停止")
        print("skip   - 現在のセッションをスキップ")
        print("status - 現在の状態を表示")
        print("stats  - 統計とバッジを表示")
        print("weekly - 週間統計を表示")
        print("monthly- 月間統計を表示")
        print("help   - このヘルプを表示")
        print("quit   - アプリケーションを終了")


def display_weekly_graph(weekly_stats):
    """週間統計をテキストグラフで表示"""
    print(f"\n=== 週間統計 ===")
    print(f"今週の完了数: {weekly_stats['total_completions']}")
    print(f"完了率: {weekly_stats['completion_rate']:.1f}%")
    print("\n今週の日別完了数:")
    
    max_completions = max([day['completions'] for day in weekly_stats['daily_data']], default=0)
    for day in weekly_stats['daily_data']:
        bar = "█" * day['completions'] + "░" * (max_completions - day['completions']) if max_completions > 0 else ""
        print(f"{day['date']}: {bar} ({day['completions']})")


def display_monthly_graph(monthly_stats):
    """月間統計を表示"""
    print(f"\n=== 月間統計 ===")
    print(f"今月の完了数: {monthly_stats['total_completions']}")
    print(f"アクティブ日数: {monthly_stats['days_active']}日")
    print(f"完了率: {monthly_stats['completion_rate']:.1f}%")
    print(f"1日平均: {monthly_stats['average_per_day']:.1f}回")


def main():
    """メインループ"""
    print("🍅 ポモドーロタイマー with ゲーミフィケーション")
    print("help と入力してコマンドを確認してください。")
    
    timer = PomodoroTimer()
    
    # 初期統計表示
    timer.gamification.display_stats()
    
    while True:
        try:
            command = input("\nコマンド: ").strip().lower()
            
            if command == "start":
                timer.start_pomodoro()
            elif command == "pause":
                timer.pause_timer()
            elif command == "resume":
                timer.resume_timer()
            elif command == "stop":
                timer.stop_timer()
            elif command == "skip":
                timer.skip_session()
            elif command == "status":
                status = timer.get_status()
                print(f"\n現在の状態: {status['state']}")
                print(f"残り時間: {status['remaining_time']}")
                print(f"完了したポモドーロ: {status['pomodoro_count']}回")
                print(f"タイマー動作中: {'はい' if status['is_running'] else 'いいえ'}")
            elif command == "stats":
                timer.gamification.display_stats()
            elif command == "weekly":
                weekly_stats = timer.gamification.get_weekly_stats()
                display_weekly_graph(weekly_stats)
            elif command == "monthly":
                monthly_stats = timer.gamification.get_monthly_stats()
                display_monthly_graph(monthly_stats)
            elif command == "help":
                timer.display_help()
            elif command == "quit":
                timer.stop_timer()
                print("お疲れ様でした！")
                break
            else:
                print("不明なコマンドです。'help'でコマンド一覧を確認してください。")
        
        except KeyboardInterrupt:
            timer.stop_timer()
            print("\nお疲れ様でした！")
            break
        except Exception as e:
            print(f"エラーが発生しました: {e}")


if __name__ == "__main__":
    main()
