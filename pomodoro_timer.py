#!/usr/bin/env python3
"""
ポモドーロタイマー - 視覚的フィードバック強化版
Enhanced Pomodoro Timer with Visual Feedback

機能:
- 円形プログレスバーのアニメーション（残り時間に応じた滑らかな減少）
- 色の変化（時間経過に応じて青→黄→赤のグラデーション）
- 背景エフェクト（集中時間中のパーティクルエフェクトや波紋アニメーション）
"""

import time
import threading
import math
import random
import os
import sys
from typing import Optional, Callable
from enum import Enum
from dataclasses import dataclass


class PomodoroState(Enum):
    """ポモドーロタイマーの状態"""
    STOPPED = "stopped"
    FOCUS = "focus"
    SHORT_BREAK = "short_break" 
    LONG_BREAK = "long_break"
    PAUSED = "paused"


@dataclass
class PomodoroConfig:
    """ポモドーロタイマーの設定"""
    focus_duration: int = 25 * 60  # 25分
    short_break_duration: int = 5 * 60  # 5分
    long_break_duration: int = 15 * 60  # 15分
    sessions_until_long_break: int = 4


class VisualEffects:
    """視覚エフェクト管理クラス"""
    
    # ANSI色コード
    COLORS = {
        'blue': '\033[94m',
        'cyan': '\033[96m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'orange': '\033[38;5;208m',
        'red': '\033[91m',
        'bold': '\033[1m',
        'reset': '\033[0m',
        'clear_line': '\033[2K\r',
        'hide_cursor': '\033[?25l',
        'show_cursor': '\033[?25h'
    }
    
    # 進捗バー用Unicode文字
    PROGRESS_CHARS = {
        'full': '█',
        'seven_eighths': '▉',
        'three_quarters': '▊',
        'five_eighths': '▋',
        'half': '▌',
        'three_eighths': '▍',
        'quarter': '▎',
        'eighth': '▏',
        'empty': ' '
    }
    
    # パーティクル用文字
    PARTICLES = ['*', '·', '•', '○', '●', '◦', '◯', '✦', '✧', '✩', '✪', '✫', '✯', '✰']
    
    @classmethod
    def clear_screen(cls):
        """画面をクリア"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @classmethod
    def hide_cursor(cls):
        """カーソルを非表示"""
        print(cls.COLORS['hide_cursor'], end='')
    
    @classmethod
    def show_cursor(cls):
        """カーソルを表示"""
        print(cls.COLORS['show_cursor'], end='')
    
    @classmethod
    def get_color_for_progress(cls, progress: float) -> str:
        """進捗に基づいて色を取得 (0.0 = 開始時, 1.0 = 終了時)"""
        if progress <= 0.33:
            return cls.COLORS['blue']
        elif progress <= 0.66:
            return cls.COLORS['yellow']
        else:
            return cls.COLORS['red']
    
    @classmethod
    def create_circular_progress(cls, progress: float, radius: int = 10) -> list:
        """円形プログレスバーを作成"""
        lines = []
        center_x, center_y = radius, radius
        
        for y in range(radius * 2 + 1):
            line = ""
            for x in range(radius * 2 + 1):
                dx = x - center_x
                dy = y - center_y
                distance = math.sqrt(dx * dx + dy * dy)
                
                if distance <= radius:
                    # 角度を計算 (上から時計回り)
                    angle = math.atan2(dx, -dy)
                    if angle < 0:
                        angle += 2 * math.pi
                    
                    # 進捗に基づいて塗りつぶし判定
                    angle_progress = angle / (2 * math.pi)
                    if angle_progress <= progress:
                        if distance <= radius - 1:
                            line += cls.PROGRESS_CHARS['full']
                        else:
                            line += cls.PROGRESS_CHARS['half']
                    else:
                        if distance <= radius - 1:
                            line += cls.PROGRESS_CHARS['empty']
                        else:
                            line += cls.PROGRESS_CHARS['eighth']
                else:
                    line += " "
            lines.append(line)
        return lines
    
    @classmethod
    def create_particles(cls, width: int = 60, height: int = 5) -> list:
        """背景パーティクルエフェクトを作成"""
        lines = []
        for _ in range(height):
            line = ""
            for _ in range(width):
                if random.random() < 0.02:  # 2%の確率でパーティクル
                    line += random.choice(cls.PARTICLES)
                else:
                    line += " "
            lines.append(line)
        return lines
    
    @classmethod
    def create_ripple_effect(cls, center_x: int, center_y: int, radius: float, width: int = 60, height: int = 10) -> list:
        """波紋エフェクトを作成"""
        lines = []
        for y in range(height):
            line = ""
            for x in range(width):
                dx = x - center_x
                dy = y - center_y
                distance = math.sqrt(dx * dx + dy * dy)
                
                # 波紋の計算
                if abs(distance - radius) < 1.5:
                    intensity = 1.0 - abs(distance - radius) / 1.5
                    if intensity > 0.7:
                        line += cls.PROGRESS_CHARS['full']
                    elif intensity > 0.3:
                        line += cls.PROGRESS_CHARS['half']
                    else:
                        line += cls.PROGRESS_CHARS['quarter']
                else:
                    line += " "
            lines.append(line)
        return lines


class PomodoroTimer:
    """ポモドーロタイマーメインクラス"""
    
    def __init__(self, config: Optional[PomodoroConfig] = None):
        self.config = config or PomodoroConfig()
        self.state = PomodoroState.STOPPED
        self.current_session = 0
        self.total_sessions = 0
        
        # タイマー関連
        self.start_time: Optional[float] = None
        self.pause_time: Optional[float] = None
        self.elapsed_time: float = 0.0
        self.current_duration: int = 0
        
        # スレッド関連
        self.timer_thread: Optional[threading.Thread] = None
        self.display_thread: Optional[threading.Thread] = None
        self.running = False
        self.display_running = False
        
        # コールバック
        self.on_session_complete: Optional[Callable] = None
        self.on_break_complete: Optional[Callable] = None
        self.on_timer_tick: Optional[Callable] = None
        
        # エフェクト用
        self.ripple_time = 0.0
        self.particle_time = 0.0
    
    def start_focus_session(self):
        """集中セッションを開始"""
        self.state = PomodoroState.FOCUS
        self.current_duration = self.config.focus_duration
        self.current_session += 1
        self.total_sessions += 1
        self._start_timer()
        print(f"\n🍅 集中セッション {self.current_session} 開始! ({self.config.focus_duration // 60}分)")
    
    def start_break(self):
        """休憩を開始"""
        if self.current_session >= self.config.sessions_until_long_break:
            self.state = PomodoroState.LONG_BREAK
            self.current_duration = self.config.long_break_duration
            self.current_session = 0
            break_type = f"長い休憩 ({self.config.long_break_duration // 60}分)"
        else:
            self.state = PomodoroState.SHORT_BREAK
            self.current_duration = self.config.short_break_duration
            break_type = f"短い休憩 ({self.config.short_break_duration // 60}分)"
        
        self._start_timer()
        print(f"\n☕ {break_type} 開始!")
    
    def pause(self):
        """タイマーを一時停止"""
        if self.state in [PomodoroState.FOCUS, PomodoroState.SHORT_BREAK, PomodoroState.LONG_BREAK]:
            self.state = PomodoroState.PAUSED
            self.pause_time = time.time()
            print("\n⏸️  タイマーを一時停止しました")
    
    def resume(self):
        """タイマーを再開"""
        if self.state == PomodoroState.PAUSED and self.pause_time:
            pause_duration = time.time() - self.pause_time
            self.start_time += pause_duration
            self.pause_time = None
            
            # 前の状態に戻る（フォーカス中だったか休憩中だったか）
            if self.elapsed_time < self.current_duration:
                if self.current_session > 0:
                    self.state = PomodoroState.FOCUS if self.current_duration == self.config.focus_duration else (
                        PomodoroState.LONG_BREAK if self.current_duration == self.config.long_break_duration 
                        else PomodoroState.SHORT_BREAK
                    )
                print("\n▶️  タイマーを再開しました")
    
    def stop(self):
        """タイマーを停止"""
        self.running = False
        self.display_running = False
        self.state = PomodoroState.STOPPED
        
        if self.timer_thread and self.timer_thread.is_alive():
            self.timer_thread.join()
        if self.display_thread and self.display_thread.is_alive():
            self.display_thread.join()
        
        VisualEffects.show_cursor()
        print("\n🛑 タイマーを停止しました")
    
    def _start_timer(self):
        """内部タイマー開始処理"""
        self.start_time = time.time()
        self.elapsed_time = 0.0
        self.pause_time = None
        self.running = True
        self.display_running = True
        
        # タイマースレッドを開始
        if self.timer_thread and self.timer_thread.is_alive():
            self.timer_thread.join()
        self.timer_thread = threading.Thread(target=self._timer_loop, daemon=True)
        self.timer_thread.start()
        
        # ディスプレイスレッドを開始
        if self.display_thread and self.display_thread.is_alive():
            self.display_thread.join()
        self.display_thread = threading.Thread(target=self._display_loop, daemon=True)
        self.display_thread.start()
    
    def _timer_loop(self):
        """タイマーメインループ"""
        while self.running and self.state != PomodoroState.STOPPED:
            if self.state != PomodoroState.PAUSED:
                current_time = time.time()
                self.elapsed_time = current_time - self.start_time
                
                # コールバック実行
                if self.on_timer_tick:
                    self.on_timer_tick(self.elapsed_time, self.current_duration)
                
                # タイマー完了チェック
                if self.elapsed_time >= self.current_duration:
                    self._handle_timer_complete()
                    break
            
            time.sleep(0.1)  # 100ms間隔で更新
    
    def _display_loop(self):
        """ディスプレイ更新ループ"""
        VisualEffects.hide_cursor()
        VisualEffects.clear_screen()
        
        frame_count = 0
        while self.display_running and self.state != PomodoroState.STOPPED:
            self._update_display(frame_count)
            frame_count += 1
            time.sleep(0.1)  # 100ms間隔で更新
        
        VisualEffects.show_cursor()
    
    def _update_display(self, frame: int):
        """ディスプレイを更新"""
        if self.state == PomodoroState.PAUSED:
            return
        
        # 進捗計算
        progress = min(self.elapsed_time / self.current_duration, 1.0) if self.current_duration > 0 else 0.0
        remaining_time = max(0, self.current_duration - self.elapsed_time)
        
        # 色を取得
        color = VisualEffects.get_color_for_progress(progress)
        
        # 画面上部に移動
        print("\033[H", end='')
        
        # タイトルと状態
        state_emoji = "🍅" if self.state == PomodoroState.FOCUS else "☕"
        state_text = {
            PomodoroState.FOCUS: "集中時間",
            PomodoroState.SHORT_BREAK: "短い休憩", 
            PomodoroState.LONG_BREAK: "長い休憩"
        }.get(self.state, "")
        
        print(f"{color}{VisualEffects.COLORS['bold']}")
        print(f"{'=' * 60}")
        print(f"{state_emoji} {state_text} - セッション {self.current_session if self.state == PomodoroState.FOCUS else self.current_session}")
        print(f"{'=' * 60}")
        print(f"{VisualEffects.COLORS['reset']}")
        
        # 円形プログレスバー
        circle_lines = VisualEffects.create_circular_progress(progress, 8)
        circle_start_col = 20
        
        # 背景エフェクト（集中時間中のみ）
        if self.state == PomodoroState.FOCUS:
            # パーティクルエフェクト
            if frame % 30 == 0:  # 3秒ごとに更新
                self.particles = VisualEffects.create_particles(60, 3)
            
            # パーティクル表示
            for i, particle_line in enumerate(getattr(self, 'particles', [])):
                print(f"{VisualEffects.COLORS['cyan']}{particle_line}{VisualEffects.COLORS['reset']}")
            
            # 波紋エフェクト
            self.ripple_time += 0.1
            if self.ripple_time > 10:
                self.ripple_time = 0
            
            ripple_radius = (self.ripple_time % 5) * 3
            ripple_lines = VisualEffects.create_ripple_effect(30, 5, ripple_radius, 60, 3)
            for ripple_line in ripple_lines:
                print(f"{VisualEffects.COLORS['blue']}{ripple_line}{VisualEffects.COLORS['reset']}")
        
        print()  # 空行
        
        # 円形プログレスバーを表示
        for i, circle_line in enumerate(circle_lines):
            padding = " " * circle_start_col
            print(f"{padding}{color}{circle_line}{VisualEffects.COLORS['reset']}")
        
        print()  # 空行
        
        # 時間情報
        minutes, seconds = divmod(int(remaining_time), 60)
        time_str = f"{minutes:02d}:{seconds:02d}"
        progress_percent = int(progress * 100)
        
        print(f"{color}{VisualEffects.COLORS['bold']}")
        print(f"{'':>20}残り時間: {time_str}")
        print(f"{'':>20}進捗: {progress_percent}%")
        print(f"{VisualEffects.COLORS['reset']}")
        
        # プログレスバー（水平）
        bar_width = 40
        filled_width = int(bar_width * progress)
        bar = "█" * filled_width + "░" * (bar_width - filled_width)
        print(f"{'':>10}{color}[{bar}]{VisualEffects.COLORS['reset']}")
        
        print()
        print(f"{'':>15}セッション合計: {self.total_sessions}")
        print()
        print("コントロール: [P]一時停止/再開 [S]停止 [Q]終了")
        
        sys.stdout.flush()
    
    def _handle_timer_complete(self):
        """タイマー完了時の処理"""
        if self.state == PomodoroState.FOCUS:
            print("\n🎉 集中セッション完了！")
            if self.on_session_complete:
                self.on_session_complete()
            
            # 次の休憩を自動開始するかユーザーに確認
            response = input("\n休憩を開始しますか？ [Y/n]: ").strip().lower()
            if response in ['', 'y', 'yes']:
                self.start_break()
            else:
                self.stop()
        
        elif self.state in [PomodoroState.SHORT_BREAK, PomodoroState.LONG_BREAK]:
            print("\n🎉 休憩完了！")
            if self.on_break_complete:
                self.on_break_complete()
            
            # 次の集中セッションを自動開始するかユーザーに確認
            response = input("\n次の集中セッションを開始しますか？ [Y/n]: ").strip().lower()
            if response in ['', 'y', 'yes']:
                self.start_focus_session()
            else:
                self.stop()
    
    def get_status(self) -> dict:
        """現在の状態を取得"""
        return {
            'state': self.state.value,
            'current_session': self.current_session,
            'total_sessions': self.total_sessions,
            'elapsed_time': self.elapsed_time,
            'remaining_time': max(0, self.current_duration - self.elapsed_time),
            'progress': min(self.elapsed_time / self.current_duration, 1.0) if self.current_duration > 0 else 0.0
        }


def main():
    """メイン実行関数"""
    print("🍅 ポモドーロタイマー - 視覚的フィードバック強化版")
    print("=" * 50)
    
    # カスタム設定の確認
    print("\nデフォルト設定:")
    print("- 集中時間: 25分")
    print("- 短い休憩: 5分")
    print("- 長い休憩: 15分")
    print("- 長い休憩までのセッション数: 4")
    
    use_custom = input("\nカスタム設定を使用しますか？ [y/N]: ").strip().lower()
    
    config = PomodoroConfig()
    if use_custom in ['y', 'yes']:
        try:
            focus_min = int(input("集中時間 (分): ") or "25")
            short_break_min = int(input("短い休憩 (分): ") or "5")
            long_break_min = int(input("長い休憩 (分): ") or "15")
            sessions_until_long = int(input("長い休憩までのセッション数: ") or "4")
            
            config = PomodoroConfig(
                focus_duration=focus_min * 60,
                short_break_duration=short_break_min * 60,
                long_break_duration=long_break_min * 60,
                sessions_until_long_break=sessions_until_long
            )
        except ValueError:
            print("無効な入力です。デフォルト設定を使用します。")
    
    # タイマー作成
    timer = PomodoroTimer(config)
    
    # コールバック設定
    def on_session_complete():
        print("🔔 集中セッションが完了しました！")
    
    def on_break_complete():
        print("🔔 休憩が完了しました！")
    
    timer.on_session_complete = on_session_complete
    timer.on_break_complete = on_break_complete
    
    try:
        # メインループ
        timer.start_focus_session()
        
        while timer.state != PomodoroState.STOPPED:
            try:
                # ノンブロッキング入力の簡易実装
                import select
                import sys
                
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    key = sys.stdin.read(1).lower()
                    
                    if key == 'p':
                        if timer.state == PomodoroState.PAUSED:
                            timer.resume()
                        else:
                            timer.pause()
                    elif key == 's':
                        timer.stop()
                        break
                    elif key == 'q':
                        timer.stop()
                        break
                
                time.sleep(0.1)
                
            except (KeyboardInterrupt, EOFError):
                print("\n\n終了中...")
                timer.stop()
                break
            except ImportError:
                # selectが使えない環境では通常の入力待ち
                print("\nキーボード操作の説明:")
                print("Ctrl+C で終了")
                try:
                    while timer.state != PomodoroState.STOPPED:
                        time.sleep(1)
                except KeyboardInterrupt:
                    timer.stop()
                    break
    
    finally:
        # 終了処理
        VisualEffects.show_cursor()
        print("\n🍅 ポモドーロタイマーを終了しました")
        
        if timer.total_sessions > 0:
            print(f"今回の成果: {timer.total_sessions} セッション完了")
            print("お疲れさまでした！")


if __name__ == "__main__":
    main()