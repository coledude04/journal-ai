import pytest
from datetime import date
from db.streaks_repo import (
    date_from_str,
    today_str,
    update_streak,
)


class TestStreakLogic:
    """Test streak calculation logic"""
    
    def test_date_from_str_parsing(self):
        """Test converting ISO date strings to date objects"""
        d = date_from_str("2025-12-19")
        assert d == date(2025, 12, 19)
    
    def test_today_str_timezone(self):
        """Test that today_str returns correct date in different timezones"""
        # This test is timezone-dependent, so we verify format only
        result = today_str("America/Chicago")
        assert len(result) == 10  # YYYY-MM-DD format
        assert result.count("-") == 2
    
    # ============================================
    # FIRST EVER LOG TESTS
    # ============================================
    
    def test_first_ever_log(self):
        """User creates their first log - streak should be 1"""
        user_data = {}
        log_date = date(2025, 12, 19)
        
        result = update_streak(None, "", user_data, log_date)
        
        assert result["current_streak"] == 1
        assert result["longest_streak"] == 1
        assert result["last_completed_date"] == "2025-12-19"
    
    # ============================================
    # SAME DAY LOG TESTS
    # ============================================
    
    def test_same_day_duplicate_log(self):
        """User tries to log same day twice - should not increment"""
        user_data = {
            "current_streak": 5,
            "longest_streak": 10,
            "last_completed_date": "2025-12-19"
        }
        log_date = date(2025, 12, 19)  # Same day
        
        result = update_streak(None, "", user_data, log_date)
        
        # Should return without changes
        assert result["current_streak"] == 5
        assert result["longest_streak"] == 10
        assert result["last_completed_date"] == "2025-12-19"
    
    # ============================================
    # CONSECUTIVE DAY TESTS (7pm-noon window)
    # ============================================
    
    def test_consecutive_day_increments_streak(self):
        """User logs day after their last log - streak increments"""
        user_data = {
            "current_streak": 5,
            "longest_streak": 10,
            "last_completed_date": "2025-12-18"
        }
        log_date = date(2025, 12, 19)  # Next day
        
        result = update_streak(None, "", user_data, log_date)
        
        assert result["current_streak"] == 6
        assert result["longest_streak"] == 10
        assert result["last_completed_date"] == "2025-12-19"
    
    def test_consecutive_day_updates_longest_streak(self):
        """When streak reaches new high, longest_streak updates"""
        user_data = {
            "current_streak": 9,
            "longest_streak": 9,
            "last_completed_date": "2025-12-18"
        }
        log_date = date(2025, 12, 19)  # Next day
        
        result = update_streak(None, "", user_data, log_date)
        
        assert result["current_streak"] == 10
        assert result["longest_streak"] == 10  # Updated!
        assert result["last_completed_date"] == "2025-12-19"
    
    # ============================================
    # MISSED DAYS TESTS
    # ============================================
    
    def test_missed_one_day_resets_streak(self):
        """User skips a day - streak resets to 1"""
        user_data = {
            "current_streak": 7,
            "longest_streak": 15,
            "last_completed_date": "2025-12-17"
        }
        log_date = date(2025, 12, 19)  # Skipped 12-18
        
        result = update_streak(None, "", user_data, log_date)
        
        assert result["current_streak"] == 1
        assert result["longest_streak"] == 15  # Unchanged
        assert result["last_completed_date"] == "2025-12-19"
    
    def test_missed_multiple_days_resets_streak(self):
        """User skips multiple days - streak resets to 1"""
        user_data = {
            "current_streak": 20,
            "longest_streak": 20,
            "last_completed_date": "2025-12-10"
        }
        log_date = date(2025, 12, 19)  # Skipped 9 days
        
        result = update_streak(None, "", user_data, log_date)
        
        assert result["current_streak"] == 1
        assert result["longest_streak"] == 20
        assert result["last_completed_date"] == "2025-12-19"
    
    # ============================================
    # BACKDATED LOG TESTS (7pm-noon window)
    # ============================================
    
    def test_backdated_log_from_yesterday(self):
        """User creates log for yesterday (within 7pm-noon window)"""
        user_data = {
            "current_streak": 3,
            "longest_streak": 5,
            "last_completed_date": "2025-12-17"
        }
        log_date = date(2025, 12, 18)  # Yesterday from "today" (12-19)
        
        result = update_streak(None, "", user_data, log_date)
        
        # Should increment streak (from 12-17 to 12-18 is consecutive)
        assert result["current_streak"] == 4
        assert result["longest_streak"] == 5
        assert result["last_completed_date"] == "2025-12-18"
    
    def test_multiple_backdated_logs_same_date(self):
        """User creates multiple logs for same date - only first counts"""
        # First attempt for 2025-12-18
        user_data = {
            "current_streak": 3,
            "longest_streak": 5,
            "last_completed_date": "2025-12-17"
        }
        log_date = date(2025, 12, 18)
        result1 = update_streak(None, "", user_data, log_date)
        assert result1["current_streak"] == 4
        assert result1["last_completed_date"] == "2025-12-18"
        
        # Second attempt for same date
        log_date2 = date(2025, 12, 18)
        result2 = update_streak(None, "", result1, log_date2)
        # Should return unchanged (same day check)
        assert result2["current_streak"] == 4
        assert result2["last_completed_date"] == "2025-12-18"
    
    def test_backdated_gap_resets_streak(self):
        """User tries to log a gap in past - streak resets"""
        user_data = {
            "current_streak": 5,
            "longest_streak": 10,
            "last_completed_date": "2025-12-17"
        }
        log_date = date(2025, 12, 15)  # Gap: 12-15 before 12-17
        
        result = update_streak(None, "", user_data, log_date)
        
        # Should reset (log_date is before last_completed_date)
        assert result["current_streak"] == 1
        assert result["longest_streak"] == 10
        assert result["last_completed_date"] == "2025-12-15"
    
    # ============================================
    # EDGE CASES
    # ============================================
    
    def test_first_log_backdated(self):
        """First user log is backdated"""
        user_data = {}
        log_date = date(2025, 12, 15)  # Several days ago
        
        result = update_streak(None, "", user_data, log_date)
        
        assert result["current_streak"] == 1
        assert result["longest_streak"] == 1
        assert result["last_completed_date"] == "2025-12-15"
    
    def test_zero_streak_becomes_one(self):
        """User with 0 streak logs - becomes 1"""
        user_data = {
            "current_streak": 0,
            "longest_streak": 5,
            "last_completed_date": "2025-12-10"  # Gap
        }
        log_date = date(2025, 12, 19)
        
        result = update_streak(None, "", user_data, log_date)
        
        assert result["current_streak"] == 1
        assert result["longest_streak"] == 5
    
    # ============================================
    # REALISTIC 7PM-NOON WINDOW SCENARIO
    # ============================================
    
    def test_realistic_7pm_noon_window_scenario(self):
        """
        Realistic scenario:
        - User in America/Chicago timezone
        - Day 1 (12-18): Logs at 11pm → streak = 1
        - Day 2 (12-19): Logs at 10am (within 7pm-noon window) → streak = 2
        - Day 3 (12-20): Logs at 8am (within 7pm-noon window) → streak = 3
        - Day 4 (12-21): Misses window, doesn't log → streak breaks
        - Day 5 (12-22): Logs at 9am → streak = 1 (reset)
        """
        # Day 1
        user_data = {}
        result = update_streak(None, "", user_data, date(2025, 12, 18))
        assert result["current_streak"] == 1
        
        # Day 2
        result = update_streak(None, "", result, date(2025, 12, 19))
        assert result["current_streak"] == 2
        
        # Day 3
        result = update_streak(None, "", result, date(2025, 12, 20))
        assert result["current_streak"] == 3
        
        # Day 4 - missed (no log creation call)
        
        # Day 5 - should reset
        result = update_streak(None, "", result, date(2025, 12, 22))
        assert result["current_streak"] == 1
        assert result["longest_streak"] == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
