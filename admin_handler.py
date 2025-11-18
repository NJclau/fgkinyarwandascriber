import streamlit as st
from datetime import datetime, timedelta
import json
import os


class AdminHandler:
    """Manage user access and usage limits"""
    
    def __init__(self):
        self.admin_emails = st.secrets.get("ADMIN_EMAILS", [])
        self.max_file_size_mb = st.secrets.get("MAX_FILE_SIZE_MB", 50)  # ~30 min audio
        self.max_duration_minutes = st.secrets.get("MAX_DURATION_MINUTES", 30)
        self.usage_file = "usage_logs.json"
    
    def is_admin(self, email: str) -> bool:
        """Check if user is admin"""
        return email in self.admin_emails
    
    def validate_file_upload(self, file) -> tuple[bool, str]:
        """Validate file size and duration limits"""
        # Check file size
        file_size_mb = file.size / (1024 * 1024)
        if file_size_mb > self.max_file_size_mb:
            return False, f"❌ File too large ({file_size_mb:.1f}MB). Maximum: {self.max_file_size_mb}MB (~{self.max_duration_minutes} minutes)"
        
        return True, f"✓ File valid ({file_size_mb:.1f}MB)"
    
    def log_usage(self, user_email: str, filename: str, file_size_mb: float, duration_sec: float):
        """Log transcription usage"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user": user_email,
            "filename": filename,
            "size_mb": round(file_size_mb, 2),
            "duration_sec": round(duration_sec, 2),
            "duration_min": round(duration_sec / 60, 2)
        }
        
        # Append to logs
        logs = self.load_logs()
        logs.append(log_entry)
        
        with open(self.usage_file, "w") as f:
            json.dump(logs, f, indent=2)
    
    def load_logs(self) -> list:
        """Load usage logs"""
        if os.path.exists(self.usage_file):
            with open(self.usage_file, "r") as f:
                return json.load(f)
        return []
    
    def get_user_stats(self, user_email: str) -> dict:
        """Get user usage statistics"""
        logs = self.load_logs()
        user_logs = [log for log in logs if log["user"] == user_email]
        
        total_files = len(user_logs)
        total_duration = sum(log["duration_min"] for log in user_logs)
        
        return {
            "total_files": total_files,
            "total_duration_min": round(total_duration, 2),
            "last_upload": user_logs[-1]["timestamp"] if user_logs else None
        }
    
    def check_rate_limit(self, user_email: str, limit_per_day: int = 10) -> tuple[bool, str]:
        """Check if user exceeded daily upload limit"""
        logs = self.load_logs()
        today = datetime.now().date()
        
        today_logs = [
            log for log in logs 
            if log["user"] == user_email 
            and datetime.fromisoformat(log["timestamp"]).date() == today
        ]
        
        if len(today_logs) >= limit_per_day:
            return False, f"❌ Daily limit reached ({limit_per_day} files). Try tomorrow."
        
        return True, f"✓ {limit_per_day - len(today_logs)} uploads remaining today"


def render_admin_dashboard():
    """Admin dashboard UI"""
    st.title("🔐 Admin Dashboard")
    
    admin = AdminHandler()
    logs = admin.load_logs()
    
    if not logs:
        st.info("No usage logs yet")
        return
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Transcriptions", len(logs))
    with col2:
        total_duration = sum(log["duration_min"] for log in logs)
        st.metric("Total Duration (min)", f"{total_duration:.1f}")
    with col3:
        unique_users = len(set(log["user"] for log in logs))
        st.metric("Unique Users", unique_users)
    
    # User breakdown
    st.subheader("Usage by User")
    user_stats = {}
    for log in logs:
        user = log["user"]
        if user not in user_stats:
            user_stats[user] = {"files": 0, "duration": 0}
        user_stats[user]["files"] += 1
        user_stats[user]["duration"] += log["duration_min"]
    
    for user, stats in user_stats.items():
        with st.expander(f"📧 {user}"):
            col1, col2 = st.columns(2)
            col1.metric("Files Processed", stats["files"])
            col2.metric("Total Duration (min)", f"{stats['duration']:.1f}")
    
    # Recent activity
    st.subheader("Recent Activity")
    recent_logs = sorted(logs, key=lambda x: x["timestamp"], reverse=True)[:10]
    
    for log in recent_logs:
        st.text(f"{log['timestamp']} | {log['user']} | {log['filename']} | {log['duration_min']:.1f} min")
