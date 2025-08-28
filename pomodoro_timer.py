#!/usr/bin/env python3
"""
ポモドーロタイマー - カスタマイズ可能な設定付き
Customizable Pomodoro Timer with flexible settings
"""

import time
import threading
import json
import os
from enum import Enum
from dataclasses import dataclass, asdict
from typing import Optional, Callable
import sys


class TimerState(Enum):
    """タイマーの状態"""
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    BREAK = "break"


class Theme(Enum):
    """テーマ設定"""
    LIGHT = "light"
    DARK = "dark"
    FOCUS = "focus"


@dataclass
class PomodoroSettings:
    """ポモドーロタイマーの設定"""
    work_duration: int = 25  # 作業時間（分）
    break_duration: int = 5  # 休憩時間（分）
    theme: Theme = Theme.LIGHT
    sound_start: bool = True
    sound_end: bool = True
    sound_tick: bool = False
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PomodoroSettings':
        """辞書からPomodoroSettingsを作成"""
        if 'theme' in data:
            data['theme'] = Theme(data['theme'])
        return cls(**data)
    
    def to_dict(self) -> dict:
        """辞書形式に変換"""
        result = asdict(self)
        result['theme'] = self.theme.value
        return result


class PomodoroTimer:
    """カスタマイズ可能なポモドーロタイマー"""
    
    # 利用可能な時間設定
    WORK_TIME_OPTIONS = [15, 25, 35, 45]  # 分
    BREAK_TIME_OPTIONS = [5, 10, 15]      # 分
    
    def __init__(self):
        self.settings = PomodoroSettings()
        self.state = TimerState.STOPPED
        self.remaining_seconds = 0
        self.total_seconds = 0
        self.is_work_session = True
        self.completed_pomodoros = 0
        
        # コールバック関数
        self.on_timer_start: Optional[Callable] = None
        self.on_timer_end: Optional[Callable] = None
        self.on_timer_tick: Optional[Callable] = None
        self.on_break_start: Optional[Callable] = None
        
        # タイマースレッド
        self._timer_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
        # 設定ファイルのパス
        self.settings_file = os.path.expanduser("~/.pomodoro_settings.json")
        
        # 設定を読み込み
        self.load_settings()
    
    def load_settings(self):
        """設定ファイルから設定を読み込み"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.settings = PomodoroSettings.from_dict(data)
        except Exception as e:
            print(f"設定の読み込みに失敗: {e}")
    
    def save_settings(self):
        """設定をファイルに保存"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings.to_dict(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"設定の保存に失敗: {e}")
    
    def set_work_duration(self, minutes: int):
        """作業時間を設定"""
        if minutes in self.WORK_TIME_OPTIONS:
            self.settings.work_duration = minutes
            self.save_settings()
            return True
        return False
    
    def set_break_duration(self, minutes: int):
        """休憩時間を設定"""
        if minutes in self.BREAK_TIME_OPTIONS:
            self.settings.break_duration = minutes
            self.save_settings()
            return True
        return False
    
    def set_theme(self, theme: Theme):
        """テーマを設定"""
        self.settings.theme = theme
        self.save_settings()
    
    def set_sound_settings(self, start: bool = None, end: bool = None, tick: bool = None):
        """サウンド設定"""
        if start is not None:
            self.settings.sound_start = start
        if end is not None:
            self.settings.sound_end = end
        if tick is not None:
            self.settings.sound_tick = tick
        self.save_settings()
    
    def start_work_session(self):
        """作業セッション開始"""
        if self.state == TimerState.RUNNING:
            return False
        
        self.is_work_session = True
        self.total_seconds = self.settings.work_duration * 60
        self.remaining_seconds = self.total_seconds
        self.state = TimerState.RUNNING
        
        if self.settings.sound_start and self.on_timer_start:
            self.on_timer_start()
        
        self._start_timer_thread()
        return True
    
    def start_break_session(self):
        """休憩セッション開始"""
        if self.state == TimerState.RUNNING:
            return False
        
        self.is_work_session = False
        self.total_seconds = self.settings.break_duration * 60
        self.remaining_seconds = self.total_seconds
        self.state = TimerState.BREAK
        
        if self.on_break_start:
            self.on_break_start()
        
        self._start_timer_thread()
        return True
    
    def pause(self):
        """タイマー一時停止"""
        if self.state == TimerState.RUNNING or self.state == TimerState.BREAK:
            self.state = TimerState.PAUSED
            return True
        return False
    
    def resume(self):
        """タイマー再開"""
        if self.state == TimerState.PAUSED:
            self.state = TimerState.RUNNING if self.is_work_session else TimerState.BREAK
            return True
        return False
    
    def stop(self):
        """タイマー停止"""
        self.state = TimerState.STOPPED
        self._stop_event.set()
        if self._timer_thread and self._timer_thread.is_alive():
            self._timer_thread.join()
        self.remaining_seconds = 0
    
    def _start_timer_thread(self):
        """タイマースレッド開始"""
        self._stop_event.clear()
        if self._timer_thread and self._timer_thread.is_alive():
            self._timer_thread.join()
        
        self._timer_thread = threading.Thread(target=self._run_timer)
        self._timer_thread.daemon = True
        self._timer_thread.start()
    
    def _run_timer(self):
        """タイマー実行ループ"""
        while (self.remaining_seconds > 0 and 
               not self._stop_event.is_set() and 
               self.state != TimerState.STOPPED):
            
            if self.state == TimerState.PAUSED:
                time.sleep(0.1)
                continue
            
            if self.settings.sound_tick and self.on_timer_tick:
                self.on_timer_tick()
            
            time.sleep(1)
            self.remaining_seconds -= 1
        
        # タイマー終了処理
        if self.remaining_seconds <= 0 and not self._stop_event.is_set():
            if self.is_work_session:
                self.completed_pomodoros += 1
            
            self.state = TimerState.STOPPED
            
            if self.settings.sound_end and self.on_timer_end:
                self.on_timer_end()
    
    def get_remaining_time(self) -> tuple[int, int]:
        """残り時間を分:秒で取得"""
        minutes = self.remaining_seconds // 60
        seconds = self.remaining_seconds % 60
        return minutes, seconds
    
    def get_progress(self) -> float:
        """進捗率を0.0-1.0で取得"""
        if self.total_seconds == 0:
            return 0.0
        return (self.total_seconds - self.remaining_seconds) / self.total_seconds
    
    def get_theme_colors(self) -> dict:
        """現在のテーマの色設定を取得"""
        themes = {
            Theme.LIGHT: {
                'bg': '#FFFFFF',
                'text': '#000000',
                'accent': '#007AFF',
                'secondary': '#F0F0F0'
            },
            Theme.DARK: {
                'bg': '#1C1C1E',
                'text': '#FFFFFF',
                'accent': '#0A84FF',
                'secondary': '#2C2C2E'
            },
            Theme.FOCUS: {
                'bg': '#F5F5F5',
                'text': '#333333',
                'accent': '#FF6B35',
                'secondary': '#E0E0E0'
            }
        }
        return themes.get(self.settings.theme, themes[Theme.LIGHT])


def play_sound(sound_type: str):
    """サウンド再生（プレースホルダー実装）"""
    sound_messages = {
        'start': '🔔 タイマー開始！',
        'end': '⏰ 時間終了！',
        'tick': '⏱️'
    }
    if sound_type in sound_messages:
        print(sound_messages[sound_type])


class ConsolePomodoroApp:
    """コンソール版ポモドーロタイマーアプリ"""
    
    def __init__(self):
        self.timer = PomodoroTimer()
        self.running = True
        
        # コールバック設定
        self.timer.on_timer_start = lambda: play_sound('start')
        self.timer.on_timer_end = lambda: play_sound('end')
        self.timer.on_timer_tick = lambda: play_sound('tick')
        self.timer.on_break_start = lambda: play_sound('start')
    
    def display_menu(self):
        """メニュー表示"""
        colors = self.timer.get_theme_colors()
        theme_name = self.timer.settings.theme.value.upper()
        
        print(f"\n🍅 ポモドーロタイマー ({theme_name}テーマ) 🍅")
        print("=" * 40)
        print("1. 作業セッション開始")
        print("2. 休憩セッション開始") 
        print("3. 一時停止/再開")
        print("4. 停止")
        print("5. 設定")
        print("6. 統計")
        print("0. 終了")
        
        if self.timer.state != TimerState.STOPPED:
            minutes, seconds = self.timer.get_remaining_time()
            state_text = {
                TimerState.RUNNING: "作業中",
                TimerState.BREAK: "休憩中", 
                TimerState.PAUSED: "一時停止"
            }.get(self.timer.state, "")
            
            progress = self.timer.get_progress()
            progress_bar = "█" * int(progress * 20) + "░" * (20 - int(progress * 20))
            
            print(f"\n状態: {state_text}")
            print(f"残り時間: {minutes:02d}:{seconds:02d}")
            print(f"進捗: [{progress_bar}] {progress:.0%}")
    
    def display_settings_menu(self):
        """設定メニュー表示"""
        s = self.timer.settings
        print(f"\n⚙️  設定")
        print("=" * 30)
        print(f"1. 作業時間: {s.work_duration}分")
        print(f"2. 休憩時間: {s.break_duration}分")
        print(f"3. テーマ: {s.theme.value}")
        print(f"4. 開始音: {'ON' if s.sound_start else 'OFF'}")
        print(f"5. 終了音: {'ON' if s.sound_end else 'OFF'}")
        print(f"6. ティック音: {'ON' if s.sound_tick else 'OFF'}")
        print("0. 戻る")
    
    def handle_settings(self):
        """設定処理"""
        while True:
            self.display_settings_menu()
            choice = input("\n選択: ").strip()
            
            if choice == '0':
                break
            elif choice == '1':
                print(f"作業時間を選択: {self.timer.WORK_TIME_OPTIONS}")
                try:
                    minutes = int(input("分数を入力: "))
                    if self.timer.set_work_duration(minutes):
                        print(f"作業時間を{minutes}分に設定しました")
                    else:
                        print("無効な時間です")
                except ValueError:
                    print("数値を入力してください")
            
            elif choice == '2':
                print(f"休憩時間を選択: {self.timer.BREAK_TIME_OPTIONS}")
                try:
                    minutes = int(input("分数を入力: "))
                    if self.timer.set_break_duration(minutes):
                        print(f"休憩時間を{minutes}分に設定しました")
                    else:
                        print("無効な時間です")
                except ValueError:
                    print("数値を入力してください")
            
            elif choice == '3':
                print("テーマを選択:")
                print("1. Light  2. Dark  3. Focus")
                theme_choice = input("選択: ").strip()
                theme_map = {'1': Theme.LIGHT, '2': Theme.DARK, '3': Theme.FOCUS}
                if theme_choice in theme_map:
                    self.timer.set_theme(theme_map[theme_choice])
                    print(f"{theme_map[theme_choice].value}テーマに設定しました")
            
            elif choice in ['4', '5', '6']:
                current = [
                    self.timer.settings.sound_start,
                    self.timer.settings.sound_end, 
                    self.timer.settings.sound_tick
                ][int(choice) - 4]
                
                new_value = not current
                if choice == '4':
                    self.timer.set_sound_settings(start=new_value)
                elif choice == '5':
                    self.timer.set_sound_settings(end=new_value)
                elif choice == '6':
                    self.timer.set_sound_settings(tick=new_value)
                
                print(f"設定を{'ON' if new_value else 'OFF'}にしました")
    
    def run(self):
        """アプリケーション実行"""
        print("🍅 カスタマイズ可能なポモドーロタイマーへようこそ！")
        
        try:
            while self.running:
                self.display_menu()
                choice = input("\n選択してください: ").strip()
                
                if choice == '0':
                    self.running = False
                    self.timer.stop()
                    print("タイマーを終了します。お疲れ様でした！")
                
                elif choice == '1':
                    if self.timer.start_work_session():
                        print("作業セッションを開始しました！")
                    else:
                        print("タイマーが既に動作中です")
                
                elif choice == '2':
                    if self.timer.start_break_session():
                        print("休憩セッションを開始しました！")
                    else:
                        print("タイマーが既に動作中です")
                
                elif choice == '3':
                    if self.timer.state == TimerState.PAUSED:
                        if self.timer.resume():
                            print("タイマーを再開しました")
                    elif self.timer.state in [TimerState.RUNNING, TimerState.BREAK]:
                        if self.timer.pause():
                            print("タイマーを一時停止しました")
                    else:
                        print("一時停止できません")
                
                elif choice == '4':
                    self.timer.stop()
                    print("タイマーを停止しました")
                
                elif choice == '5':
                    self.handle_settings()
                
                elif choice == '6':
                    print(f"\n📊 統計")
                    print(f"完了したポモドーロ: {self.timer.completed_pomodoros}")
                    print(f"現在の設定:")
                    print(f"  作業時間: {self.timer.settings.work_duration}分")
                    print(f"  休憩時間: {self.timer.settings.break_duration}分")
                    print(f"  テーマ: {self.timer.settings.theme.value}")
                
                else:
                    print("無効な選択です")
                
                # 短い待機でUIをスムーズにする
                time.sleep(0.1)
        
        except KeyboardInterrupt:
            print("\n\nタイマーを終了します...")
            self.timer.stop()


if __name__ == "__main__":
    app = ConsolePomodoroApp()
    app.run()