import time
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class BadgeType(Enum):
    """バッジの種類"""
    CONSECUTIVE_3_DAYS = "3consecutive_days"
    WEEKLY_10_COMPLETIONS = "weekly_10_completions"
    FIRST_COMPLETION = "first_completion"
    LEVEL_5_REACHED = "level_5_reached"
    LEVEL_10_REACHED = "level_10_reached"
    STREAK_MASTER = "streak_master"  # 7日連続


@dataclass
class Badge:
    """バッジのデータクラス"""
    badge_type: BadgeType
    name: str
    description: str
    earned_date: Optional[str] = None
    
    def is_earned(self) -> bool:
        return self.earned_date is not None


@dataclass 
class PomodoroStats:
    """ポモドーロ統計のデータクラス"""
    total_completions: int = 0
    current_streak: int = 0
    max_streak: int = 0
    weekly_completions: int = 0
    monthly_completions: int = 0
    last_completion_date: Optional[str] = None
    current_level: int = 1
    current_xp: int = 0
    daily_completions: Dict[str, int] = None
    
    def __post_init__(self):
        if self.daily_completions is None:
            self.daily_completions = {}


class GamificationSystem:
    """ゲーミフィケーションシステム"""
    
    XP_PER_COMPLETION = 100
    XP_PER_LEVEL = 500
    SAVE_FILE = "pomodoro_data.json"
    
    def __init__(self):
        self.stats = PomodoroStats()
        self.badges: List[Badge] = []
        self._initialize_badges()
        self.load_data()
    
    def _initialize_badges(self):
        """バッジを初期化"""
        self.badges = [
            Badge(BadgeType.FIRST_COMPLETION, "First Success", "初回ポモドーロ完了"),
            Badge(BadgeType.CONSECUTIVE_3_DAYS, "3 Days Streak", "3日連続完了"),
            Badge(BadgeType.WEEKLY_10_COMPLETIONS, "Weekly Master", "今週10回完了"),
            Badge(BadgeType.LEVEL_5_REACHED, "Level 5", "レベル5到達"),
            Badge(BadgeType.LEVEL_10_REACHED, "Level 10", "レベル10到達"),
            Badge(BadgeType.STREAK_MASTER, "Streak Master", "7日連続完了"),
        ]
    
    def complete_pomodoro(self):
        """ポモドーロ完了時の処理"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        # 基本統計の更新
        self.stats.total_completions += 1
        self.stats.current_xp += self.XP_PER_COMPLETION
        
        # 日別完了数を更新
        if today not in self.stats.daily_completions:
            self.stats.daily_completions[today] = 0
        self.stats.daily_completions[today] += 1
        
        # 連続日数の更新
        self._update_streak(today)
        
        # レベルアップチェック
        level_up = self._check_level_up()
        
        # 週間・月間統計の更新  
        self._update_weekly_monthly_stats(today)
        
        # バッジチェック
        self._check_badges()
        
        # 最終完了日を更新
        self.stats.last_completion_date = today
        
        # データを保存
        self.save_data()
        
        return {
            "xp_gained": self.XP_PER_COMPLETION,
            "new_level": level_up,
            "new_badges": self._get_newly_earned_badges()
        }
    
    def _update_streak(self, today: str):
        """連続日数を更新"""
        if self.stats.last_completion_date is None:
            self.stats.current_streak = 1
        else:
            last_date = datetime.strptime(self.stats.last_completion_date, "%Y-%m-%d")
            current_date = datetime.strptime(today, "%Y-%m-%d")
            day_diff = (current_date - last_date).days
            
            if day_diff == 1:
                # 連続
                self.stats.current_streak += 1
            elif day_diff == 0:
                # 同じ日（既にカウント済み）
                pass
            else:
                # 連続が途切れた
                self.stats.current_streak = 1
        
        # 最大連続記録を更新
        if self.stats.current_streak > self.stats.max_streak:
            self.stats.max_streak = self.stats.current_streak
    
    def _check_level_up(self) -> bool:
        """レベルアップチェック"""
        new_level = (self.stats.current_xp // self.XP_PER_LEVEL) + 1
        if new_level > self.stats.current_level:
            self.stats.current_level = new_level
            return True
        return False
    
    def _update_weekly_monthly_stats(self, today: str):
        """週間・月間統計を更新"""
        current_date = datetime.strptime(today, "%Y-%m-%d")
        
        # 週間統計（過去7日）
        week_start = current_date - timedelta(days=6)
        self.stats.weekly_completions = sum(
            count for date_str, count in self.stats.daily_completions.items()
            if week_start <= datetime.strptime(date_str, "%Y-%m-%d") <= current_date
        )
        
        # 月間統計（今月）
        month_start = current_date.replace(day=1)
        self.stats.monthly_completions = sum(
            count for date_str, count in self.stats.daily_completions.items()
            if month_start <= datetime.strptime(date_str, "%Y-%m-%d") <= current_date
        )
    
    def _check_badges(self):
        """バッジ獲得チェック"""
        for badge in self.badges:
            if not badge.is_earned():
                if self._should_earn_badge(badge.badge_type):
                    badge.earned_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _should_earn_badge(self, badge_type: BadgeType) -> bool:
        """バッジを獲得すべきかチェック"""
        if badge_type == BadgeType.FIRST_COMPLETION:
            return self.stats.total_completions >= 1
        elif badge_type == BadgeType.CONSECUTIVE_3_DAYS:
            return self.stats.current_streak >= 3
        elif badge_type == BadgeType.WEEKLY_10_COMPLETIONS:
            return self.stats.weekly_completions >= 10
        elif badge_type == BadgeType.LEVEL_5_REACHED:
            return self.stats.current_level >= 5
        elif badge_type == BadgeType.LEVEL_10_REACHED:
            return self.stats.current_level >= 10
        elif badge_type == BadgeType.STREAK_MASTER:
            return self.stats.current_streak >= 7
        return False
    
    def _get_newly_earned_badges(self) -> List[Badge]:
        """新しく獲得したバッジを取得"""
        # この実装では簡単のため、すべての獲得済みバッジを返す
        return [badge for badge in self.badges if badge.is_earned()]
    
    def get_progress_to_next_level(self) -> Dict[str, int]:
        """次のレベルまでの進捗を取得"""
        current_level_xp = (self.stats.current_level - 1) * self.XP_PER_LEVEL
        next_level_xp = self.stats.current_level * self.XP_PER_LEVEL
        progress_xp = self.stats.current_xp - current_level_xp
        required_xp = next_level_xp - current_level_xp
        
        return {
            "current_xp": progress_xp,
            "required_xp": required_xp,
            "progress_percentage": int((progress_xp / required_xp) * 100)
        }
    
    def get_weekly_stats(self) -> Dict:
        """週間統計を取得"""
        today = datetime.now()
        week_data = []
        
        for i in range(7):
            date = today - timedelta(days=6-i)
            date_str = date.strftime("%Y-%m-%d")
            completions = self.stats.daily_completions.get(date_str, 0)
            week_data.append({
                "date": date.strftime("%m/%d"),
                "completions": completions
            })
        
        return {
            "daily_data": week_data,
            "total_completions": self.stats.weekly_completions,
            "completion_rate": min(100, (self.stats.weekly_completions / 35) * 100) if self.stats.weekly_completions > 0 else 0
        }
    
    def get_monthly_stats(self) -> Dict:
        """月間統計を取得"""
        today = datetime.now()
        month_start = today.replace(day=1)
        days_in_month = (today.replace(month=today.month + 1, day=1) - timedelta(days=1)).day if today.month < 12 else 31
        
        total_possible = days_in_month * 5  # 1日5ポモドーロを目標と仮定
        
        return {
            "total_completions": self.stats.monthly_completions,
            "days_active": len([d for d in self.stats.daily_completions.keys() 
                              if month_start <= datetime.strptime(d, "%Y-%m-%d") <= today]),
            "completion_rate": min(100, (self.stats.monthly_completions / total_possible) * 100) if total_possible > 0 else 0,
            "average_per_day": self.stats.monthly_completions / today.day if today.day > 0 else 0
        }
    
    def display_stats(self):
        """統計情報を表示"""
        print(f"\n=== ポモドーロ統計 ===")
        print(f"レベル: {self.stats.current_level}")
        print(f"経験値: {self.stats.current_xp}")
        
        progress = self.get_progress_to_next_level()
        print(f"次のレベルまで: {progress['current_xp']}/{progress['required_xp']} XP ({progress['progress_percentage']}%)")
        
        print(f"総完了数: {self.stats.total_completions}")
        print(f"現在の連続記録: {self.stats.current_streak}日")
        print(f"最高連続記録: {self.stats.max_streak}日")
        print(f"今週の完了数: {self.stats.weekly_completions}")
        print(f"今月の完了数: {self.stats.monthly_completions}")
        
        # 獲得済みバッジを表示
        earned_badges = [b for b in self.badges if b.is_earned()]
        if earned_badges:
            print(f"\n=== 獲得バッジ ({len(earned_badges)}/{len(self.badges)}) ===")
            for badge in earned_badges:
                print(f"🏆 {badge.name}: {badge.description}")
    
    def save_data(self):
        """データを保存"""
        # バッジデータを辞書形式に変換
        badges_data = []
        for badge in self.badges:
            badge_dict = {
                "badge_type": badge.badge_type.value,  # Enumの値を使用
                "name": badge.name,
                "description": badge.description,
                "earned_date": badge.earned_date
            }
            badges_data.append(badge_dict)
        
        data = {
            "stats": asdict(self.stats),
            "badges": badges_data
        }
        
        try:
            with open(self.SAVE_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"データ保存エラー: {e}")
    
    def load_data(self):
        """データを読み込み"""
        if not os.path.exists(self.SAVE_FILE):
            return
        
        try:
            with open(self.SAVE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 統計データを復元
            stats_data = data.get("stats", {})
            self.stats = PomodoroStats(**stats_data)
            
            # バッジデータを復元
            badges_data = data.get("badges", [])
            for i, badge_data in enumerate(badges_data):
                if i < len(self.badges):
                    self.badges[i].earned_date = badge_data.get("earned_date")
                    
        except Exception as e:
            print(f"データ読み込みエラー: {e}")
            # エラーの場合は初期状態を維持
