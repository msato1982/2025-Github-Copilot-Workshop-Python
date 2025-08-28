#!/usr/bin/env python3
"""
メインエントリーポイント - カスタマイズ可能なポモドーロタイマー
Main entry point for the customizable Pomodoro timer
"""

from pomodoro_timer import ConsolePomodoroApp

if __name__ == "__main__":
    app = ConsolePomodoroApp()
    app.run()